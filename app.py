import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Carga de datos
df = pd.read_excel("datos_2006_2023.xlsx")

# Obtener la lista de cultivos únicos para el dropdown
cultivos_disponibles = sorted(df['CULTIVO'].unique())

# Título
st.title("Dashboard de Análisis de Cultivos en Colombia")
st.write("Seleccione un cultivo para visualizar sus estadísticas")

# Dropdown de cultivos
cultivo_seleccionado = st.selectbox(
    "Seleccione un Cultivo:",
    options=cultivos_disponibles,
    index=cultivos_disponibles.index('ARROZ')  # Valor predeterminado
)

# Filtrar datos por cultivo seleccionado
cultivo_df = df[df['CULTIVO'] == cultivo_seleccionado]

# Gráfico 1: Top 10 departamentos por área sembrada
top_10_departamentos = cultivo_df.groupby('DEPARTAMENTO')['Área Cosechada\n(ha)'].sum().nlargest(10)
fig1 = go.Figure(go.Bar(
    x=top_10_departamentos.index,
    y=top_10_departamentos.values,
    marker_color='#1f77b4'
))
fig1.update_layout(
    title=f'Top 10 Departamentos por Área Sembrada - {cultivo_seleccionado}',
    xaxis_title='Departamento',
    yaxis_title='Área Cosechada (ha)',
    template='plotly_white'
)

# Gráfico 2: Boxplot del rendimiento
fig2 = go.Figure(go.Box(
    y=cultivo_df['Rendimiento\n(t/ha)'],
    name='Rendimiento',
    marker_color='#ff7f0e'
))
fig2.update_layout(
    title=f'Distribución del Rendimiento - {cultivo_seleccionado}',
    yaxis_title='Rendimiento (t/ha)',
    template='plotly_white'
)

# Gráfico 3: Histórico de producción
cultivo_historico = cultivo_df.groupby('AÑO')['Producción\n(t)'].sum().reset_index()
fig3 = go.Figure(go.Scatter(
    x=cultivo_historico['AÑO'],
    y=cultivo_historico['Producción\n(t)'],
    mode='lines+markers',
    line=dict(color='#2ca02c', width=2),
    marker=dict(size=8)
))
fig3.update_layout(
    title=f'Histórico de Producción de {cultivo_seleccionado}',
    xaxis_title='Año',
    yaxis_title='Producción (t)',
    template='plotly_white'
)

# Gráfico 4: Gráfico de dispersión
fig4 = go.Figure(go.Scatter(
    x=cultivo_df['Área Cosechada\n(ha)'],
    y=cultivo_df['Rendimiento\n(t/ha)'],
    mode='markers',
    marker=dict(
        color='#d62728',
        size=10,
        opacity=0.7,
        line=dict(width=1)
    )
))
fig4.update_layout(
    title=f'Área Cosechada vs. Rendimiento - {cultivo_seleccionado}',
    xaxis_title='Área Cosechada (ha)',
    yaxis_title='Rendimiento (t/ha)',
    template='plotly_white'
)

# Mostrar los gráficos en la app de Streamlit
st.plotly_chart(fig1)
st.plotly_chart(fig2)
st.plotly_chart(fig3)
st.plotly_chart(fig4)

