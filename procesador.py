import re

import gspread
import pandas as pd
from gspread_formatting import CellFormat, Color, format_cell_ranges
import streamlit as st
from google.oauth2.service_account import Credentials


from config import (
    SCOPES,
    COLUMNAS_BASE,
)


# ==========================================================
# CONEXIÓN CON GOOGLE
# ==========================================================

def conectar_google():
    creds_dict = st.secrets["google"]

    credentials = Credentials.from_service_account_info(
        creds_dict,
        scopes=SCOPES
    )

    return credentials


# ==========================================================
# DETECTAR TIPO Y NÚMERO
# ==========================================================

def detectar_tipo_y_numero(nombre_archivo):
    """
    Determina si el archivo corresponde a una Tarea o
    Autoevaluación y obtiene su número.
    """

    nombre = nombre_archivo.lower()

    if "tarea" in nombre:

        tipo = "Tareas"

        patron = r"tarea\s*(\d+)"

    elif (
        "autoevaluacion" in nombre
        or
        "autoevaluación" in nombre
    ):

        tipo = "Autoevaluaciones"

        patron = r"autoevaluaci[oó]n\s*(\d+)"

    else:

        raise ValueError(
            f"No se pudo determinar el tipo del archivo:\n{nombre_archivo}"
        )

    coincidencia = re.search(
        patron,
        nombre
    )

    if coincidencia is None:

        raise ValueError(
            f"No se pudo determinar el número del archivo:\n{nombre_archivo}"
        )

    numero = int(
        coincidencia.group(1)
    )

    return tipo, numero


# ==========================================================
# BUSCAR FIN DE ALUMNOS
# ==========================================================

def obtener_fin_datos(datos):
    """
    Devuelve la última fila que corresponde a estudiantes,
    evitando procesar las filas de resumen.
    """

    for fila, valores in enumerate(datos[1:], start=2):

        if len(valores) < 2:
            continue

        nombre = valores[1].strip().lower()

        if "tareas rendidas por tema" in nombre:

            return fila - 1

    return len(datos)
# ==========================================================
# ACTUALIZAR UN ARCHIVO
# ==========================================================

def actualizar_notas(worksheet, uploaded_file):

    nombre_archivo = uploaded_file.name

    tipo, numero = detectar_tipo_y_numero(nombre_archivo)

    uploaded_file.seek(0)

    df = pd.read_csv(uploaded_file)

    df.columns = [
        c.strip().lower()
        for c in df.columns
    ]

    # ---------------------------------------------
    # Buscar columnas
    # ---------------------------------------------

    try:

        mail_col = next(
            c for c in df.columns
            if "correo" in c or "mail" in c
        )

    except StopIteration:

        raise ValueError(
            f"{nombre_archivo}: no se encontró la columna de correo."
        )

    try:

        nota_col = next(
            c for c in df.columns
            if "calific" in c
        )

    except StopIteration:

        raise ValueError(
            f"{nombre_archivo}: no se encontró la columna de calificación."
        )

    # ---------------------------------------------
    # Leer hoja
    # ---------------------------------------------

    datos = worksheet.get_all_values()

    fin_datos = obtener_fin_datos(datos)

    mails = [
        fila[2].strip().lower()
        for fila in datos[1:fin_datos]
    ]

    columna = COLUMNAS_BASE[tipo] + numero - 1

    letra_columna = gspread.utils.rowcol_to_a1(
        1,
        columna
    )[:-1]

    notas = dict(
        zip(
            df[mail_col]
                .astype(str)
                .str.strip()
                .str.lower(),
            df[nota_col]
        )
    )

    valores = []

    rangos_amarillos = []

    actualizados = 0
    no_encontrados = 0

    for fila, mail in enumerate(
        mails,
        start=2
    ):

        if mail in notas:

            nota = notas[mail]

            actualizados += 1

        else:

            nota = 0

            no_encontrados += 1

            rangos_amarillos.append(
                f"{letra_columna}{fila}"
            )

        valores.append([nota])

    # ---------------------------------------------
    # Escritura por lotes
    # ---------------------------------------------

    worksheet.update(
        values=valores,
        range_name=f"{letra_columna}2:{letra_columna}{fin_datos}"
    )

    # ---------------------------------------------
    # Formato por lotes
    # ---------------------------------------------

    if rangos_amarillos:

        amarillo = CellFormat(
            backgroundColor=Color(
                1,
                1,
                0.6
            )
        )

        format_cell_ranges(
            worksheet,
            [
                (celda, amarillo)
                for celda in rangos_amarillos
            ]
        )

    return {

        "archivo": nombre_archivo,

        "tipo": tipo,

        "numero": numero,

        "actualizados": actualizados,

        "no_encontrados": no_encontrados

    }


# ==========================================================
# PROCESAR TODOS LOS ARCHIVOS
# ==========================================================

def procesar_archivos(
    spreadsheet_url,
    archivos
):

    gc = conectar_google()

    spreadsheet = gc.open_by_url(
        spreadsheet_url
    )

    worksheets = {

        "Tareas":
            spreadsheet.worksheet("Tareas"),

        "Autoevaluaciones":
            spreadsheet.worksheet("Autoevaluaciones")

    }

    resultados = []

    for archivo in archivos:

        tipo, _ = detectar_tipo_y_numero(
            archivo.name
        )

        worksheet = worksheets[tipo]

        resultado = actualizar_notas(
            worksheet,
            archivo
        )

        resultados.append(
            resultado
        )

    return resultados
