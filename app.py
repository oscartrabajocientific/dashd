import streamlit as st
import pandas as pd
import plotly.graph_objects as go
# No necesitas 'make_subplots' si no lo usas explícitamente para crear la figura inicial.
# No necesitas Dash, dcc, html, Input, Output, dash_bootstrap_components

# --- Configuración de la Página (Opcional pero recomendado) ---
st.set_page_config(
    page_title="Dashboard de Cultivos Colombia",
    page_icon="🌱", # Puedes usar un emoji o una URL a un favicon
    layout="wide" # Usa el ancho completo de la página
)

# --- Carga de Datos ---
# Función para cargar datos (mejor práctica para usar el caché de Streamlit)
# @st.cache_data asegura que los datos se carguen solo una vez, mejorando el rendimiento.
@st.cache_data
def load_data(url):
    """Carga los datos desde una URL (GitHub Raw Link)."""
    try:
        # Asegúrate de que la URL apunte al archivo "raw" en GitHub
        # Ejemplo: https://raw.githubusercontent.com/tu_usuario/tu_repo/main/datos.xlsx
        df = pd.read_excel(url)
        # Limpieza básica de nombres de columna (opcional pero útil)
        df.columns = df.columns.str.strip() # Quita espacios al inicio/final
        df.columns = df.columns.str.replace('\n', ' ', regex=False) # Reemplaza saltos de línea
        return df
    except Exception as e:
        st.error(f"Error al cargar los datos desde la URL: {e}")
        st.error(f"Verifica que la URL sea correcta y apunte al archivo 'raw': {url}")
        return None # Devuelve None si hay error

# --- Interfaz de Usuario y Lógica Principal ---

st.title("📊 Dashboard de Análisis de Cultivos en Colombia (2006-2023)")
st.markdown("Selecciona un cultivo para visualizar sus estadísticas anuales y departamentales.")

# --- Barra Lateral para Filtros ---
st.sidebar.header("Filtros")

# URL del archivo Excel en GitHub (¡DEBES REEMPLAZAR ESTA URL!)
# 1. Ve a tu repositorio en GitHub.
# 2. Navega hasta el archivo .xlsx.
# 3. Haz clic en el botón "Raw".
# 4. Copia la URL de esa página "Raw".
github_raw_url = "https://raw.githubusercontent.com/oscartrabajocientific/dashd/main/datos.xlsx" # <--- ¡REEMPLAZA ESTO!

# Cargar los datos usando la función
df = load_data(github_raw_url)

