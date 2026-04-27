import time
import gc
import sqlite3
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import fake_useragent
import os
import file_sripts
import db_sripts
from logger_master import get_logger
import slice_data_from_html 

log = get_logger('PARSING')


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


def get_info_hh():
    try:
        driver.get('https://hh.ru/')
        WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )
        
        log.info(f'Успешно перешли на главную страницу, ожидаем 0.75 сек')
        time.sleep(0.75)

        if driver.current_url:        
            driver.get('https://hh.ru/search/vacancy/')
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
            )
            
            if driver.current_url:
                log.info('--- УСПЕШНЫЙ ПЕРЕХОД К ВАКАНСИЯМ --- ')

                result = driver.page_source
                log.info(result)
                return result
            else:
                log.info(f'Переход к вакансиям не удался')
                return -1
        else:
            log.warning(f'Переход на главную страницу не удался...')
    except Exception as ex:
        log.error(f'Возникла ошибка: {ex}')  
    finally:
        driver.quit()
    

def get_info_from_user() -> str:
    # job_title = input(f'Введите профессию для поиска')
    job_title = 'Аналитик данных'
    return job_title


def prepare_user_response(text: str) -> str | int:
    try: 
        if isinstance(text, str) and len(text) >= 1:
            text = text.strip()
            words = ''

            # if ' ' in text:
            #     key_words = text.split()
            #     words = '+'.join(key_words)

            words = '+'.join(text.split())

            synonims = '&ored_clusters=true'
            result_link = '?text=' + words + synonims
            
            log.debug(f'Итоговая ссылка с названием профессии: {result_link}')

            return result_link
        else:
            log.warning(f'Некоректные входные данные в prepare_user_response: {text}')
            return -1
    except Exception as ex:
        log.error(f'--- ОШИБКА ПРИ ОБРАБОТКЕ ЗАПРОСА: функция: prepare_user_response\n\nОШИБКА: {ex}')
        return -1


def get_info_job_title(total_link, driver):
    all_html = ''

    try:
        driver.get('https://hh.ru/')

        WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )
        
        log.info(f'Успешно перешли на главную страницу, ожидаем 0.75 сек')
        time.sleep(0.75)

        if driver.current_url:        
                page = 0

                while True:
                    url = f'https://hh.ru/search/vacancy{total_link}&salary=&label=with_salary&search_field=name&area=113&page={page}'
                    driver.get(url=url)
                    WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.TAG_NAME, 'body'))
                    )
            
                    if driver.current_url:
                        log.info(f'--- УСПЕШНЫЙ ПЕРЕХОД К ВАКАНСИЯМ (страница {page})--- ')

                        result = driver.page_source
                        all_html += result

                        # создание чек-поинта для больших обновлений данных
                        if page > 0 and page % 5 == 0:
                            
                            # создаем папку для сохранения файлов
                            name_of_dir = 'checkpoints'
                            file_sripts.create_checkpoints_dir()

                            vac_name = total_link.replace('?text=', '').replace('&ored_clusters=true', '').replace('+', '_')
                            path_to_load_check = os.path.join(name_of_dir, f'page_{vac_name}_checkpoint_{page}.html')

                            with open(path_to_load_check, 'w', encoding='utf-8') as file:
                                file.write(all_html)
                                all_html = ''

                            log.info(f'--- ПРОМЕЖУТОЧНОЕ СОХРАНЕНИЕ /// страницы {page-5}-{page}) ---')                    
                            
                            gc.collect()
                            log.debug(f'Очистка оперативной памяти через GC после чекпоинта: {page}')
                        
                        soup = BeautifulSoup(result, 'html.parser')
                        future_page = soup.find('a', attrs={'data-qa': 'pager-page'}, string=str(page + 2))
                        

                        del soup
                        gc.collect()
                        log.debug(f'Очистка переменной soup после: {page}')

                        if future_page:
                            page += 1
                        else:
                            log.info(f'ВСЕГО СОБРАНО СТРАНИЦ {page + 1}')
                            break

                    else:
                        log.warning(f'Переход к вакансиям не удался')
                        return -1

                if all_html:
                    vac_name = total_link.replace('?text=', '').replace('&ored_clusters=true', '').replace('+', '_')
                    path_to_load_check = os.path.join(name_of_dir, f'page_{vac_name}_checkpoint_{page}.html')
                    
                    with open(path_to_final, 'w', encoding='utf-8') as file:
                        file.write(all_html)
                    
                    gc.collect()
                    log.debug(f'Очистка оперативной памяти через GC после финальной страницы')

                log.info(f'--- ФИНАЛЬНОЕ СОХРАНЕНИЕ ---')

                return 1
        else:
            log.warning(f'Переход на главную страницу не удался...')
    except Exception as ex:
        log.error(f'Возникла ошибка: {ex}')  



