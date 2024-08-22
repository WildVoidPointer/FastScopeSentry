import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

JWT_SECRET_KEY = "sentry-insecure-@_$#n9&ye_r^03&v#i%r9ytmn2speyrq7+-=*o6i7%09q7aqf4"

AUTH_SECRET_KEY = "sentry-eyJhbGciOiJIUz-@_$#n9&ye_r^03&v#i%r9y6InIxMjMiAiOjE3MTc5Nj"

USER_AGENT_DICT_PATH = os.path.join(BASE_DIR, "data", "crawler", "UserAgent.txt")

FINGERPRINT_LIST_PATH = os.path.join(BASE_DIR, "data", "crawler", "fingerprint", "fingerprint.yaml")

LOGGER_CONF_PATH = os.path.join(BASE_DIR, "config", "logcfg.ini")

PORT_SCAN_CONF_PATH = os.path.join(BASE_DIR, "data", "portscan", "portscancfg.json")

TEMPLATE_SCAN_SERVICE_PATH = r"C:\Users\R123\Downloads\nuclei_3.2.8_windows_amd64\nuclei.exe"

INTELLI_QA_TEMPLATE = os.path.join(BASE_DIR, "data", "intellitmpl", "sparktemplate.json")

TASK_EXECUTE_CYCLE = 3.0

DATABASES_CONF = {
    "default": {
        "DB_ENGINE": "mysql+pymysql",
        "USERNAME": "root",
        "PASSWORD": "123456",
        "HOST": "127.0.0.1",
        "PORT": "3308",
        "DBNAME": "sentryapp"
    }
}

DEFAULT_DB_CONF = DATABASES_CONF.get('default')
