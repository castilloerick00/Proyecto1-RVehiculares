import xml.etree.ElementTree as ET
from collections import defaultdict

# === Configuración ===
archivo_emisiones = "emissions_traci.xml"
archivo_salida = "edgedata_0_10800_traci.xml"
inicio_intervalo = 0
fin_intervalo = 10800

co2_por_edge = defaultdict(float)
tiempo_actual = 0

context = ET.iterparse(archivo_emisiones, events=("start",))
for event, elem in context:
    if elem.tag == "timestep":
        tiempo_actual = float(elem.attrib["time"])
    elif elem.tag == "vehicle":
        if inicio_intervalo <= tiempo_actual <= fin_intervalo:
            co2 = float(elem.attrib["CO2"])
            lane_id = elem.attrib["lane"]
            edge_id = lane_id.split("_")[0]
            co2_por_edge[edge_id] += co2
    elem.clear()

# === Crear archivo edgedata ===
root = ET.Element("edgedata")
interval = ET.SubElement(root, "interval")
interval.set("begin", str(inicio_intervalo))
interval.set("end", str(fin_intervalo))

for edge_id, total_co2 in co2_por_edge.items():
    edge = ET.SubElement(interval, "edge")
    edge.set("id", edge_id)
    edge.set("CO2", f"{total_co2:.2f}")

tree = ET.ElementTree(root)
tree.write(archivo_salida, encoding="UTF-8", xml_declaration=True)
print(f"✅ Archivo '{archivo_salida}' generado con emisiones de {inicio_intervalo}s a {fin_intervalo}s.")


