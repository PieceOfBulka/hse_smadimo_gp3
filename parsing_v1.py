import requests 
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
        # time.sleep(0.75)

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
    

if __name__ == '__main__':
    print('--- Начало работы ---')
    
    get_info_hh()