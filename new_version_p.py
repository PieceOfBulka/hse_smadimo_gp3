import sqlite3
from logger_master import get_logger
import json 
import time
import random
from datetime import datetime
import requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import fake_useragent
from bs4 import BeautifulSoup
import os
from concurrent.futures import ThreadPoolExecutor
from threading import Semaphore

llm_semaphore = Semaphore(2)

log = get_logger('DB_COLLECT_MORE_DATA')


def scroll_down(driver, steps=5, delay=0.5):
    for _ in range(steps):
        driver.execute_script("window.scrollBy(0, window.innerHeight * 0.7);")
        time.sleep(delay)



def create_driver():
    new_options = webdriver.ChromeOptions()
    user_agent = fake_useragent.UserAgent()

    new_options.add_argument(f'user-agent={user_agent.random}')
    new_options.add_argument('--disable-blink-features=AutomationControlled')
    new_options.add_experimental_option('excludeSwitches', ['enable-automation'])

    driver = webdriver.Chrome(options=new_options)


    if driver:
        log.info(f'Драйвер для работы с selenium создан: {driver}')
        return driver
    else:
        log.critical(f'Драйвер для работы c selenium НЕ создан: {driver}')

def create_tmp_table(cursor, conn):
    query = """CREATE TABLE IF NOT EXISTS processed_vacancies(
        hh_vac_id TEXT PRIMARY KEY,
        processed_at TIMESTAMP
    );
    """

    cursor.execute(query)
    conn.commit()

    log.info('--- Была создана временная таблица ---')



def select_unprocessed(cursor):
    query = """SELECT vacancies.id, vacancies.hh_vac_id, vacancies.hh_vac_link
        FROM vacancies
        LEFT JOIN processed_vacancies p ON vacancies.hh_vac_id = p.hh_vac_id
        WHERE p.hh_vac_id IS NULL AND (vacancies.employment IS NULL OR vacancies.schedule IS NULL OR vacancies.area IS NULL)
    """

    cursor.execute(query)

    log.info('--- Найдены незаполненые значения ---')
    return cursor.fetchall()



def update_vacancy(cursor, conn, vac_id, data: dict):
    # про именнованное присвоение в запросе: https://docs.python.org/3/library/sqlite3.html#sqlite3-placeholders:~:text=ignored.%20Here%E2%80%99s%20an%20example%20of%20both%20styles%3A

    data['hh_vac_id'] = vac_id

    cursor.execute("""UPDATE vacancies SET
            employment=:employment, schedule=:schedule,
            salary_from=:salary_from, salary_to=:salary_to,
            currency=:currency, area=:area,
            skills=:skills, published_at=:published_at
        WHERE hh_vac_id=:hh_vac_id
    """, 
    data)

    log.info(f'--- Обновили данные по vac_id={vac_id} ---')
    conn.commit()


def mark_as_processed(cursor, conn, vac_id):
    query = """INSERT OR IGNORE INTO processed_vacancies (hh_vac_id, processed_at)
               VALUES (?, datetime('now'))
    """

    cursor.execute(query, (vac_id,))

    conn.commit()
    log.info(f'--- Внесены данные во временную таблицу по vac_id={vac_id} ---')


def get_vacancy_from_web(url):
    try:
        # driver.get(url)
        # WebDriverWait(driver, 3).until(
        #     EC.presence_of_element_located((By.TAG_NAME, 'body'))
        # )
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        
        if response.status_code != 200:
            log.warning(f'Плохой статус {response.status_code} для {url}')
            return
        
        html = response.text


        
        

        log.info(f'Успешный переход по ссылке: {url}')

        # time.sleep(0.5)

        soup = BeautifulSoup(html, 'html.parser')
        container_main = soup.find('div', class_='HH-MainContent')

        if container_main:
            return str(container_main)    
    except Exception as ex:
        log.error(f'Возникал ошибка в ходе перехода по ссылке: {url}: ОШИБКА {ex}')

