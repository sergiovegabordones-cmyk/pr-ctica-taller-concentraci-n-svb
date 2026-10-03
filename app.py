import streamlit as st
import numpy as np
import plotly.figure_factory as ff
import plotly.graph_objects as go

from indicadores import (
    ratio_concentracion, 
    indice_herfindahl_hirschman, 
    indice_dominancia, 
    indice_entropia,
    validar_cuotas
)
from simulacion import ejecutar_monte_carlo

st.set_page_config(page_title="Simulador de Concentración de Mercado", layout="wide")

st.title("📊 Simulador y Evaluador de Concentración de Mercado")
st.markdown("Herramienta de análisis estocástico de Monte Carlo para Organización Industrial.")

# Sidebar - Configuración
st.sidebar.header("Configuración de Simulación")

indicador_sel = st.sidebar.selectbox(
    "Selecciona el Indicador",
    ["IHH", "CRk", "ID", "IE"]
)

k_val = 4
if indicador_sel == "CRk":
    k_val = st.sidebar.slider("Valor de k para CR_k", 1, 10, 4)

n_empresas = st.sidebar.slider("Número de Empresas (N)", min_value=2, max_value=100, value=10)

n_iter = st.sidebar.number_input(
    "Número de Iteraciones de Monte Carlo", 
    min_value=100, 
    max_value=50000, 
    value=1000, 
    step=500
)

# Advertencia de Carga Computacional
if n_iter > 10000 or n_empresas > 50:
    st.sidebar.warning("⚠️ **Advertencia de Carga Computacional:** Procesar un alto volumen de iteraciones o un N elevado puede aumentar el tiempo de respuesta y la latencia del servidor.")

# Ejecución de Monte Carlo
simulaciones = ejecutar_monte_carlo(n_empresas, n_iter, indicador_sel, k_val)

# Definición del Caso Particular
st.subheader("📌 Definición del Caso Particular")
col1, col2 = st.columns(2)

with col1:
    modo_ingreso = st.radio("Modo de definición de cuotas:", ["Aleatoria Puntual", "Entrada Manual"])

cuotas_caso = []

if modo_ingreso == "Aleatoria Puntual":
    if st.button("Generar Cuotas Aleatorias"):
        cuotas_caso = np.random.dirichlet(np.ones(n_empresas))
    else:
        cuotas_caso = np.random.dirichlet(np.ones(n_empresas))
else:
    input_text = st.text_input(f"Ingresa {n_empresas} cuotas separadas por coma (ej: 40, 30, 20, 10):")
    if input_text:
        try:
            cuotas_caso = [float(x.strip()) for x in input_text.split(",")]
            if len(cuotas_caso) != n_empresas:
                st.error(f"Debes ingresar exactamente {n_empresas} cuotas.")
                cuotas_caso = []
        except:
            st.error("Asegúrate de ingresar solo números separados por coma.")

if len(cuotas_caso) > 0:
    try:
        cuotas_caso = validar_cuotas(cuotas_caso)
        
        # Calcular indicador particular
        if indicador_sel == "CRk":
            val_caso = ratio_concentracion(cuotas_caso, k_val)
        elif indicador_sel == "IHH":
            val_caso = indice_herfindahl_hirschman(cuotas_caso)
        elif indicador_sel == "ID":
            val_caso = indice_dominancia(cuotas_caso)
        elif indicador_sel == "IE":
            val_caso = indice_entropia(cuotas_caso)
            
        percentil = (simulaciones < val_caso).mean() * 100
        
        # Gráfica Comparativa con Plotly
        st.subheader("📈 Distribución Empírica vs. Caso Particular")
        
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=simulaciones, 
            histnorm='probability density',
            name='Simulación Monte Carlo',
            marker_color='#1f77b4',
            opacity=0.6
        ))
        
        fig.add_vline(
            x=val_caso, 
            line_width=3, 
            line_dash="dash", 
            line_color="red",
            annotation_text=f"Caso Particular: {val_caso:.2f} (Percentil {percentil:.1f}%)",
            annotation_position="top right"
        )
        
        fig.update_layout(
            title=f"Distribución del Indicador {indicador_sel} (N={n_empresas}, Iteraciones={n_iter})",
            xaxis_title=f"Valor del Indicador ({indicador_sel})",
            yaxis_title="Densidad de Probabilidad",
            hovermode="x unified"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Módulo Evaluador Interactiva
        st.subheader("🎓 Módulo Evaluador y Retroalimentación Pedagógica")
        
        opcion_resp = st.radio(
            f"Según los umbrales teóricos, ¿cómo clasificarías la concentración del mercado para este caso particular ({indicador_sel} = {val_caso:.2f})?",
            ["Baja Concentración / Mercado Competitivo", "Concentración Moderada", "Alta Concentración / Mercado Concentrado"]
        )
        
        if st.button("Validar Respuesta"):
            # Evaluación con base en IHH estándar
            if indicador_sel == "IHH":
                if val_caso < 1500:
                    correcta = "Baja Concentración / Mercado Competitivo"
                    explicacion = "El IHH es menor a 1,500 puntos, lo que indica un mercado desconcentrado y competitivo según los estándares internacionales de libre competencia."
                elif 1500 <= val_caso <= 2500:
                    correcta = "Concentración Moderada"
                    explicacion = "El IHH está entre 1,500 y 2,500 puntos, correspondiente a un mercado moderadamente concentrado."
                else:
                    correcta = "Alta Concentración / Mercado Concentrado"
                    explicacion = "El IHH supera los 2,500 puntos, identificando un mercado altamente concentrado."
            else:
                if percentil < 33:
                    correcta = "Baja Concentración / Mercado Competitivo"
                elif 33 <= percentil <= 66:
                    correcta = "Concentración Moderada"
                else:
                    correcta = "Alta Concentración / Mercado Concentrado"
                explicacion = f"Comparado contra las {n_iter} simulaciones estocásticas, este mercado se ubica en el percentil {percentil:.1f}% de la distribución empírica."
                
            if opcion_resp == correcta:
                st.success(f"¡Correcto! 🎉 {explicacion}")
            else:
                st.error(f"Incorrecto. La clasificación adecuada es **{correcta}**. {explicacion}")
                
    except Exception as e:
        st.error(f"Error al procesar las cuotas del caso particular: {e}")
        