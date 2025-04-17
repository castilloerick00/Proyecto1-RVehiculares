import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import os

# === CONFIGURACIÓN GENERAL ===
archivo_emisiones_sin_traci = "emissions1.xml"
archivo_emisiones_con_traci = "emissions_traci.xml"  # Descomentar si existe

graficar_emisiones = True
graficar_densidad = True
usar_zona = True  # Cambiar a True para filtrar por zona

#zona_interes = {
#    "zona_1": [
#        "337277957#0", "337277970", "40668087#5", "337277951",
#        "337277981", "567060342", "337277973", "337277984#0"
#    ]
#}

zona_interes = {
    "zona_1":[
    "337277973",
    "567060342",
    "553352498#4",
    "553352498#3",
    "553352498#2",
    "553352498#1",
    "553352498#0",
    "49217117",
    "337277957#6",
    "337277957#5",
    "337277957#4",
    "337277957#3",
    "337277957#2",
    "337277957#0",
    "337277970",
    "337277981",
    "337277951",
    "351440624#7",
    "351440624#6",
    "351440624#5",
    "351440624#4",
    "351440624#8",
    "49217115"
]
}


def leer_datos_streaming(archivo, zona=None):
    """Lee emisiones de CO2 y densidad vehicular usando streaming"""
    emisiones = {}
    densidad = {}
    
    contexto = ET.iterparse(archivo, events=("start", "end"))
    _, root = next(contexto)  # Obtener elemento root

    tiempo_actual = None
    co2_acumulado = 0.0
    vehiculos_acumulados = 0

    for evento, elem in contexto:
        if evento == "start" and elem.tag == "timestep":
            # Iniciar nuevo intervalo de tiempo
            tiempo_actual = float(elem.get("time"))
            co2_acumulado = 0.0
            vehiculos_acumulados = 0

        elif evento == "end" and elem.tag == "vehicle":
            # Procesar datos del vehículo
            lane = elem.get("lane", "").split("_")[0]
            if zona is None or lane in zona:
                co2_acumulado += float(elem.get("CO2", 0.0))
                vehiculos_acumulados += 1
            elem.clear()  # Liberar memoria inmediatamente

        elif evento == "end" and elem.tag == "timestep":
            # Finalizar intervalo de tiempo
            if tiempo_actual is not None:
                emisiones[tiempo_actual] = co2_acumulado
                densidad[tiempo_actual] = vehiculos_acumulados
            root.clear()  # Limpiar memoria acumulada

    return emisiones, densidad

# === EJECUCIÓN PRINCIPAL ===
zona_ids = list(zona_interes.values())[0] if usar_zona else None

try:
    # Cargar datos principales
    em_sin, d_sin = leer_datos_streaming(archivo_emisiones_sin_traci, zona_ids)
    
    # Para comparación (descomentar si hay datos de control)
    em_con, d_con = leer_datos_streaming(archivo_emisiones_con_traci, zona_ids)

except FileNotFoundError as e:
    print(f"Error: {str(e)}")
    exit(1)

# === GENERACIÓN DE GRÁFICOS ===
if graficar_emisiones:
    plt.figure(figsize=(12, 6))
    plt.plot(em_sin.keys(), em_sin.values(), 
             label="Sin control TraCI", 
             color='red', 
             linewidth=1)
    
    # Añadir comparación (descomentar si hay datos)
    plt.plot(em_con.keys(), em_con.values(), 
              label="Con control TraCI", 
              color='green',
              linewidth=1)
    
    plt.title(f"Emisiones de CO₂ ({'Zona crítica' if usar_zona else 'Global'})")
    plt.xlabel("Tiempo (s)")
    plt.ylabel("CO₂ acumulado (mg)")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()

if graficar_densidad:
    plt.figure(figsize=(12, 6))
    plt.plot(d_sin.keys(), d_sin.values(),
             label="Sin control TraCI",
             color='blue',
             linestyle='--',
             linewidth=1)
    
    # Añadir comparación (descomentar si hay datos)
    plt.plot(d_con.keys(), d_con.values(),
             label="Con control TraCI",
             color='orange',
             linewidth=1)
    
    plt.title(f"Densidad vehicular ({'Zona crítica' if usar_zona else 'Global'})")
    plt.xlabel("Tiempo (s)")
    plt.ylabel("Vehículos simultáneos")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()

plt.show()
