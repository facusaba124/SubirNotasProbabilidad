import re

import pandas as pd
import gspread

from google.oauth2.service_account import Credentials

from config import (
    CREDENTIALS_FILE,
    SCOPES,
    COLUMNAS_BASE,
    COLOR_AMARILLO
)


# ==========================================================
# CONEXIÓN CON GOOGLE
# ==========================================================

def conectar_google():
    """
    Devuelve un cliente autenticado de Google Sheets.
    """

    creds = Credentials.from_service_account_file(
        CREDENTIALS_FILE,
        scopes=SCOPES
    )

    return gspread.authorize(creds)


# ==========================================================
# DETECTAR TIPO Y NÚMERO
# ==========================================================

def detectar_tipo_y_numero(nombre_archivo):

    nombre = nombre_archivo.lower()

    if "tarea" in nombre:

        tipo = "Tareas"

        match = re.search(
            r"tarea\s*(\d+)",
            nombre
        )

    elif (
        "autoevaluación" in nombre
        or
        "autoevaluacion" in nombre
    ):

        tipo = "Autoevaluaciones"

        match = re.search(
            r"autoevaluaci[oó]n\s*(\d+)",
            nombre
        )

    else:

        raise ValueError(
            f"No se pudo determinar el tipo del archivo:\n{nombre_archivo}"
        )

    if match is None:

        raise ValueError(
            f"No se pudo determinar el número del archivo:\n{nombre_archivo}"
        )

    numero = int(match.group(1))

    return tipo, numero


# ==========================================================
# BUSCAR FIN DE ALUMNOS
# ==========================================================

def obtener_fin_datos(datos):

    for fila, valores in enumerate(datos[1:], start=2):

        if len(valores) > 1:

            nombre = valores[1].strip().lower()

            if "tareas rendidas por tema" in nombre:

                return fila - 1

    return len(datos)


# ==========================================================
# ACTUALIZAR UN ARCHIVO
# ==========================================================

def actualizar_notas(gc, spreadsheet_url, uploaded_file):

    nombre_archivo = uploaded_file.name

    tipo, numero = detectar_tipo_y_numero(
        nombre_archivo
    )

    # ---------------------------------------------
    # Leer CSV
    # ---------------------------------------------

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

            if (
                "correo" in c
                or
                "mail" in c
            )

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
    # Abrir hoja
    # ---------------------------------------------

    sh = gc.open_by_url(
        spreadsheet_url
    )

    worksheet = sh.worksheet(
        tipo
    )

    datos = worksheet.get_all_values()

    fin_datos = obtener_fin_datos(
        datos
    )

    mails = [

        fila[2].strip().lower()

        for fila in datos[1:fin_datos]

    ]

    columna = (
        COLUMNAS_BASE[tipo]
        +
        numero
        -
        1
    )

    notas = dict(

        zip(

            df[mail_col]
            .astype(str)
            .str.strip()
            .str.lower(),

            df[nota_col]

        )

    )

    actualizados = 0
    no_encontrados = 0

    # ---------------------------------------------
    # Escribir notas
    # ---------------------------------------------

    for indice, mail in enumerate(
        mails,
        start=2
    ):

        if mail in notas:

            nota = notas[mail]

            actualizados += 1

        else:

            nota = 0

            no_encontrados += 1

        worksheet.update_cell(
            indice,
            columna,
            nota
        )

        if nota == 0:

            letra = chr(
                64 + columna
            )

            worksheet.format(

                f"{letra}{indice}",

                COLOR_AMARILLO

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

    resultados = []

    for archivo in archivos:

        resultados.append(

            actualizar_notas(

                gc,

                spreadsheet_url,

                archivo

            )

        )

    return resultados