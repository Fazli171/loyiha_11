from database import Database
from api import get_vacancies

def main():
    db = Database()
    db.connect()
    print("✅ Bazaga ulanish amalga oshdi.")

    db.create_skills()
    db.create_main_vacancy()
    db.create_vacancy_skill()
    print("✅ Jadvallar yaratildi (agar mavjud bo'lmasa).")

    # API dan vakansiyalarni olish
    text = input("Qaysi kasb bo'yicha vakansiya qidirilsin? >>> ")
    vacancies = get_vacancies(text)

    print(f"✅ {len(vacancies)} ta vakansiya topildi. Bazaga yozilmoqda...")

    # Har birini bazaga yozish
    for vacancy in vacancies:
        db.insert_main_vacancy(vacancy)

    db.close()
    print("✅ Ulanish yopildi.")

if __name__ == "__main__":
    main()
