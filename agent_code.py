import time
import gc
import sqlite3
import random
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

log = get_logger('AGENT_COLLENT_DATA')


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


def prepare_user_response(text: str) -> str | int:
    try: 
        if isinstance(text, str) and len(text) >= 1:
            text = text.strip()
            words = ''

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


def get_info_job_title(total_link, driver, name_of_dir):
    all_html = ''
    page = 0
    
    try:     
        while True:
            
            # ссылка на чтение запросов по названию специальности, порядок: по дате публикации
            url = f'https://hh.ru/search/vacancy{total_link}area=113&label=with_salary&ored_clusters=true&search_field=name&order_by=publication_time'

            driver.get(url=url)
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
            )

            scroll_down(driver) 
    
            if driver.current_url:
                log.info(f'--- УСПЕШНЫЙ ПЕРЕХОД К ВАКАНСИЯМ (страница {page})--- ')

                result = driver.page_source
                all_html += result

                # создание чек-поинта для больших обновлений данных
                if page > 0 and page % 5 == 0:
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

                if page == 10:
                    break

        if all_html:
            vac_name = total_link.replace('?text=', '').replace('&ored_clusters=true', '').replace('+', '_')
            path_to_load_check = os.path.join(name_of_dir, f'page_{vac_name}_checkpoint_{page}.html')
            
            with open(path_to_load_check, 'w', encoding='utf-8') as file:
                file.write(all_html)
            
            gc.collect()
            log.debug(f'Очистка оперативной памяти через GC после финальной страницы')
        log.info(f'--- ФИНАЛЬНОЕ СОХРАНЕНИЕ ---')
        return 1
    
    except Exception as ex:
        log.error(f'Возникла ошибка: {ex}')  
