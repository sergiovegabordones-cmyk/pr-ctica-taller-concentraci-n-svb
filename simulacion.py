import numpy as np
from indicadores import (
    ratio_concentracion, 
    indice_herfindahl_hirschman, 
    indice_dominancia, 
    indice_entropia
)

def ejecutar_monte_carlo(n_empresas, n_iteraciones=1000, indicador='IHH', k=4):
    """
    Simula distribuciones aleatorias de cuotas de mercado usando Dirichlet
    y retorna el vector con los valores simulados del indicador.
    """
    # Parámetros simétricos para la distribución Dirichlet (suma de cuotas = 1.0)
    alpha = np.ones(n_empresas)
    simulaciones_cuotas = np.random.dirichlet(alpha, size=n_iteraciones)
    
    resultados = np.zeros(n_iteraciones)
    
    for i in range(n_iteraciones):
        s = simulaciones_cuotas[i]
        if indicador == 'CRk':
            resultados[i] = ratio_concentracion(s, k=k)
        elif indicador == 'IHH':
            resultados[i] = indice_herfindahl_hirschman(s)
        elif indicador == 'ID':
            resultados[i] = indice_dominancia(s)
        elif indicador == 'IE':
            resultados[i] = indice_entropia(s)
            
    return resultados
