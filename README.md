# 🌆 Simulación de Control Inteligente de Emisiones de CO₂ en el Centro de Cuenca

Este proyecto de simulación busca modelar el tráfico y controlar dinámicamente las emisiones de CO₂ en el centro histórico de Cuenca, Ecuador. A través del simulador SUMO y control inteligente con TraCI, se generan escenarios realistas de congestión y se aplican estrategias de mitigación sin intervenir los semáforos.

---

## 📁 Estructura del proyecto

```
📁 Proyecto1-RVehiculares
├── 📂 Control
│   └── control_inteligente_trafico.py
├── 📂 Escenario
│   ├── crear_trips.sh
│   ├── modificar_rutas_buses.py
│   └── modificar_rutas.py
├── 📂 Resultados
│   ├── grafico_co2.py
│   └── previo.py
└── README.md
```



---

## 📂 1. Escenario

### `crear_trips.sh`
Genera tráfico aleatorio en la red del centro de Cuenca.  
**Entrada:** `mapa.net.xml`, `vtypes.add.xml`  
**Salida:** `mapa.rou.xml`  
✔️ Añade vehículos como autos, buses, motos (varias marcas y tipos).

### `modificar_rutas_buses.py`
Redefine rutas más realistas para buses urbanos.  
**Entrada:** `mapa.rou.xml`, `mapa.net.xml`  
**Salida:** `mapa_buses_modificado.rou.xml`  
✔️ Permite definir el porcentaje de buses con rutas definidas.

### `modificar_rutas.py`
Define rutas realistas para el resto de vehículos.  
**Entrada:** `mapa_buses_modificado.rou.xml`, `mapa.net.xml`  
**Salida:** `mapa_modificado.rou.xml`  
✔️ Permite establecer zonas congestionadas y porcentaje de redirección en horas pico.  
✔️ No afecta las rutas ya definidas para los buses.

---

## 🧠 2. Control

### `control_inteligente_trafico.py`
Aplica control de tráfico inteligente con TraCI.  
**Entrada:** `mapa_modificado.rou.xml`, `mapa.net.xml`, `vtypes.add.xml`  
**Salida:** `emissions_traci.xml`  
✔️ Control dinámico del **coste de edges congestionados**  
✔️ Control dinámico de **velocidad máxima por edge**  
✔️ El usuario puede seleccionar el porcentaje de aplicación para cada estrategia.

---

## 📊 3. Resultados

### `grafico_co2.py`
Genera gráficos de emisiones de CO₂ y densidad vehicular.  
**Entrada:** `emissions.xml`, `emissions_traci.xml`  
✔️ Puede analizar todo el mapa o una zona específica de congestión mediante lista de edges.

### `previo.py`
Filtra los archivos `emissions.xml` o `emissions_traci.xml` para generar estructuras tipo `edgedata.xml`.  
**Entrada:** archivo de emisiones  
**Salida:** `emissions_0_10800.xml`, `emissions_3600_5400.xml`  
✔️ Permite seleccionar el intervalo de tiempo a analizar:
- `0–10800` segundos (toda la simulación)
- `3600–5400` segundos (hora pico)

---

## 🗺️ Visualización de mapa de calor

Una vez generado el archivo filtrado, puedes usar `plot_net_dump.py` de SUMO para visualizar el mapa de calor:

```bash
python3 /opt/sumo/tools/visualization/plot_net_dump.py \
    -v \
    -n network_centro.net.xml \
    --measures CO2,CO2 \
    -i emissions_0_10800.xml,emissions_0_10800.xml \
    --xlabel [m] --ylabel [m] \
    --default-width .5 --min-width .5 --max-width 3 \
    --xlim 9250,12580 --ylim 7000,9400 \
    --colormap plasma \
    --color-bar-label "CO₂ (mg)" \
    -o co2_0_10800_map.png
```

---

## 🎓 Créditos académicos

**Universidad de Cuenca**  
Facultad de Ingeniería  
Ingeniería en Telecomunicaciones  
Asignatura: Redes Vehiculares  

**Autores:**  
- Erick Castillo  
- Sebastián Chalco  
- Felipe Palaguachi
