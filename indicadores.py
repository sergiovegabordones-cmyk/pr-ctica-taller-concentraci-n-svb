import numpy as np

def validar_cuotas(cuotas):
    """
    Valida que las cuotas de mercado estén en el intervalo [0, 100%]
    y que la suma total sea exactamente 1.0 (100%).
    """
    cuotas = np.array(cuotas, dtype=float)
    
    # Validar que no existan valores negativos ni mayores a 100
    if np.any(cuotas < 0) or np.any(cuotas > 100):
        raise ValueError("Las cuotas individuales deben estar dentro del intervalo [0, 100%].")
    
    # Si las cuotas vienen ingresadas en porcentaje (ej: 40 en vez de 0.4), normalizarlas
    if np.sum(cuotas) > 1.5:
        cuotas = cuotas / 100.0
        
    # Validar la condición de cierre de suma igual a 100% (1.0)
    if not np.isclose(np.sum(cuotas), 1.0, atol=1e-3):
        raise ValueError(f"La suma de las cuotas debe ser igual a 100% (Suma actual: {np.sum(cuotas)*100:.2f}%).")
        
    return cuotas

def ratio_concentracion(cuotas, k=4):
    """
    Calcula el Ratio de Concentración CR_k (Suma de las k mayores cuotas).
    """
    cuotas = validar_cuotas(cuotas)
    cuotas_ordenadas = np.sort(cuotas)[::-1]
    return float(np.sum(cuotas_ordenadas[:k]))

def indice_herfindahl_hirschman(cuotas):
    """
    Calcula el Índice de Herfindahl-Hirschman (IHH).
    Escala estándar de 0 a 10,000 puntos.
    """
    cuotas = validar_cuotas(cuotas)
    return float(np.sum((cuotas * 100) ** 2))

def indice_dominancia(cuotas):
    """
    Calcula el Índice de Dominancia (ID).
    """
    cuotas = validar_cuotas(cuotas)
    ihh = np.sum(cuotas ** 2)
    if ihh == 0:
        return 0.0
    return float(np.sum((cuotas ** 4) / (ihh ** 2)))

def indice_entropia(cuotas):
    """
    Calcula el Índice de Entropía (IE).
    """
    cuotas = validar_cuotas(cuotas)
    # Filtrar cuotas mayores a 0 para evitar logaritmo de cero
    cuotas_pos = cuotas[cuotas > 0]
    return float(np.sum(cuotas_pos * np.log(1.0 / cuotas_pos)))
