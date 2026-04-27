import sqlite3


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
        area TEXT,
        skills TEXT, -- передаем в формате json
        published_at TIMESTAMP
        );
        """
    
        cursor.execute(query)
        conn.commit()
    except Exception as ex:
        print(f'Возникла ошибка при первичном создании таблицы: {ex}')


def insert_data(cursor, conn):
    try:
        query = """INSERT INTO vacancies (hh_vac_id, hh_vac_link, title, experience, employment, schedule, salary_from, salary_to, currency, employer, area, skills, published_at)
        VALUES
        ('98765432', 'https://hh.ru/vacancy/98765432', 'Data Scientist', 'between3And6', 'full', 'remote', 200000, 300000, 'RUR', 'Яндекс', 'Москва', '["Python", "ML", "SQL", "PyTorch"]', '2024-03-15 10:00:00'),
        ('11223344', 'https://hh.ru/vacancy/11223344', 'Backend Developer', 'between1And3', 'full', 'fullDay', 120000, 180000, 'RUR', 'Тинькофф', 'Санкт-Петербург', '["Python", "FastAPI", "PostgreSQL", "Redis"]', '2024-03-14 09:30:00'),
        ('55667788', 'https://hh.ru/vacancy/55667788', 'Junior Python Developer', 'noExperience', 'full', 'flexible', NULL, 80000, 'RUR', 'СберТех', 'Москва', '["Python", "Django"]', '2024-03-13 14:00:00');
        """

        cursor.execute(query)
        conn.commit()
    except Exception as ex:
        print(f'Возникла ошибка при первичном создании таблицы: {ex}')

def select_data(cursor):
    try:
        query = """ SELECT *
        FROM vacancies;
        """ 

        cursor.execute(query)
        answer = cursor.fetchall()
        return answer
    except Exception as ex:
        print(f'Возникла ошибка при первичном создании таблицы: {ex}')

def DROP_TABLE(cursor, conn):
    try:
        query = """DROP TABLE EXISTS vacancies;"""
        
        cursor.execute(query)
        conn.commit()
    except Exception as ex:
        print(f'Возникла ошибка при первичном создании таблицы: {ex}')

if __name__ == '__main__':
    connection = sqlite3.Connection('GP_DB.db')
    cursor = connection.cursor()

    create_table(cursor, connection)
    insert_data(cursor, connection)
    print(select_data(cursor))
    DROP_TABLE(cursor, connection)
    connection.close()