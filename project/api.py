import requests
from config import BASE_URL

def get_vacancies(text=""):
    try:
        n = int(input("Vakansiyalar sonini kiriting >>> "))
    except ValueError:
        print("Faqat raqam kiriting, standart 20 olinadi.")
        n = 20

    per_page = n
    params = {"per_page": per_page, "text": text}
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()

    vakansiyalar = response.json().get("items", [])
    results = []

    for vak in vakansiyalar:
        salary = vak.get("salary") or {}
        min_salary = salary.get("from") or 0
        max_salary = salary.get("to") or min_salary
        currency = salary.get("currency") or '???'

        results.append({
            "category": vak.get("professional_roles", [{'name': 'kritilmagan'}])[0].get("name"),
            "title": vak.get("name"),
            "h_id": vak.get("id"),
            "publish_date": vak.get("published_at"),
            "company": vak.get("employer", {'name': 'kritilmagan'}).get("name"),
            "skills": vak.get("snippet", {'requirement': 'kritilmagan'}).get("requirement"),
            "country": vak.get("area", {'name': 'kritilmgan'}).get("name"),
            "location": vak.get("address", {}).get("raw") if vak.get("address") else "Ko'rsatilmagan",
            "min_salary": min_salary,
            "max_salary": max_salary,
            "currency": currency
        })

    return results
