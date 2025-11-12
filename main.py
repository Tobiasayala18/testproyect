from fastapi import FastAPI
from google.oauth2.service_account import Credentials
import gspread
import pandas as pd
import os, json

app = FastAPI()

# Alcances requeridos
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# URL del Google Sheet
SHEET_URL = "https://docs.google.com/spreadsheets/d/18pObgvT-LmFRUAC_99N0MSpE_hnJM8nXs021Qs9MCFs/edit?usp=sharing"


@app.get("/")
def home():
    return {"status": "ok", "message": "API funcionando correctamente"}


@app.get("/sheet")
def leer_sheet():
    """Lee los datos del Google Sheet y los devuelve en formato JSON"""

    # ✅ Leer credenciales desde variable de entorno
    service_account_info = json.loads(os.environ["GOOGLE_CREDENTIALS"])
    creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)

    # Conectar con Google Sheets
    gc = gspread.authorize(creds)
    sh = gc.open_by_url(SHEET_URL)
    worksheet = sh.sheet1
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    return df.to_dict(orient="records")


@app.get("/privacy")
def privacy():
    """Endpoint requerido por OpenAI para el GPT público"""
    return {
        "title": "Política de Privacidad - Analizador de Precios",
        "description": (
            "Esta API solo accede a datos públicos del Google Sheet autorizado. "
            "No recopila, almacena ni comparte información personal de los usuarios."
        ),
        "contact": "tobias.ayala.ortiz@example.com"
    }
