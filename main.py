from src.database import Database
from src.db_manager import DBManager
from src.hh_api import HH_API

COMPANIES = [
    "Яндекс",
    "СБЕР",
    "АСПЭК-Авто",
    "OZON",
    "Гвоздь",
    "МАГНИТ",
    "МТС",
    "Форвард-Авто",
    "МегаФон",
    "Школа английcкого языка Orange English",
]


def main():
    """Основная функция программы"""

    # Инициализация
    db = Database()
    hh_api = HH_API()

    try:
        # Подключение к БД
        db.connect()
        db.create_tables()

        # Сбор данных
        print("Собираем данные...")

        for company_name in COMPANIES:
            print(f"Обрабатываем работодателя: {company_name}")

            # Получаем ID компании
            employer_id = hh_api.get_employer_id(company_name)
            if not employer_id:
                print(f"Не найден ID компании {company_name}")
                continue

            # Получаем информацию о компании
            employer_info = hh_api.get_employer_info(employer_id)
            if not employer_info:
                continue

            # Сохраняем компанию в БД
            company_id = db.insert_company(
                employer_info["name"],
                employer_info.get("description", ""),
                employer_info.get("site_url", ""),
            )

            if not company_id:
                continue

            # Получаем вакансии
            vacancies = hh_api.get_all_vacancies(employer_id)
            print(f"Найдено вакансий: {len(vacancies)}")

            # Сохраняем вакансии
            for vacancy in vacancies:
                salary = vacancy.get("salary")
                db.insert_vacancy(
                    company_id,
                    vacancy["name"],
                    salary["from"] if salary else None,
                    salary["to"] if salary else None,
                    salary["currency"] if salary else None,
                    vacancy["alternate_url"],
                    vacancy["published_at"],
                )

        # Работа с менеджером БД
        manager = DBManager()

        while True:
            print("\n" + "=" * 50)
            print("Меню управления базой данных:")
            print("1. Компании и количество вакансий")
            print("2. Все вакансии")
            print("3. Средняя зарплата")
            print("4. Вакансии с зарплатой выше средней")
            print("5. Поиск вакансий по ключевому слову")
            print("0. Выход")

            choice = input("Выберите действие: ")

            if choice == "1":
                result = manager.get_companies_and_vacancies_count()
                print("\nКомпании и количество вакансий:")
                for company, count in result:
                    print(f"Количество вакансий компании {company}: {count}")

            elif choice == "2":
                result = manager.get_all_vacancies()
                print("\nВсе вакансии:")
                for company, title, salary_from, salary_to, currency, url in result:
                    salary = (
                        f"{salary_from}-{salary_to} {currency}"
                        if salary_from or salary_to
                        else "Не указана"
                    )
                    print(f"{company}: {title} - {salary} - {url}")

            elif choice == "3":
                avg_salary = manager.get_avg_salary()
                print(f"\nСредняя зарплата: {avg_salary} RUB")

            elif choice == "4":
                result = manager.get_vacancies_with_higher_salary()
                print("\nВакансии с зарплатой выше средней: ")
                for company, title, salary_from, salary_to, currency, url in result:
                    salary = f"{salary_from}-{salary_to} {currency}"
                    print(f"{company}: {title} - {salary} - {url}")

            elif choice == "5":
                keyword = input("Введите ключевое слово для поиска: ")
                result = manager.get_vacancies_with_keyword(keyword)
                print(f"\nРезультаты поиска по '{keyword}':")
                for company, title, salary_from, salary_to, currency, url in result:
                    salary = (
                        f"{salary_from}-{salary_to} {currency}"
                        if salary_from or salary_to
                        else "Не указана"
                    )
                    print(f"{company}: {title} - {salary} - {url}")

            elif choice == "0":
                break

            else:
                print("Неверный ввод. Попробуйте снова.")

    except Exception as e:
        print(f"Произошла ошибка: {e}")

    finally:
        db.disconnect()


if __name__ == "__main__":
    main()
