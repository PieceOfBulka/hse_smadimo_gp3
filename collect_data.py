import os
import json
import sqlite3
import pandas as pd
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from logger_master import get_logger

log = get_logger('DB_COLLECT_MORE_DATA_V2')

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



def model_work(html):
    API_KEY = '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'
    MODEL = 'openai/gpt-oss-120b:free'

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


def get_vacancy_from_web(url):
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        
        if response.status_code != 200:
            log.warning(f'Плохой статус {response.status_code} для {url}')
            return
        
        html = response.text
        log.info(f'Успешный переход по ссылке: {url}')

        soup = BeautifulSoup(html, 'html.parser')
        container_main = soup.find('div', class_='HH-MainContent')

        if container_main:
            return str(container_main)    
    except Exception as ex:
        log.error(f'Возникал ошибка в ходе перехода по ссылке: {url}: ОШИБКА {ex}')


def main_def_to_uload(cursor, conn):
    
    create_tmp_table(cursor, conn)

    vacancies = select_unprocessed(cursor)
    total = len(vacancies)
    log.info(f'Найдено необработанных вакансий: {total}')

    for i, (row_id, vac_id, vac_link) in enumerate(vacancies):
        log.info(f'[{i+1}/{total}] Обработка: {vac_id}')

        html = get_vacancy_from_web(vac_link)
        
        if not html:
            log.warning(f'Пустой HTML для {vac_id} пропупскаем')

            mark_as_processed(cursor, conn, vac_id)
            continue
        
        data = model_work(html)

        if not data:

            log.warning(f'LLM упал с ошибкой для {vac_id} - пропускаем')
            continue

        data['published_at'] = datetime.now().isoformat()
        update_vacancy(cursor, conn, vac_id, data)
        mark_as_processed(cursor, conn, vac_id)

        log.info(f'Вакансия {vac_id} обновdлена')


if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, 'GP_DB.db')

    log.info('Старт обработки')

    try:
        with sqlite3.connect(os.path.join(base_dir, 'GP_DB.db')) as conn:
            log.info('Соединение с БД установлено')

            cursor = conn.cursor()
            main_def_to_uload(cursor, conn)

            log.info('Соединение с БД закрыто')
    finally:
        log.info('Драйвер успешно закрыт')
