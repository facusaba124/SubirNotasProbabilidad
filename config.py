# ============================================
# CONFIGURACIÓN GENERAL
# ============================================

# Ruta al archivo de credenciales
CREDENTIALS_FILE = "secrets/cargarnotasprobabilidad-9caca2f93f76.json"

# Scopes de Google
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Columnas donde comienzan las notas
COLUMNAS_BASE = {
    "Autoevaluaciones": 8,   # Columna H
    "Tareas": 4              # Columna D
}

# Color amarillo para notas 0
COLOR_AMARILLO = {
    "backgroundColor": {
        "red": 1.0,
        "green": 1.0,
        "blue": 0.6
    }
}