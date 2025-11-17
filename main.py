from fastapi import FastAPI
from google.oauth2.service_account import Credentials
import gspread
import pandas as pd
import os, json

app = FastAPI()

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

SHEETS = {
    "competencia": "https://docs.google.com/spreadsheets/d/1Uze_ajhdMESfiBdg85EwR_u3SDjA_xXwAKKGk1AU8bs/edit?usp=sharing",
    "nuestro": "https://docs.google.com/spreadsheets/d/1QV_9PtLKhHwD_2VLe2-KBmPPnA_jUx8BokmlyQz-pa8/edit?usp=sharing"
}

DATA_FOLDER = "data"
os.makedirs(DATA_FOLDER, exist_ok=True)


def cargar_credenciales():
    service_account_info = json.loads(os.environ["GOOGLE_CREDENTIALS"])
    return Credentials.from_service_account_info(service_account_info, scopes=SCOPES)


def descargar_sheet(nombre, url):
    """Descarga un Google Sheet y lo guarda en JSON local."""
    creds = cargar_credenciales()
    gc = gspread.authorize(creds)

    sh = gc.open_by_url(url)
    worksheet = sh.sheet1

    registros = worksheet.get_all_records()

    ruta = f"{DATA_FOLDER}/{nombre}.json"
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(registros, f, ensure_ascii=False, indent=2)

    return {"sheet": nombre, "filas": len(registros)}


@app.get("/")
def home():
    return {"status": "ok", "message": "API funcionando y datos locales listos."}


@app.get("/cron/actualizar")
def actualizar_todo():
    """Descarga los 2 Google Sheets y los guarda en JSON."""
    resultados = []
    for nombre, url in SHEETS.items():
        resultado = descargar_sheet(nombre, url)
        resultados.append(resultado)

    return {
        "status": "actualizado",
        "detalles": resultados
    }


@app.get("/data/{nombre}")
def leer_data(nombre: str):
    """Devuelve el JSON local ya procesado (rápido y liviano)."""
    ruta = f"{DATA_FOLDER}/{nombre}.json"

    if not os.path.exists(ruta):
        return {"error": f"No existe data local para '{nombre}'. Ejecutá /cron/actualizar"}

    with open(ruta, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data


@app.get("/comparar")
def comparar(item: str):
    """Compara un producto entre CMP (nuestro) y la competencia."""
    ruta_comp = f"{DATA_FOLDER}/competencia.json"
    ruta_nuest = f"{DATA_FOLDER}/nuestro.json"

    if not os.path.exists(ruta_comp) or not os.path.exists(ruta_nuest):
        return {"error": "Los datos no están actualizados. Ejecutá /cron/actualizar"}

    with open(ruta_comp, "r", encoding="utf-8") as f:
        comp = json.load(f)

    with open(ruta_nuest, "r", encoding="utf-8") as f:
        nuest = json.load(f)

    comp_filtrado = [fila for fila in comp if item.lower() in str(fila).lower()]
    nuest_filtrado = [fila for fila in nuest if item.lower() in str(fila).lower()]

    return {
        "item": item,
        "competencia": comp_filtrado,
        "nuestro": nuest_filtrado
    }


@app.get("/analizar")
def analizar(query: str):
    """Endpoint general para GPT: analiza un producto, categoría o texto."""
    ruta_comp = f"{DATA_FOLDER}/competencia.json"
    ruta_nuest = f"{DATA_FOLDER}/nuestro.json"

    with open(ruta_comp, "r", encoding="utf-8") as f:
        comp = json.load(f)

    with open(ruta_nuest, "r", encoding="utf-8") as f:
        nuest = json.load(f)

    comp_filtrado = [fila for fila in comp if query.lower() in str(fila).lower()]
    nuest_filtrado = [fila for fila in nuest if query.lower() in str(fila).lower()]

    return {
        "query": query,
        "cantidad_coincidencias_competencia": len(comp_filtrado),
        "cantidad_coincidencias_nuestro": len(nuest_filtrado),
        "competencia_detalle": comp_filtrado[:50],
        "nuestro_detalle": nuest_filtrado[:50]
    }
