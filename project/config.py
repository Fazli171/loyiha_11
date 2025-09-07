import environs

env = environs.Env()

DATABASE = env.str('DATABASE', 'db_vak')
TRUSTED = env.str('TRUSTED', True)
SERVER = env.str('SERVER', 'localhost')
DRIVER = env.str("DRIVER", "ODBC Driver 17 for SQL Server")

BASE_URL = "https://api.hh.ru/vacancies"