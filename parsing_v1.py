import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import fake_useragent


def create_driver():
    new_options = webdriver.ChromeOptions()
    user_agent = fake_useragent.UserAgent()

    new_options.add_argument(f'user-agent={user_agent.random}')
    new_options.add_argument('--disable-blink-features=AutomationControlled')
    new_options.add_experimental_option('excludeSwitches', ['enable-automation'])

    driver = webdriver.Chrome(options=new_options)

    if driver:
        print(f'Драйвер для работы с selenium-создан: {driver}')
        return driver
    else:
        return None


def get_info_hh():
    driver = create_driver()

    try:
        driver.get('https://hh.ru/')
        WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )
        
        print(f'Успешно перешли на главную страницу, ожидаем 0.75 сек')
        time.sleep(0.75)

        if driver.current_url:        
            driver.get('https://hh.ru/search/vacancy/')
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
            )
            
            if driver.current_url:
                print('--- УСПЕШНЫЙ ПЕРЕХОД К ВАКАНСИЯМ --- ')

                result = driver.page_source
                print(result)
                return result
            else:
                print(f'Переход к вакансиям не удался')
                return -1
        else:
            print(f'Переход на главную страницу не удался...')
    except Exception as ex:
        print(f'Возникла ошибка: {ex}')  
    finally:
        driver.quit()
    

def get_info_from_user() -> str:
    # job_title = input(f'Введите профессию для поиска')
    job_title = 'Аналитик данных'
    return job_title

def prepare_user_response(text: str) -> str | int:
    try: 
        if isinstance('text', str) and len(text) >= 1:
            text = text.strip()
            words = ''

            if ' ' in text:
                key_words = text.split()
                for item in key_words:
                    words += item + '+'

            synonims = '&ored_clusters=true'
            result_link = '?text=' + words + synonims
            return result_link
        else:
            return -1
    except Exception as ex:
        print(f'--- ОШИБКА ПРИ ОБРАБОТКЕ ЗАПРОСА: функция: prepare_user_response\n\nОШИБКА: {ex}')
        return -1



def get_info_job_title(total_link):
    driver = create_driver()

    try:
        driver.get('https://hh.ru/')
        WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )
        
        print(f'Успешно перешли на главную страницу, ожидаем 0.75 сек')
        time.sleep(0.75)

        if driver.current_url:        
            url = f'https://hh.ru/search/vacancy{total_link}&salary=&label=with_salary&search_field=name&area=113'
            driver.get(url=url)
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
            )
            
            if driver.current_url:
                print('--- УСПЕШНЫЙ ПЕРЕХОД К ВАКАНСИЯМ --- ')

                result = driver.page_source
                
                with open(f'page_{total_link}.html', 'w', encoding='utf-8') as f:
                    f.write(result)
                    print(f' --- СТРАНИЦА СОХРАНЕНА В HTML')
                return 1
            else:
                print(f'Переход к вакансиям не удался')
                return -1
        else:
            print(f'Переход на главную страницу не удался...')
    except Exception as ex:
        print(f'Возникла ошибка: {ex}')  
    finally:
        driver.quit()







if __name__ == '__main__':
    print('--- 1. Начало работы ---')
    job_name = get_info_from_user()

    print('--- 2. Обработка запроса ---')
    second_link_part = prepare_user_response('Аналитик данных')    
    if second_link_part == -1:
        print(' --- ОШИБКА: некорректный запрос пользователя')
    else:
        print('--- 3. Получение страницы ---')
        page_text = get_info_job_title(second_link_part)
        if page_text == -1:
            print(' --- ОШИБКА: возникла ошибка при обращении к hh.ru')
