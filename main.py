from fastapi import FastAPI
from google.oauth2.service_account import Credentials
import gspread
import pandas as pd
import os, json

app = FastAPI()

# Scopes necesarios para leer y ESCRIBIR en Google Sheets
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Sheets originales (los que vos scrapeás)
SHEETS_ORIGINALES = {
    "competencia": "https://docs.google.com/spreadsheets/d/1Uze_ajhdMESfiBdg85EwR_u3SDjA_xXwAKKGk1AU8bs/edit?usp=sharing",
    "nuestro": "https://docs.google.com/spreadsheets/d/1QV_9PtLKhHwD_2VLe2-KBmPPnA_jUx8BokmlyQz-pa8/edit?usp=sharing"
}

# Sheet de CACHE (persistente y gratuito)
SHEET_CACHE = "https://docs.google.com/spreadsheets/d/18hXubsYfy-YGHmejWGNB7p5nZzRvg103IxNsmd4RNxQ/edit?usp=sharing"

# Nombres EXACTOS de las pestañas
TABLA_COMPETENCIA_CACHE = "competencia_cache"
TABLA_NUESTRO_CACHE = "nuestro_cache"


# ---------------------- FUNCIONES INTERNAS ---------------------- #

def cargar_credenciales():
    service_account_info = json.loads(os.environ["GOOGLE_CREDENTIALS"])
    return Credentials.from_service_account_info(service_account_info, scopes=SCOPES)


def leer_sheet(url):
    """Lee un Google Sheet y devuelve un DataFrame."""
    creds = cargar_credenciales()
    gc = gspread.authorize(creds)
    sh = gc.open_by_url(url)
    ws = sh.sheet1
    data = ws.get_all_records()
    return pd.DataFrame(data)


def escribir_cache(nombre_tab, df):
    """Escribe un DataFrame en una pestaña de cache."""
    creds = cargar_credenciales()
    gc = gspread.authorize(creds)
    sh = gc.open_by_url(SHEET_CACHE)

    try:
        ws = sh.worksheet(nombre_tab)
    except:
        ws = sh.add_worksheet(title=nombre_tab, rows="2000", cols="20")

    # Limpiar antes de escribir
    ws.clear()

    if df.empty:
        ws.update("A1", [["SIN DATOS"]])
        return

    # Escribir encabezados + datos
    rows = [df.columns.tolist()] + df.values.tolist()
    ws.update("A1", rows)


def leer_cache(nombre_tab):
    """Lee un cache desde una pestaña específica."""
    creds = cargar_credenciales()
    gc = gspread.authorize(creds)
    sh = gc.open_by_url(SHEET_CACHE)
    ws = sh.worksheet(nombre_tab)
    data = ws.get_all_records()
    return pd.DataFrame(data)


# ---------------------- ENDPOINTS ---------------------- #

@app.get("/")
def home():
    return {"status": "ok", "message": "API lista con cache persistente en Google Sheets."}


@app.get("/cron/actualizar")
def actualizar_cache():
    resultados = []

    for nombre, url in SHEETS_ORIGINALES.items():
        df = leer_sheet(url)

        if nombre == "competencia":
            escribir_cache(TABLA_COMPETENCIA_CACHE, df)
        else:
            escribir_cache(TABLA_NUESTRO_CACHE, df)

        resultados.append({
            "hoja": nombre,
            "filas_cargadas": len(df)
        })

    return {
        "status": "cache_actualizado",
        "detalles": resultados
    }


@app.get("/data/competencia")
def data_competencia():
    df = leer_cache(TABLA_COMPETENCIA_CACHE)
    return df.to_dict(orient="records")


@app.get("/data/nuestro")
def data_nuestro():
    df = leer_cache(TABLA_NUESTRO_CACHE)
    return df.to_dict(orient="records")


@app.get("/comparar")
def comparar(item: str):
    df_comp = leer_cache(TABLA_COMPETENCIA_CACHE)
    df_nuest = leer_cache(TABLA_NUESTRO_CACHE)

    comp_fil = df_comp[df_comp.apply(lambda x: item.lower() in str(x).lower(), axis=1)]
    nuest_fil = df_nuest[df_nuest.apply(lambda x: item.lower() in str(x).lower(), axis=1)]

    return {
        "item": item,
        "competencia": comp_fil.to_dict(orient="records"),
        "nuestro": nuest_fil.to_dict(orient="records")
    }


@app.get("/analizar")
def analizar(query: str):
    df_comp = leer_cache(TABLA_COMPETENCIA_CACHE)
    df_nuest = leer_cache(TABLA_NUESTRO_CACHE)

    comp_fil = df_comp[df_comp.apply(lambda x: query.lower() in str(x).lower(), axis=1)]
    nuest_fil = df_nuest[df_nuest.apply(lambda x: query.lower() in str(x).lower(), axis=1)]

    return {
        "query": query,
        "coincidencias_competencia": len(comp_fil),
        "coincidencias_nuestro": len(nuest_fil),
        "competencia_detalle": comp_fil.to_dict(orient="records"),
        "nuestro_detalle": nuest_fil.to_dict(orient="records")
    }
