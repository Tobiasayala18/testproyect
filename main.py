from fastapi import FastAPI
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import json
import os

app = FastAPI()

# --------------------------------------------------------
# 1) Cargar credenciales desde VARIABLE DE ENTORNO
# --------------------------------------------------------
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# IMPORTANTE: La variable en Render se debe llamar GOOGLE_CREDENTIALS
service_account_info = json.loads(os.environ["GOOGLE_CREDENTIALS"])

CREDS = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
CLIENT = gspread.authorize(CREDS)

# --------------------------------------------------------
# 2) IDs de Sheets (EL ARCHIVO ES UNO SOLO)
# --------------------------------------------------------
SHEET_ID = "18hXubsYfy-YGHmejWGNB7p5nZzRvg103IxNsmd4RNxQ"

TAB_COMPETENCIA = "competencia_cache"
TAB_NUESTROS = "nuestro_cache"

# --------------------------------------------------------
# FUNCIÓN PARA LEER HOJAS
# --------------------------------------------------------
def read_sheet(sheet_id, tab_name):
    sheet = CLIENT.open_by_key(sheet_id).worksheet(tab_name)
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    return df

# --------------------------------------------------------
# 3) ENDPOINT — ACTUALIZAR Y GUARDAR JSON
# --------------------------------------------------------
@app.get("/cron/actualizar")
def actualizar():
    try:
        df_comp = read_sheet(SHEET_ID, TAB_COMPETENCIA)
        df_nuestros = read_sheet(SHEET_ID, TAB_NUESTROS)

        df_comp["tipo"] = "competencia"
        df_nuestros["tipo"] = "nuestro"

        df_final = pd.concat([df_comp, df_nuestros], ignore_index=True)
        df_final.to_json("precios.json", orient="records")

        return {"ok": True, "message": "Datos actualizados correctamente."}

    except Exception as e:
        return {"ok": False, "error": str(e)}

# --------------------------------------------------------
# 4) ENDPOINT — LEER JSON
# --------------------------------------------------------
@app.get("/data/precios")
def get_precios():
    try:
        with open("precios.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        return data

    except:
        return {"ok": False, "error": "No hay datos generados todavía."}
