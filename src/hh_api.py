import time

import requests

HH_API_URL = "https://api.hh.ru/"


class HH_API:
    """Класс для работы с API HeadHunter"""

    def __init__(self):
        self.base_url = HH_API_URL

    def get_employer_id(self, company_name: str) -> str:
        """Получение ID работодателя по названию"""
        try:
            response = requests.get(
                f"{self.base_url}employers",
                params={"text": company_name, "only_with_vacancies": True},
            )
            response.raise_for_status()  # Проверяем успешность запроса
            employers_data = response.json().get("items", [])

            for employer in employers_data:
                if employer["name"].lower() == company_name.lower():
                    return employer["id"]

            return None
        except Exception as e:
            print(f"Ошибка получения ID для {company_name}: {e}")
            return None

    def get_employer_info(self, employer_id: str) -> dict:
        """Получение информации о работодателе"""
        try:
            response = requests.get(f"{self.base_url}employers/{employer_id}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Ошибка получения информации о работодателе {employer_id}: {e}")
            return None

    def get_vacancies(self, employer_id: str, page: int = 0) -> list:
        """Получение вакансий работодателя"""
        try:
            response = requests.get(
                f"{self.base_url}vacancies",
                params={"employer_id": employer_id, "page": page, "per_page": 100},
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Ошибка получения вакансий для {employer_id}: {e}")
            return None

    def get_all_vacancies(self, employer_id: str) -> list:
        """Получение всех вакансий работодателя"""
        all_vacancies = []
        page = 0

        while True:
            data = self.get_vacancies(employer_id, page)
            if not data or "items" not in data:
                break

            all_vacancies.extend(data["items"])

            if page >= data["pages"] - 1:
                break

            page += 1
            time.sleep(0.1)

        return all_vacancies
