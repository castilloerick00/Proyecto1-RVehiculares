import os
import sys
import traci

# Configurar la ruta de SUMO tools
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Por favor, declare la variable de entorno 'SUMO_HOME'")

# Iniciar la simulación con TraCI
sumoBinary = "sumo-gui"
sumoCmd = [
    sumoBinary,
    "-n", "network_centro.net.xml",
    "-r", "mapa1.rou.xml",
    "--additional-files", "vtypes.add.xml",
    "--emission-output", "emissions_traci.xml"
]
traci.start(sumoCmd)

# Lista de IDs de las calles donde se produce la congestión
congested_edges = [
    "337277973", "567060342", "553352498#4", "553352498#3", "553352498#2",
    "553352498#1", "553352498#0", "49217117", "337277957#6", "337277957#5",
    "337277957#4", "337277957#3", "337277957#2", "337277957#0", "337277970",
    "337277981", "337277951", "351440624#7", "351440624#6", "351440624#5",
    "351440624#4", "351440624#8", "49217115"
]

# Parámetros configurables
occupancy_threshold = 0.8  # Umbral de ocupación para ajuste de costos
cost_factor = 10           # Factor para aumentar el costo

# Diccionarios para rastrear costos y velocidades originales
edge_costs = {edge: None for edge in congested_edges}
original_speeds = {}       # Para almacenar velocidades originales de los carriles

# Banderas para activar/desactivar funcionalidades
enable_rerouting = True    # Cambiar a False para desactivar redireccionamiento y cambio de pesos
enable_speed_control = True  # Cambiar a False para desactivar control de velocidad

# Función para ajustar la velocidad basada en ocupación
def adjust_speed_based_on_occupancy(edge):
    lanes = traci.edge.getLaneNumber(edge)
    for lane_index in range(lanes):
        laneID = f"{edge}_{lane_index}"
        occupancy = traci.lane.getLastStepOccupancy(laneID)
        
        # Umbrales y factores de reducción
        if occupancy < 0.1:
            speed_factor = 1.0
        elif occupancy < 0.3:
            speed_factor = 0.6
        elif occupancy < 0.5:
            speed_factor = 0.4
        elif occupancy < 0.7:
            speed_factor = 0.2
        else:
            speed_factor = 0.1
        
        # Guardar la velocidad original si no está registrada
        if laneID not in original_speeds:
            original_speeds[laneID] = traci.lane.getMaxSpeed(laneID)
        
        # Calcular y aplicar la nueva velocidad
        new_speed = original_speeds[laneID] * speed_factor
        traci.lane.setMaxSpeed(laneID, new_speed)
        print(f"Step {step}: Ajustando velocidad del carril {laneID} a {new_speed} debido a ocupación {occupancy}")

# Bucle de simulación
step = 0
while traci.simulation.getMinExpectedNumber() > 0:
    traci.simulationStep()
    step += 1

    # Ajuste de costos (cambio de pesos) y redireccionamiento si rerouting está habilitado
    if enable_rerouting and step % 5 == 0:
        for edge in congested_edges:
            occupancy = traci.edge.getLastStepOccupancy(edge)
            if occupancy > occupancy_threshold:
                if edge_costs[edge] is None:
                    original_travel_time = traci.edge.getTraveltime(edge)
                    new_cost = original_travel_time * cost_factor
                    traci.edge.setEffort(edge, new_cost)
                    edge_costs[edge] = original_travel_time
                    print(f"Step {step}: Aumentando costo de la calle {edge} a {new_cost} debido a ocupación {occupancy}")
            else:
                if edge_costs[edge] is not None:
                    traci.edge.setEffort(edge, edge_costs[edge])
                    print(f"Step {step}: Restaurando costo original de la calle {edge} a {edge_costs[edge]}")
                    edge_costs[edge] = None

    # Redireccionamiento cada 60 pasos si está habilitado
    if enable_rerouting and step % 60 == 0:
        for vehID in traci.vehicle.getIDList():
            traci.vehicle.rerouteTraveltime(vehID)
            print(f"Step {step}: Redireccionando vehículo {vehID}")

    # Control de velocidad si está habilitado, entre pasos 3600 y 5400
    if enable_speed_control and 3600 <= step <= 5400 and step % 5 == 0:
        for edge in congested_edges:
            adjust_speed_based_on_occupancy(edge)

# Cerrar la simulación
traci.close()
