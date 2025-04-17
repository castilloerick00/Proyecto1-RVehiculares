import xml.etree.ElementTree as ET
import random
import sumolib

# Archivos de entrada y salida
input_file = "mapa.rou.xml"
output_file = "mapa_buses_modificado.rou.xml"
net_file = "network_centro.net.xml"
percentage = 100  # Porcentaje de buses urbanos a modificar

# Edges de inicio y fin para las rutas
start_edges = ["553363959", "399285450#0", "42140278#1"]
end_edges = ["399285452#4", "400084631#3", "42143918#13", "402191985#4"]

# Combinaciones posibles de rutas (inicio-fin)
route_combinations = [
    (start_edges[0], end_edges[0]),
    (start_edges[0], end_edges[2]),
    (start_edges[1], end_edges[1]),
    (start_edges[1], end_edges[2]),
    (start_edges[1], end_edges[3]),
    (start_edges[2], end_edges[0]),
    (start_edges[2], end_edges[1]),
    (start_edges[2], end_edges[2]),
    (start_edges[2], end_edges[3])
]
route_weights = [3/18, 3/18, 2/18, 2/18, 2/18, 1/18, 1/18, 3/18, 1/18]  # Pesos uniformes para las combinaciones

# Leer la red de SUMO
net = sumolib.net.readNet(net_file)

# Parsear el archivo XML
tree = ET.parse(input_file)
root = tree.getroot()

# Filtrar solo los buses urbanos
buses = [vehicle for vehicle in root.findall("vehicle") if vehicle.get("type") == "bus_urbano"]
total_buses = len(buses)
print(f"Total de buses urbanos en {input_file}: {total_buses}")

# Calcular cuántos buses modificar según el porcentaje
num_to_modify = int(total_buses * percentage / 100)
buses_to_modify = random.sample(buses, num_to_modify)
print(f"Modificando {num_to_modify} buses urbanos.")

# Función para encontrar la ruta más corta entre dos edges
def get_path(net, start, end):
    try:
        start_edge = net.getEdge(start)
        end_edge = net.getEdge(end)
        path, _ = net.getShortestPath(start_edge, end_edge)
        return [edge.getID() for edge in path] if path else None
    except Exception as e:
        print(f"Error buscando ruta entre {start} y {end}: {e}")
        return None

# Modificar las rutas de los buses seleccionados
for bus in buses_to_modify:
    start_edge, end_edge = random.choices(route_combinations, weights=route_weights, k=1)[0]
    
    # Calcular la ruta directa más corta entre start_edge y end_edge
    full_route = get_path(net, start_edge, end_edge)
    
    if full_route:
        route_element = bus.find("route")
        if route_element is not None:
            route_element.set("edges", " ".join(full_route))
        else:
            ET.SubElement(bus, "route", edges=" ".join(full_route))
        print(f"Bus {bus.get('id')} actualizado. Ruta: {' '.join(full_route)}")
    else:
        print(f"No se encontró ruta válida para el bus {bus.get('id')}.")

# Guardar el archivo modificado
tree.write(output_file, encoding="UTF-8", xml_declaration=True)
print(f"Archivo guardado como {output_file}")
