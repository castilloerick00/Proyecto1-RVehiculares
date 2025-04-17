import xml.etree.ElementTree as ET
import random
import sumolib

# Archivos
input_file = "mapa.rou.xml"
output_file = "mapa_modificado.rou.xml"
net_file = "network_centro.net.xml"
percentage = 50

# Edges de inicio y fin
start_edges = ["375081257#0", "42143918#0"]
end_edges = ["400051329#4", "42143918#13"]

# Combinaciones posibles
route_combinations = [
    #(start_edges[0], end_edges[0]),
    (start_edges[0], end_edges[1]),
    (start_edges[1], end_edges[0])#,
    #(start_edges[1], end_edges[1])
]
#route_weights = [1, 0.25, 0.25, 0.25]
route_weights = [0.5, 0.5]

# Definir zonas y pesos personalizados (asegúrate de que sumen 1.0)
zonas = [
    ["337277957#0", "337277970", "40668087#5", "337277951", "337277981", "567060342", "337277973", "337277984#0"],
    ["552651836", "492470515", "399285450#1", "399285450#0", "518706138#1", "48202933", "399285450#2", "492443599#1"],
    ["400051329#1", "39525772#0", "35287032#7", "400051329#0", "39525772#1", "35287032#6", "402191987#6", "402191987#5"]
]
zona_weights = [0.4, 0.3, 0.3]  # ← Puedes personalizar estos valores

# Leer red de SUMO
net = sumolib.net.readNet(net_file)

# Parsear archivo XML
tree = ET.parse(input_file)
root = tree.getroot()
vehicles = root.findall("vehicle")
total_vehicles = len(vehicles)
print(f"Total de vehículos en {input_file}: {total_vehicles}")

# Selección de vehículos a modificar
num_to_modify = int(total_vehicles * percentage / 100)
vehicles_to_modify = random.sample(vehicles, num_to_modify)
print(f"Modificando {num_to_modify} vehículos.")

# Función para encontrar ruta más corta entre dos edges
def get_path(net, start, end):
    try:
        start_edge = net.getEdge(start)
        end_edge = net.getEdge(end)
        path, _ = net.getShortestPath(start_edge, end_edge)
        return [edge.getID() for edge in path] if path else None
    except Exception as e:
        print(f"Error buscando ruta entre {start} y {end}: {e}")
        return None

# Modificar rutas
for vehicle in vehicles_to_modify:
    depart = float(vehicle.get("depart", "0"))
    start_edge, end_edge = random.choices(route_combinations, weights=route_weights, k=1)[0]

    if 2000 <= depart <= 4000:
        # Elegir zona y edge intermedio según pesos
        zona = random.choices(zonas, weights=zona_weights, k=1)[0]
        edge_intermedio = random.choice(zona)

        # Obtener rutas parciales
        ruta1 = get_path(net, start_edge, edge_intermedio)
        ruta2 = get_path(net, edge_intermedio, end_edge)

        if ruta1 and ruta2:
            full_route = ruta1 + ruta2[1:]
        else:
            print(f"Vehículo {vehicle.get('id')}: no se pudo generar ruta pasando por zona.")
            continue
    else:
        # Ruta directa sin paso por zona
        full_route = get_path(net, start_edge, end_edge)

    if full_route:
        route_element = vehicle.find("route")
        if route_element is not None:
            route_element.set("edges", " ".join(full_route))
        else:
            ET.SubElement(vehicle, "route", edges=" ".join(full_route))
        print(f"Vehículo {vehicle.get('id')} actualizado. Ruta: {' '.join(full_route)}")
    else:
        print(f"No se encontró ruta válida para vehículo {vehicle.get('id')}.")

# Guardar archivo
tree.write(output_file, encoding="UTF-8", xml_declaration=True)
print(f"Archivo guardado como {output_file}")

