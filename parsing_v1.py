import requests 
import curl_cffi 


def get_vac_info():
    pass


def get_details():
    pass




try:
    get_f1 = requests.get('https://hh.ru/search/vacancy/')

    status = get_f1.status_code

    if int(status) == 200:
        print(get_f1.text)
    else:
        print(status)
except Exception as ex:
    print(f'Возникла ошибка: {ex}')