from difflib import get_close_matches

@app.get("/comparar_todo")
def comparar_todo():
    df_comp = leer_cache(TABLA_COMPETENCIA_CACHE)
    df_nuest = leer_cache(TABLA_NUESTRO_CACHE)

    # Normalizar nombres
    df_comp["nombre_norm"] = df_comp.astype(str).agg(" ".join, axis=1).str.lower()
    df_nuest["nombre_norm"] = df_nuest.astype(str).agg(" ".join, axis=1).str.lower()

    resultados = []

    for idx, row in df_nuest.iterrows():
        nombre = row["nombre_norm"]

        # Buscar coincidencia más cercana en competencia
        coincidencias = get_close_matches(nombre, df_comp["nombre_norm"], n=1, cutoff=0.45)

        if coincidencias:
            comp_row = df_comp[df_comp["nombre_norm"] == coincidencias[0]].iloc[0]
        else:
            comp_row = None

        resultados.append({
            "producto": row.to_dict(),
            "competencia": comp_row.to_dict() if comp_row is not None else None
        })

    return {
        "status": "ok",
        "productos_comparados": len(resultados),
        "detalle": resultados
    }