if __name__ == '__main__':

    # возьмем самые популярные вакансии, ссылка на сттью hh: https://hh.ru/article/32303
    vac_names = [
        "Программист Python",
        "Программист Java",
        "Программист JavaScript",
        "Программист C++",
        "Программист C#",
        "Программист Go",
        "Программист PHP",
        "Разработчик 1С",
        "Frontend разработчик",
        "Backend разработчик",
        "Fullstack разработчик",
        "Mobile разработчик Android",
        "Mobile разработчик iOS",
        "Разработчик React",
        "Разработчик Vue",
        "Аналитик данных",
        "Data Scientist",
        "Data Engineer",
        "ML Engineer",
        "AI Engineer",
        "Бизнес аналитик",
        "Системный аналитик",
        "BI аналитик",
        "Инженер данных",
        "NLP инженер",
        "DevOps инженер",
        "Cloud инженер",
        "Системный администратор",
        "Сетевой инженер",
        "DBA администратор баз данных",
        "Инженер по кибербезопасности",
        "Специалист информационной безопасности",
        "Site Reliability Engineer",
        "Архитектор программного обеспечения",
        "Технический директор CTO",
        "QA инженер",
        "Тестировщик",
        "Автоматизатор тестирования",
        "Продуктовый менеджер",
        "Проджект менеджер",
        "Scrum мастер",
        "Технический писатель",
        "UX UI дизайнер",
        "Графический дизайнер",
        "Game разработчик",
        "Бухгалтер",
        "Главный бухгалтер",
        "Финансовый аналитик",
        "Финансовый директор",
        "Экономист",
        "Аудитор",
        "Налоговый консультант",
        "Риск менеджер",
        "Инвестиционный аналитик",
        "Актуарий",
        "Менеджер по продажам",
        "Руководитель отдела продаж",
        "Маркетолог",
        "Digital маркетолог",
        "SEO специалист",
        "Контент менеджер",
        "SMM менеджер",
        "Таргетолог",
        "Менеджер по работе с клиентами",
        "Менеджер по развитию бизнеса",
        "HR менеджер",
        "Рекрутер",
        "HR бизнес партнер",
        "Менеджер по обучению персонала",
        "Операционный директор",
        "Генеральный директор",
        "Врач терапевт",
        "Врач педиатр",
        "Врач кардиолог",
        "Врач хирург",
        "Медицинская сестра",
        "Фармацевт",
        "Психолог",
        "Психотерапевт",
        "Инженер конструктор",
        "Инженер проектировщик",
        "Инженер технолог",
        "Инженер по охране труда",
        "Прораб",
        "Архитектор",
        "Сметчик",
        "Электромонтажник",
        "Сварщик",
        "Автослесарь",
        "Логист",
        "Менеджер по логистике",
        "Водитель",
        "Кладовщик",
        "Оператор производственной линии",
        "Повар",
        "Администратор",
        "Менеджер ресторана",
        "Юрист",
        "Юрисконсульт",
    ]

    driver = create_driver()

    log.info('--- 1. Начало работы ---')
    # job_name = get_info_from_user()

    log.info('--- 2. Обработка запроса ---')

    for curr_vac_name in vac_names:
        second_link_part = prepare_user_response(curr_vac_name)    

        if second_link_part == -1:
            log.error(' --- ОШИБКА: некорректный запрос пользователя')
        else:
            log.info('--- 3. Получение страницы ---')
            page_text = get_info_job_title(second_link_part, driver)
            if page_text == -1:
                log.error(f'ОШИБКА при обращении к hh.ru для профессии: {curr_vac_name}')


        log.info(f'Закончена обработка профессии: {curr_vac_name}')
        
        log.debug('Программа остановлена на 2 секунды при смене профессии')
        time.sleep(2)

    driver.quit()
    log.info('Драйвер успешно закрыт')

    log.info('Начат процесс обработки HTML-файлов и загрузки данных в БД')
    connection = sqlite3.connect('GP_DB.db')
    cursor = connection.cursor()

    db_sripts.create_table(cursor, connection)

    slice_data_from_html.parse_all_checkpoints(cursor, connection)

    print(db_sripts.select_limit_data(cursor))

    connection.close()
    log.info('Соединение успешно закрыт')
    