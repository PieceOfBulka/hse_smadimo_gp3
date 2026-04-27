import sqlite3
from logger_master import get_logger

log = get_logger('DB')

def create_table(cursor, conn):
    try:
        query = """ CREATE TABLE IF NOT EXISTS vacancies (
        id INTEGER PRIMARY KEY,
        hh_vac_id TEXT NOT NULL,
        hh_vac_link TEXT NOT NULL,
        title TEXT NOT NULL,
        experience TEXT,
        employment TEXT,
        schedule TEXT,
        salary_raw TEXT,
        salary_from INTEGER,
        salary_to INTEGER,
        currency TEXT,
        employer TEXT,
        address_raw TEXT,
        area TEXT,
        skills TEXT, -- передаем в формате json
        published_at TIMESTAMP
        );
        """
    
        cursor.execute(query)
        conn.commit()

        log.info(f'СОЗДАНА ТАБЛИЦА vacancies')
    except Exception as ex:
        log.error(f'Возникла ошибка при первичном создании таблицы: {ex}')


def insert_data_first_batch(cursor, conn, batch_list):
    try:
        
        query = """ INSERT OR IGNORE INTO vacancies
        (hh_vac_id, hh_vac_link, title, experience, salary_raw, employer, address_raw)
        VALUES
        (:hh_vac_id, :hh_vac_link, :title, :experience, :salary_raw, :company_name, :address_raw)    
        """

        cursor.executemany(query, batch_list)
        conn.commit()
        log.info(f'--- Сохранено {len(batch_list)} вакансий ---')
    except Exception as ex:
        log.error(f'Возникла ошибка при первичном создании таблицы: {ex}')


def select_all_data(cursor):
    try:
        query = """ SELECT *
        FROM vacancies;
        """ 

        cursor.execute(query)
        answer = cursor.fetchall()
        return answer
    except Exception as ex:
        log.error(f'Возникла ошибка при первичном создании таблицы: {ex}')

def select_count_data(cursor):
    try:
        query = """ SELECT 
        count(id),
        count(hh_vac_id),
        count(hh_vac_link),
        count(title),
        count(experience),
        count(employment),
        count(schedule),
        count(salary_raw),
        count(salary_from),
        count(salary_to),
        count(currency),
        count(employer),
        count(address_raw),
        count(area),
        count(address_raw),
        count(skills),
        count(published_at)
        FROM vacancies;
        """ 

        cursor.execute(query)
        answer = cursor.fetchall()
        return answer
    except Exception as ex:
        log.error(f'Ошибка в select_count_data: {ex}')


def select_limit_data(cursor, limit=100):
    try:
        # query = f""" SELECT *
        # FROM vacancies
        # LIMIT {limit};
        # """ 
        # cursor.execute(query)
        
        query = "SELECT * FROM vacancies LIMIT ?"
        cursor.execute(query, (limit,))
        
        answer = cursor.fetchall()

        log.debug(f'Выборка в: {limit} строк из таблицы vacancies излечена')

        return answer
    except Exception as ex:
        log.error(f'Возникла ошибка при первичном создании таблицы: {ex}')


def DROP_TABLE(cursor, conn):
    try:
        query = """DROP TABLE IF EXISTS vacancies;"""
        
        cursor.execute(query)
        conn.commit()

        log.warning(f'ТАБЛИЦА УСПЕШНО УДАЛЕНА vacancies - НЕ ОБРАЩАТЬСЯ')
    except Exception as ex:
        log.error(f'Возникла ошибка при первичном создании таблицы: {ex}')

if __name__ == '__main__':
    connection = sqlite3.Connection('/Users/anastasia/Desktop/HSE/HSE_3/СМАДИМО/GP_3/hse_smadimo_gp3/GP_DB.db')
    cursor = connection.cursor()

    # create_table(cursor, connection)

    # DROP_TABLE(cursor, connection)

    print(select_count_data(cursor))

    connection.close()