# Verifica si la carga de datos fue exitosa antes de continuar
if df is not None:
    # --- Selección de Cultivo ---
    cultivos_disponibles = sorted(df['CULTIVO'].unique())
    # Usa st.selectbox para el menú desplegable en la barra lateral
    cultivo_seleccionado = st.sidebar.selectbox(
        "Selecciona un Cultivo:",
        options=cultivos_disponibles,
        index=cultivos_disponibles.index('ARROZ') if 'ARROZ' in cultivos_disponibles else 0 # Valor predeterminado 'ARROZ' si existe
    )

    # --- Filtrar Datos ---
    # Filtra el DataFrame basado en la selección del usuario
    # Esto ocurre automáticamente cada vez que el usuario cambia la selección en Streamlit
    cultivo_df = df[df['CULTIVO'] == cultivo_seleccionado].copy() # Usar .copy() para evitar SettingWithCopyWarning

    # --- Mostrar KPIs o Información Resumida (Opcional) ---
    st.subheader(f"Resumen para: {cultivo_seleccionado}")
    total_produccion = cultivo_df['Producción (t)'].sum()
    area_promedio = cultivo_df['Área Cosechada (ha)'].mean()
    rendimiento_promedio = cultivo_df['Rendimiento (t/ha)'].mean()

    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Producción Total (t)", f"{total_produccion:,.0f}")
    kpi2.metric("Área Cosechada Promedio (ha)", f"{area_promedio:,.1f}")
    kpi3.metric("Rendimiento Promedio (t/ha)", f"{rendimiento_promedio:,.2f}")

    st.markdown("---") # Separador visual

    # --- Creación de Gráficos (usando la lógica de Plotly que ya tenías) ---

    # Dividir la página en columnas para los gráficos
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top 10 Departamentos por Área Cosechada")
        # Gráfico 1: Top 10 departamentos por área cosechada (cambiado de 'sembrada')
        top_10_departamentos = cultivo_df.groupby('DEPARTAMENTO')['Área Cosechada (ha)'].sum().nlargest(10)
        if not top_10_departamentos.empty:
            fig1 = go.Figure(go.Bar(
                x=top_10_departamentos.index,
                y=top_10_departamentos.values,
                marker_color='#1f77b4',
                name='Área Cosechada'
            ))
            fig1.update_layout(
                # title=f'Top 10 Departamentos por Área Cosechada - {cultivo_seleccionado}', # Título ya está como subheader
                xaxis_title='Departamento',
                yaxis_title='Área Cosechada (ha)',
                template='plotly_white',
                height=400 # Ajustar altura si es necesario
            )
            # Mostrar gráfico en Streamlit
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.warning("No hay suficientes datos departamentales para mostrar este gráfico.")


        st.subheader("Histórico de Producción Anual")
        # Gráfico 3: Histórico de producción
        cultivo_historico = cultivo_df.groupby('AÑO')['Producción (t)'].sum().reset_index()
        if not cultivo_historico.empty:
            fig3 = go.Figure(go.Scatter(
                x=cultivo_historico['AÑO'],
                y=cultivo_historico['Producción (t)'],
                mode='lines+markers',
                line=dict(color='#2ca02c', width=2),
                marker=dict(size=8),
                name='Producción'
            ))
            fig3.update_layout(
                # title=f'Histórico de Producción de {cultivo_seleccionado}',
                xaxis_title='Año',
                yaxis_title='Producción (t)',
                template='plotly_white',
                 height=400 # Ajustar altura si es necesario
            )
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.warning("No hay suficientes datos históricos para mostrar este gráfico.")

    with col2:
        st.subheader("Distribución del Rendimiento")
        # Gráfico 2: Boxplot del rendimiento
        if not cultivo_df['Rendimiento (t/ha)'].dropna().empty:
            fig2 = go.Figure(go.Box(
                y=cultivo_df['Rendimiento (t/ha)'],
                name='Rendimiento',
                marker_color='#ff7f0e'
            ))
            fig2.update_layout(
                # title=f'Distribución del Rendimiento - {cultivo_seleccionado}',
                yaxis_title='Rendimiento (t/ha)',
                template='plotly_white',
                height=400 # Ajustar altura si es necesario
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
             st.warning("No hay datos de rendimiento para mostrar este gráfico.")


        st.subheader("Relación Área Cosechada vs. Rendimiento")
        # Gráfico 4: Gráfico de dispersión
        if not cultivo_df[['Área Cosechada (ha)', 'Rendimiento (t/ha)']].dropna().empty:
            fig4 = go.Figure(go.Scatter(
                x=cultivo_df['Área Cosechada (ha)'],
                y=cultivo_df['Rendimiento (t/ha)'],
                mode='markers',
                marker=dict(
                    color='#d62728',
                    size=10,
                    opacity=0.7,
                    line=dict(width=1)
                ),
                text=cultivo_df['DEPARTAMENTO'], # Mostrar departamento en hover (opcional)
                name='Registros'
            ))
            fig4.update_layout(
                # title=f'Área Cosechada vs. Rendimiento - {cultivo_seleccionado}',
                xaxis_title='Área Cosechada (ha)',
                yaxis_title='Rendimiento (t/ha)',
                template='plotly_white',
                height=400 # Ajustar altura si es necesario
            )
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.warning("No hay suficientes datos para mostrar el gráfico de dispersión.")

    # --- Mostrar Tabla de Datos Filtrados (Opcional) ---
    st.markdown("---")
    st.subheader(f"Datos Detallados para {cultivo_seleccionado}")
    # Muestra el dataframe filtrado, puedes limitar las columnas si quieres
    st.dataframe(cultivo_df[['AÑO', 'DEPARTAMENTO', 'MUNICIPIO', 'Área Sembrada (ha)', 'Área Cosechada (ha)', 'Producción (t)', 'Rendimiento (t/ha)']].reset_index(drop=True))

else:
    st.warning("No se pudieron cargar los datos. Verifica la URL de GitHub y la conexión.")

# --- Pie de Página (Opcional) ---
st.markdown("---")
st.markdown("Dashboard creado con Streamlit y Plotly.")

