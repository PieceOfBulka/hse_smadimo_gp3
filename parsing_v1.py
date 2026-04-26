import requests 
import time
from selenium import webdriver
import fake_useragent

def create_headers() -> dict:
    user_agent = fake_useragent.UserAgent()

    headers = {
        'User-Agent': user_agent.random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    }

    print(f'User-Agent для сессии: {headers}')

    return headers


def get_info_hh(headers: dict):
    driver = webdriver.Chrome()

    try:
        response_main_page = driver.get('https://hh.ru/')
        time.sleep(1)

        if response_main_page.status_code == 200:
            print(f'Успешно перещли на главную страницу, ожидаем 1 сек')

            time.sleep(1)  

            get_f1 = driver.get('https://hh.ru/search/vacancy/', headers=headers)
            
            if get_f1:
                result = get_f1.text

                print(result)
                return result
            else:
                print('Переход к вакансиям не сложился...')
        else:
            print(f'Переход на главную страницу не удался...')
    except Exception as ex:
        print(f'Возникла ошибка: {ex}')  
    finally:
        driver.quit()
    

if __name__ == '__main__':
    print('--- Начало работы ---')

    new_headers = create_headers()

    get_info_hh(new_headers)