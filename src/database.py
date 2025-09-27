import psycopg2

from src.config import DB_CONFIG


class Database:
    """Класс для работы с базой данных PostgreSQL"""

    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self):
        """Подключение к базе данных"""
        try:
            self.connection = psycopg2.connect(**DB_CONFIG)
            self.cursor = self.connection.cursor()
            print("Успешное подключение к базе данных")
        except Exception as e:
            print(f"Ошибка подключения: {e}")

    def disconnect(self):
        """Отключение от базы данных"""
        if self.connection:
            self.cursor.close()
            self.connection.close()
            print("Отключение от базы данных")

    def create_tables(self):
        """Создание таблиц в базе данных"""
        try:
            # Таблица компаний
            self.cursor.execute(
                """
                                CREATE TABLE IF NOT EXISTS companies
                                (
                                    company_id
                                    SERIAL
                                    PRIMARY
                                    KEY,
                                    name
                                    VARCHAR
                                (
                                    255
                                ) NOT NULL UNIQUE,
                                    description TEXT,
                                    url VARCHAR
                                (
                                    255
                                )
                                    )
                                """
            )

            # Таблица вакансий
            self.cursor.execute(
                """
                                CREATE TABLE IF NOT EXISTS vacancies
                                (
                                    vacancy_id
                                    SERIAL
                                    PRIMARY
                                    KEY,
                                    company_id
                                    INTEGER
                                    REFERENCES
                                    companies
                                (
                                    company_id
                                ),
                                    title VARCHAR
                                (
                                    255
                                ) NOT NULL,
                                    salary_from INTEGER,
                                    salary_to INTEGER,
                                    currency VARCHAR
                                (
                                    10
                                ),
                                    url VARCHAR
                                (
                                    255
                                ) NOT NULL,
                                    published_date TIMESTAMP
                                    )
                                """
            )

            self.connection.commit()
            print("Таблицы успешно созданы")

        except Exception as e:
            print(f"Ошибка создания таблиц: {e}")

    def insert_company(self, name: str, description: str, url: str) -> int:
        """Вставка компании в базу данных"""
        try:
            self.cursor.execute(
                "INSERT INTO companies (name, description, url) VALUES (%s, %s, %s) RETURNING company_id",
                (name, description, url),
            )
            company_id = self.cursor.fetchone()[0]
            self.connection.commit()
            return company_id
        except Exception as e:
            print(f"Ошибка вставки компании {name}: {e}")
            return None

    def insert_vacancy(
        self,
        company_id: int,
        title: str,
        salary_from: int,
        salary_to: int,
        currency: str,
        url: str,
        published_date: str,
    ):
        """Вставка вакансии в базу данных"""
        try:
            self.cursor.execute(
                """INSERT INTO vacancies (company_id, title, salary_from, salary_to, currency, url, published_date)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (
                    company_id,
                    title,
                    salary_from,
                    salary_to,
                    currency,
                    url,
                    published_date,
                ),
            )
            self.connection.commit()
        except Exception as e:
            print(f"Ошибка вставки вакансии {title}: {e}")
