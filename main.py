from fastapi import FastAPI
from google.oauth2.service_account import Credentials
import gspread
import pandas as pd

app = FastAPI()

# Tu archivo de credenciales
SERVICE_ACCOUNT_FILE = "credentials.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# Tu Google Sheet
SHEET_URL = "https://docs.google.com/spreadsheets/d/18pObgvT-LmFRUAC_99N0MSpE_hnJM8nXs021Qs9MCFs/edit?usp=sharing"

@app.get("/")
def home():
    return {"status": "ok", "message": "API funcionando correctamente"}

@app.get("/sheet")
def leer_sheet():
    """Lee los datos del Google Sheet y los devuelve en formato JSON"""
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    gc = gspread.authorize(creds)
    sh = gc.open_by_url(SHEET_URL)
    worksheet = sh.sheet1
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    return df.to_dict(orient="records")
