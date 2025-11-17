from fastapi import FastAPI
from google.oauth2.service_account import Credentials
import gspread
import pandas as pd
import os, json

app = FastAPI()

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# 🔗 Tus Google Sheets
SHEETS = {
    "competencia": "https://docs.google.com/spreadsheets/d/1Uze_ajhdMESfiBdg85EwR_u3SDjA_xXwAKKGk1AU8bs/edit?usp=sharing",
    "nuestro": "https://docs.google.com/spreadsheets/d/1QV_9PtLKhHwD_2VLe2-KBmPPnA_jUx8BokmlyQz-pa8/edit?usp=sharing"
}


@app.get("/")
def home():
    return {"status": "ok", "message": "API funcionando correctamente"}


@app.get("/sheet/{name}")
def leer_sheet(name: str):
    """Lee 1 de los 2 Google Sheets definidos en SHEETS"""

    if name not in SHEETS:
        return {
            "error": "Sheet no encontrado",
            "disponibles": list(SHEETS.keys())
        }

    url = SHEETS[name]

    # Credenciales desde variable de entorno
    service_account_info = json.loads(os.environ["GOOGLE_CREDENTIALS"])
    creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)

    gc = gspread.authorize(creds)
    sh = gc.open_by_url(url)
    worksheet = sh.sheet1

    data = worksheet.get_all_records()
    df = pd.DataFrame(data)

    return df.to_dict(orient="records")
