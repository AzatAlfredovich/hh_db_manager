from typing import List, Tuple

import psycopg2

from config import DB_CONFIG


class DBManager:
    """Класс для управления данными в базе данных"""

    def __init__(self):
        self.connection = psycopg2.connect(**DB_CONFIG)
        self.cursor = self.connection.cursor()

    def __del__(self):
        """Закрытие соединения при уничтожении объекта"""
        if self.connection:
            self.cursor.close()
            self.connection.close()

    def get_companies_and_vacancies_count(self) -> List[Tuple]:
        """Получает список всех компаний и количество вакансий у каждой компании"""
        query = """
                SELECT c.name, COUNT(v.vacancy_id)
                FROM companies c
                         LEFT JOIN vacancies v ON c.company_id = v.company_id
                GROUP BY c.name
                ORDER BY COUNT(v.vacancy_id) DESC \
                """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_all_vacancies(self) -> List[Tuple]:
        """Получает список всех вакансий с указанием компании, названия, зарплаты и ссылки"""
        query = """
                SELECT c.name, \
                       v.title,
                       COALESCE(v.salary_from, 0), \
                       COALESCE(v.salary_to, 0), \
                       v.currency,
                       v.url
                FROM vacancies v
                         JOIN companies c ON v.company_id = c.company_id
                ORDER BY c.name, v.title \
                """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_avg_salary(self) -> float:
        """Получает среднюю зарплату по вакансиям"""
        query = """
                SELECT AVG((COALESCE(salary_from, 0) + COALESCE(salary_to, 0)) / 2)
                FROM vacancies
                WHERE salary_from IS NOT NULL \
                   OR salary_to IS NOT NULL \
                """
        self.cursor.execute(query)
        result = self.cursor.fetchone()[0]
        return round(result, 2) if result else 0

    def get_vacancies_with_higher_salary(self) -> List[Tuple]:
        """Получает список вакансий с зарплатой выше средней"""
        avg_salary = self.get_avg_salary()
        query = """
                SELECT c.name, \
                       v.title,
                       COALESCE(v.salary_from, 0), \
                       COALESCE(v.salary_to, 0), \
                       v.currency,
                       v.url
                FROM vacancies v
                         JOIN companies c ON v.company_id = c.company_id
                WHERE (COALESCE(v.salary_from, 0) + COALESCE(v.salary_to, 0)) / 2 > %s
                ORDER BY (COALESCE(v.salary_from, 0) + COALESCE(v.salary_to, 0)) / 2 DESC \
                """
        self.cursor.execute(query, (avg_salary,))
        return self.cursor.fetchall()

    def get_vacancies_with_keyword(self, keyword: str) -> List[Tuple]:
        """Получает список вакансий, содержащих ключевое слово в названии"""
        query = """
                SELECT c.name, \
                       v.title,
                       COALESCE(v.salary_from, 0), \
                       COALESCE(v.salary_to, 0), \
                       v.currency,
                       v.url
                FROM vacancies v
                         JOIN companies c ON v.company_id = c.company_id
                WHERE LOWER(v.title) LIKE LOWER(%s)
                ORDER BY c.name, v.title \
                """
        self.cursor.execute(query, (f"%{keyword}%",))
        return self.cursor.fetchall()
