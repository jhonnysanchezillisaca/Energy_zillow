from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import pandas as pd
from rapidfuzz import process, fuzz
import os
from openai import OpenAI

# Importamos tus funciones personalizadas
import Funciones as f

app = FastAPI(
    title="Energy Dashboard API",
    description="API para búsqueda de edificios, predicciones de multas y recomendaciones energéticas."
)

# =========================================================
# CARGA DE DATOS (Se ejecuta al iniciar la API)
# =========================================================
try:
    df_basic = pd.read_csv("basic_information.csv")
    df_basic.columns = df_basic.columns.str.strip()
except Exception as e:
    print(f"Error cargando basic_information.csv: {e}")
    df_basic = pd.DataFrame()

# =========================================================
# HELPERS BÁSICOS
# =========================================================
def normalizar_texto(s):
    s = str(s).lower().strip()
    return s.replace("avenue", "ave").replace("street", "st").replace("road", "rd").replace("boulevard", "blvd")

def asegurar_dict(resultado):
    """Convierte series de Pandas, DataFrames o tipos NumPy a diccionarios nativos de Python."""
    if resultado is None:
        return {}
    if isinstance(resultado, pd.Series):
        # El truco es pasarlo por JSON o usar tipos nativos para limpiar int64/float64
        return {k: (int(v) if isinstance(v, (pd.Int64Dtype, type(pd.NA))) else v) for k, v in resultado.fillna("").to_dict().items()}
    if isinstance(resultado, pd.DataFrame):
        if resultado.empty:
            return {}
        return resultado.iloc[0].fillna("").to_dict()
    if isinstance(resultado, dict):
        return resultado
    return {}

# =========================================================
# ENDPOINTS (RUTAS DE LA API)
# =========================================================

@app.get("/")
def inicio():
    return {"mensaje": "Energy Dashboard API funcionando. Visita /docs para probarla."}


@app.get("/api/v1/search")
def buscar_edificio(address: str = Query(..., description="Dirección del edificio a buscar")):
    """
    Busca un edificio por dirección y devuelve toda su información agrupada:
    Datos básicos, predicciones de multas, combustibles y futuro.
    """
    if df_basic.empty:
        raise HTTPException(status_code=500, detail="Base de datos no disponible.")

    # 1. Búsqueda difusa (Fuzzy matching)
    direcciones1_norm = [normalizar_texto(d) for d in df_basic.get("address", pd.Series()).fillna("").astype(str)]
    direcciones2_norm = [normalizar_texto(d) for d in df_basic.get("Address 1", pd.Series()).fillna("").astype(str)]
    direccion_norm = normalizar_texto(address)

    res1 = process.extractOne(direccion_norm, direcciones1_norm, scorer=fuzz.WRatio)
    res2 = process.extractOne(direccion_norm, direcciones2_norm, scorer=fuzz.WRatio)

    mejor = max([r for r in [res1, res2] if r is not None], key=lambda x: x[1], default=None)

    if not mejor or mejor[1] < 60: # Umbral de similitud
        raise HTTPException(status_code=404, detail="No se encontró ningún edificio con esa dirección.")

    idx_final = mejor[2]
    bbl = int(df_basic["BBL"].iloc[idx_final])

    # 2. Extraer datos con tus funciones
    try:
        data_info = asegurar_dict(f.display_information(2024, bbl))
        data_pred = asegurar_dict(f.display_predictions(2024, bbl))
        data_fuel = asegurar_dict(f.display_fuels(2024, bbl))
        
        # Para el dataframe futuro, lo convertimos a una lista de diccionarios
        df_future = f.display_future(bbl)
        data_future = df_future.to_dict(orient="records") if not df_future.empty else []

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar los datos del BBL {bbl}: {str(e)}")

    # 3. Retornar el JSON estructurado
    return {
        "bbl_encontrado": bbl,
        "informacion_general": data_info,
        "predicciones": data_pred,
        "combustibles": data_fuel,
        "consumo_futuro": data_future
    }


@app.get("/api/v1/recommendations/{bbl}")
def obtener_recomendaciones(bbl: str):
    """
    Genera 5 recomendaciones de eficiencia usando ChatGPT para un BBL específico.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="La variable de entorno OPENAI_API_KEY no está configurada.")

    client = OpenAI(api_key=api_key)

    try:
        # Obtenemos los datos necesarios para el prompt
        data = asegurar_dict(f.display_information(2024, bbl))
        data_pred = asegurar_dict(f.display_predictions(2024, bbl))
        data_fuel = asegurar_dict(f.display_fuels(2024, bbl))

        prompt = f"""
        You are an expert building energy efficiency consultant.
        Based ONLY on the following building data, generate exactly 5 concrete improvement recommendations.
        The recommendations must be practical, specific, and related to emissions, penalties,
        fuels, ENERGY STAR, and regulatory compliance.

        Building data:
        - Name: {data.get("Property Name", "N/A")}
        - Calculated emissions: {data.get("Emisiones Calculadas", "N/A")}
        - Emissions limit: {data.get("Limite", "N/A")}
        - Current penalty: {data.get("multa", "N/A")}
        - Estimated penalty 2030: {data_pred.get("multa 2030", "N/A")}
        - Electricity: {data_fuel.get("Electricity", "N/A")}
        - Natural Gas: {data_fuel.get("Natural Gas", "N/A")}
        - Fuel Oil: {data_fuel.get("Fuel Oil", "N/A")}

        The recommendations must include: expected impact on emissions, relation to penalties reduction, level of investment, and implementation difficulty.
        Return the answer in English, as a numbered list from 1 to 5.
        """

        respuesta = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert in building energy efficiency and decarbonization."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4
        )

        return {"bbl": bbl, "recomendaciones": respuesta.choices[0].message.content}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar recomendaciones: {str(e)}")