def model_work(html):
    llm_semaphore = Semaphore(2)

    API_KEY = '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'
    MODEL = 'minimax/minimax-m2.5:free'

    PROMPT_TEMPLATE = """Ты парсер вакансий. Извлеки информацию из HTML вакансии и верни ТОЛЬКО валидный JSON без пояснений.

    HTML:
    {html}

    Верни JSON строго в формате:
    {{
    "employment": "полная/частичная/проектная/волонтёрство/стажировка или null",
    "schedule": "полный день/сменный/гибкий/удалённая работа/вахтовый метод или null",
    "salary_from": число или null,
    "salary_to": число или null,
    "currency": "RUR/USD/EUR или null",
    "area": "город или null",
    "skills": ["навык1", "навык2"] или []
    }}
    """

    # try:
    #     # ссылка на документацию, уважаемая коммисия это не GPT: https://openrouter.ai/docs/client-sdks/python/overview        
    #     with OpenRouter(
    #         api_key=API_KEY
    #     ) as client:
    #         response = client.chat.send(
    #             model=MODEL,
    #             messages=[
    #                 {
    #                 "role": "user",
    #                 "content": PROMPT_TEMPLATE.format(html=html[:8000])
    #                 }
    #             ]
    #         )
        
    #     model_answer = response.choices[0].message.content
    #     data_to_upload = json.loads(model_answer)

    #     # перестрахуемся, если модель передаст на выход skills не как json, а как список
    #     if isinstance(data_to_upload.get('skills'), list):
    #         data_to_upload['skills'] = json.dumps(data_to_upload['skills'], ensure_ascii=False)

    #     return data_to_upload
    # except Exception as ex:
    #     log.error(f'Ошибка LLM парсинга: {ex}')
    #     return
    try:
        response = requests.post(
            'https://openrouter.ai/api/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                'model': MODEL,
                'messages': [
                    {
                        'role': 'user',
                        'content': PROMPT_TEMPLATE.format(html=html[:8000])
                    }
                ],
                'temperature': 0
            },
            timeout=30
        )

        if 'choices' not in response:
            log.error(f'ОШИБКА отвеа LLM: {response}')
            return None

        model_answer = response.json()['choices'][0]['message']['content']
        model_answer = model_answer.strip().removeprefix('```json').removeprefix('```').removesuffix('```').strip()

        data_to_upload = json.loads(model_answer)

        if isinstance(data_to_upload.get('skills'), list):
            data_to_upload['skills'] = json.dumps(data_to_upload['skills'], ensure_ascii=False)

        return data_to_upload
    except Exception as ex:
        log.error(f'Ошибка LLM парсинга: {ex}')
        return None
    
def main_def_to_uload(driver, cursor, conn):
    create_tmp_table(cursor, conn)

    vacancies = select_unprocessed(cursor)
    total = len(vacancies)
    log.info(f'Найдено необработанных вакансий: {total}')

    for i, (row_id, vac_id, vac_link) in enumerate(vacancies):
        log.info(f'[{i+1}/{total}] Обработка: {vac_id}')

        html = get_vacancy_from_web(driver, vac_link)
        
        if not html:
            log.warning(f'Пустой HTML для {vac_id} пропупскаем')

            mark_as_processed(cursor, conn, vac_id)
            continue

            
        model_work(html)

        if not data:

            log.warning(f'LLM упал с ошибкой для {vac_id} - пропускаем')
            continue

        data['published_at'] = datetime.now().isoformat()
        update_vacancy(cursor, conn, vac_id, data)
        mark_as_processed(cursor, conn, vac_id)

        log.info(f'Вакансия {vac_id} обновdлена')
        time.sleep(0.05)
   

def process_vacancy(vac, db_path):
    row_id, vac_id, vac_link = vac


    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        log.info(f'Обработка: {vac_id}')



        html = get_vacancy_from_web(vac_link)

        if not html:
            log.warning(f'Пустой HTML для {vac_id} пропускаем')
            mark_as_processed(cursor, conn, vac_id)
            return

        data = model_work(html)

        if not data:
            log.warning(f'LLM упал для {vac_id}')
            return

        data['published_at'] = datetime.now().isoformat()

        update_vacancy(cursor, conn, vac_id, data)
        mark_as_processed(cursor, conn, vac_id)

        log.info(f'Вакансия {vac_id} обновлена')

    except Exception as e:
        log.error(f'Ошибка обработки {vac_id}: {e}')

    finally:
        # driver.quit()
        conn.close()




def main_def_to_uload(db_path):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        create_tmp_table(cursor, conn)
        vacancies = select_unprocessed(cursor)

    total = len(vacancies)
    log.info(f'Найдено необработанных вакансий: {total}')

    MAX_WORKERS = 2

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        executor.map(lambda vac: process_vacancy(vac, db_path), vacancies)


if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.abspath(__file__))
    driver = create_driver()

    try:
        with sqlite3.connect(os.path.join(base_dir, 'GP_DB.db')) as conn:
            log.info('Соединение с БД установлено')

            cursor = conn.cursor()
            main_def_to_uload(driver, cursor, conn)

            log.info('Соединение с БД закрыто')
    finally:
        driver.quit()
        log.info('Драйвер успешно закрыт')
