import streamlit as st

from procesador import procesar_archivos, conectar_google
from settings import cargar_settings, guardar_settings


# ==========================================================
# CONFIGURACIÓN DE LA PÁGINA
# ==========================================================

st.set_page_config(
    page_title="Carga automática de notas",
    page_icon="📚",
    layout="centered"
)

settings = cargar_settings()

if "editando_url" not in st.session_state:
    st.session_state.editando_url = (
        settings["spreadsheet_url"] == ""
    )


# ==========================================================
# TÍTULO
# ==========================================================

st.title("📚 Carga automática de notas")

st.write(
    """
    Esta aplicación permite actualizar automáticamente las
    notas de Tareas y Autoevaluaciones en Google Sheets.
    """
)

st.divider()


# ==========================================================
# CONFIGURAR PLANILLA
# ==========================================================

st.subheader("Planilla de Google Sheets")

if st.session_state.editando_url:

    nueva_url = st.text_input(
        "URL de Google Sheets",
        value=settings["spreadsheet_url"]
    )

    col1, col2 = st.columns([1, 1])

    with col1:

        if st.button("💾 Guardar planilla"):

            if nueva_url.strip() == "":

                st.error("Debe ingresar una URL.")

            else:

                try:

                    gc = conectar_google()

                    sh = gc.open_by_url(nueva_url)

                    settings["spreadsheet_url"] = nueva_url
                    settings["spreadsheet_name"] = sh.title

                    guardar_settings(settings)

                    st.session_state.editando_url = False

                    st.success("Planilla configurada correctamente.")

                    st.rerun()

                except Exception as e:

                    st.error("No fue posible acceder a la planilla.")

                    st.exception(e)

else:

    st.success("Planilla configurada")

    st.info(
        f"**{settings['spreadsheet_name']}**"
    )

    if st.button("🔄 Cambiar planilla"):

        st.session_state.editando_url = True

        st.rerun()


st.divider()


# ==========================================================
# SELECCIÓN DE ARCHIVOS
# ==========================================================

archivos = st.file_uploader(
    "Seleccione uno o más archivos CSV",
    type=["csv"],
    accept_multiple_files=True
)

st.divider()


# ==========================================================
# BOTÓN DE ACTUALIZACIÓN
# ==========================================================

if st.button(
    "🚀 Actualizar notas",
    use_container_width=True
):

    if settings["spreadsheet_url"] == "":

        st.error(
            "Debe configurar primero una planilla."
        )

        st.stop()

    if not archivos:

        st.error(
            "Debe seleccionar al menos un archivo CSV."
        )

        st.stop()

    with st.spinner("Actualizando planilla..."):

        try:

            resultados = procesar_archivos(
                settings["spreadsheet_url"],
                archivos
            )

        except Exception as e:

            st.error("Ocurrió un error durante el procesamiento.")

            st.exception(e)

            st.stop()

    st.success("Proceso finalizado correctamente.")

    st.divider()

    total_actualizados = 0
    total_no_encontrados = 0

    for resultado in resultados:

        with st.container(border=True):

            st.subheader(resultado["archivo"])

            col1, col2 = st.columns(2)

            col1.metric(
                "Actualizados",
                resultado["actualizados"]
            )

            col2.metric(
                "No encontrados (nota 0)",
                resultado["no_encontrados"]
            )

            st.write(f"**Tipo:** {resultado['tipo']}")
            st.write(f"**Número:** {resultado['numero']}")

        total_actualizados += resultado["actualizados"]
        total_no_encontrados += resultado["no_encontrados"]

    st.divider()

    st.header("Resumen")

    col1, col2 = st.columns(2)

    col1.metric(
        "Total actualizados",
        total_actualizados
    )

    col2.metric(
        "Total nota 0",
        total_no_encontrados
    )