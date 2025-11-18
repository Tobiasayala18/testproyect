from fastapi import FastAPI
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import json
import os

app = FastAPI()

# -------------------------------
# CONFIGURACIÓN GOOGLE SHEETS
# -------------------------------
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# LEER LA VARIABLE DE ENTORNO CON LAS CREDENCIALES
service_account_info = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT"])
CREDS = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)

CLIENT = gspread.authorize(CREDS)

# IDs de tus sheets
SHEET_COMPETENCIA = "TU_SHEET_COMPETENCIA_ID"
SHEET_NUESTROS = "TU_SHEET_NUESTROS_ID"

# -------------------------------
# FUNCIÓN ÚTIL PARA LEER SHEETS
# -------------------------------
def read_sheet(sheet_id, tab_name):
    sheet = CLIENT.open_by_key(sheet_id).worksheet(tab_name)
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    return df

# -------------------------------
# 1) ACTUALIZAR Y GENERAR JSON FINAL
# -------------------------------
@app.get("/cron/actualizar")
def actualizar():
    try:
        df_comp = read_sheet(SHEET_COMPETENCIA, "Hoja1")
        df_nuestros = read_sheet(SHEET_NUESTROS, "Hoja1")

        # RENOMBRAR COLUMNAS PARA ESTÁNDAR UNIFICADO
        df_comp["tipo"] = "competencia"
        df_nuestros["tipo"] = "nuestro"

        df_final = pd.concat([df_comp, df_nuestros], ignore_index=True)

        # Guardar JSON
        df_final.to_json("precios.json", orient="records")

        return {"ok": True, "message": "Datos actualizados correctamente."}

    except Exception as e:
        return {"ok": False, "error": str(e)}

# -------------------------------
# 2) DEVOLVER EL JSON FINAL
# -------------------------------
@app.get("/data/precios")
def get_precios():
    try:
        with open("precios.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except:
        return {"ok": False, "error": "No hay datos generados todavía."}
