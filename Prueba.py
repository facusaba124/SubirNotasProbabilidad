import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file(
    "secrets/cargarnotasprobabilidad-9caca2f93f76.json",
    scopes=SCOPES
)

gc = gspread.authorize(creds)

url = input("URL: ")

try:
    sh = gc.open_by_url(url)
    print("Conectado correctamente")
    print("Nombre:", sh.title)

except Exception as e:
    print(type(e))
    print(e)