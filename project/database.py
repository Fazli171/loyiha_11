import pyodbc
from config import DATABASE, SERVER, DRIVER, TRUSTED
from datetime import datetime

class Database:
    def __init__(self):
        self.server = SERVER
        self.database = DATABASE
        self.driver = DRIVER
        self.trusted = TRUSTED
        self.conn = None
        self.cursor = None

    def connect(self):
        """Bazaga ulanish"""
        self.conn = pyodbc.connect(
            f"DRIVER={{{self.driver}}};"
            f"SERVER={self.server};"
            f"DATABASE={self.database};"
            f"Trusted_Connection={'yes' if self.trusted else 'no'};"
        )
        self.cursor = self.conn.cursor()
        return self.cursor

    def close(self):
        """Ulanishni yopish"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    # ---------------- Jadvallar yaratish ----------------
    def create_skills(self):
        self.cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='skills' AND xtype='U')
        BEGIN
            CREATE TABLE skills (
                id INT IDENTITY(1,1) PRIMARY KEY,
                name NVARCHAR(450) UNIQUE
            )
        END
        """)
        self.conn.commit()


    def create_main_vacancy(self):
        self.cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='main_vacancy' AND xtype='U')
        BEGIN
            CREATE TABLE main_vacancy (
                id INT IDENTITY PRIMARY KEY,
                category NVARCHAR(100),
                title NVARCHAR(255),
                h_id BIGINT,
                publish_date DATETIME,
                company NVARCHAR(255),
                country NVARCHAR(100),
                location NVARCHAR(255),
                min_salary DECIMAL(10,2),
                max_salary DECIMAL(10,2),
                currency NVARCHAR(10)
            )
        END
        """)
        self.conn.commit()

    def create_vacancy_skill(self):
        self.cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='vacancy_skill' AND xtype='U')
        BEGIN
            CREATE TABLE vacancy_skill (
                id INT IDENTITY(1,1) PRIMARY KEY,
                skill_id INT,
                main_vacancy_id INT,
                FOREIGN KEY (skill_id) REFERENCES skills(id),
                FOREIGN KEY (main_vacancy_id) REFERENCES main_vacancy(id)
            )
        END
        """)
        self.conn.commit()

    # ---------------- Malumot qo'shish ----------------
    def insert_main_vacancy(self, vacancy):
        """main_vacancy va skills/vacancy_skill ga yozish"""
        try:
            # publish_date formatini datetime ga o'zgartirish
            publish_date = None
            if vacancy.get("publish_date"):
                try:
                    publish_date = datetime.fromisoformat(
                        vacancy["publish_date"].replace("Z", "").split("+")[0]
                    )
                except ValueError:
                    publish_date = None

            # main_vacancy ga yozish
            sql = """
            INSERT INTO main_vacancy 
            (category, title, h_id, publish_date, company, country, location, min_salary, max_salary, currency)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            self.cursor.execute(sql, (
                vacancy.get("category"),
                vacancy.get("title"),
                int(vacancy.get("h_id")),
                publish_date,
                vacancy.get("company"),
                vacancy.get("country"),
                vacancy.get("location"),
                float(vacancy.get("min_salary", 0)),
                float(vacancy.get("max_salary", 0)),
                vacancy.get("currency")
            ))
            self.conn.commit()
            main_vacancy_id = self.cursor.execute("SELECT @@IDENTITY").fetchone()[0]

            # Skills ro'yxatini olish
            skills_str = vacancy.get("skills") or ""
            skills_list = [s.strip() for s in skills_str.split(",") if s.strip()]

            for skill in skills_list:
                # Skills jadvalida skill borligini tekshirish
                row = self.cursor.execute("SELECT id FROM skills WHERE name = ?", skill).fetchone()
                if row:
                    skill_id = row[0]
                else:
                    # Yangi skill qo'shish
                    self.cursor.execute("INSERT INTO skills(name) VALUES (?)", skill)
                    self.conn.commit()
                    skill_id = self.cursor.execute("SELECT @@IDENTITY").fetchone()[0]

                # vacancy_skill ga bog'lash
                self.cursor.execute(
                    "INSERT INTO vacancy_skill(skill_id, main_vacancy_id) VALUES (?, ?)",
                    (skill_id, main_vacancy_id)
                )
            self.conn.commit()
            print("✅ Vakansiya va skills muvaffaqiyatli yozildi.")

        except Exception as e:
            print("❌ Xato:", e)
