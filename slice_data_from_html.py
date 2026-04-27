import time
from bs4 import BeautifulSoup
import fake_useragent
import os
import file_sripts
import db_sripts


def get_title(data_item):
    title_tag = data_item.find(attrs={'data-qa': 'serp-item__title-text'})
    if title_tag:
        title = title_tag.get_text(strip=True)
    else:
        title = ''
    
    return title


def get_vac_id(data_item):
    link_tag = data_item.find('a', attrs={'data-qa': 'serp-item__title'})
    if link_tag:
        href = link_tag['href']
    else:
        href = ''
    
    vac_id = data_item.find('div', id=True)
    if vac_id:
        vac_id = vac_id['id']
        link = f'https://hh.ru/vacancy/{vac_id}'
    else:
        link = href.split("?")[0]
        vac_id = link.split('/')[-1]
    
    return vac_id, link


def get_company_name(data_item):
    company = data_item.find(attrs={'data-qa': 'vacancy-serp__vacancy-employer-text'})
    if company:
        name = company.get_text(strip=True)
    else:
        name = ''
    
    return name


def get_salary(data_item):
    CURRENCY_SUMBOLS = [
        '₽',
        '$',
        '€',
        'руб',
        'RUB',
        'USD',
        'EUR',
        'KZT'
    ]
    salary = ''

    for span_tag in data_item.find_all('span'):
        text = span_tag.get_text(strip=True)
        if any(symb in text for symb in CURRENCY_SUMBOLS):
            salary = text
            break
    
    return salary


def get_exp(data_item):
    exp = data_item.find(attrs={"data-qa": lambda x: x and "work-experience" in x})
    if exp:
        exp_data = exp.get_text(strip=True)
    else:
        exp_data = ''
    
    return exp_data


def get_company_adress(data_item):
    address_tag = data_item.find(attrs={"data-qa": "vacancy-serp__vacancy-address"})
    if address_tag:
        address = address_tag.get_text(strip=True)
    else:
        address = ''
    
    return address


def get_first_data_batch(path_to_file):
    with open(path_to_file, encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    data_cards = soup.find_all('div', attrs={'data-qa': 'vacancy-serp__vacancy'})
    print(f'--- Найдено {len(data_cards)} вакансий')

    result = []

    for item in data_cards:
        title = get_title(item)
        vac_id, url = get_vac_id(item)
        company_name = get_company_name(item)
        salary = get_salary(item)
        experience = get_exp(item)
        address = get_company_adress(item)

        result.append({
            'title': title,
            'hh_vac_id': vac_id,
            'hh_vac_link': url,
            'company_name': company_name,
            'salary_raw': salary,
            'experience': experience,
            'address_raw': address,
            })
    
    return result

if __name__ == '__main__':
    pass