#!/bin/bash

# Definir arrays de inicios y períodos
declare -a INICIOS=(0 2700 3600 5400 7200 10800)
declare -a PERIODOS=(0.45 0.4 0.35 0.5 0.45)

# Archivo final
OUTPUT="mapa.rou.xml"
TEMP_FILES=()

declare -i OFFSET=0  # Contador para IDs únicos

# Generar rutas para cada franja horaria
for ((i=0; i<${#INICIOS[@]}-1; i++)); do
    BEGIN=${INICIOS[$i]}
    END=${INICIOS[$i+1]}
    PERIOD=${PERIODOS[$i]}
    TEMP_FILE="temp_routes_${i}.rou.xml"

    echo "Generando rutas para franja $BEGIN-$END con período $PERIOD segundos..."
    python3 /opt/sumo/tools/randomTrips.py -v -n network_centro.net.xml -r "$TEMP_FILE" \
        --additional-files vtypes.add.xml \
        --begin "$BEGIN" --end "$END" --period "$PERIOD" \
        --seed 42

    # Ajustar IDs en el archivo temporal
    awk -v offset="$OFFSET" '/<vehicle / {
        sub(/id="[0-9]+"/, sprintf("id=\"%d\"", offset++))
    } 1' "$TEMP_FILE" > "$TEMP_FILE.adjusted"
    mv "$TEMP_FILE.adjusted" "$TEMP_FILE"

    # Actualizar el contador con el número de vehículos en este intervalo
    COUNT=$(grep -c "<vehicle " "$TEMP_FILE")
    OFFSET+=$COUNT

    TEMP_FILES+=("$TEMP_FILE")
done

# Combinar todos los archivos temporales en mapa.rou.xml
echo "Combinando archivos en $OUTPUT..."
echo '<?xml version="1.0" encoding="UTF-8"?>' > "$OUTPUT"
echo '<routes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/routes_file.xsd">' >> "$OUTPUT"

for TEMP_FILE in "${TEMP_FILES[@]}"; do
    # Extraer contenido entre <routes> y </routes>, omitiendo el encabezado XML y las etiquetas <routes>
    sed '1d; $d' "$TEMP_FILE" | grep -v '<routes' | grep -v '</routes>' >> "$OUTPUT"
    rm "$TEMP_FILE"  # Eliminar archivo temporal
done

echo '</routes>' >> "$OUTPUT"

# Script Python para asignar tipos de vehículos aleatorios con porcentajes
echo "Asignando tipos de vehículos aleatorios con porcentajes..."
cat << 'EOF' > assign_random_vtypes.py
import xml.etree.ElementTree as ET
import random


vehicle_types = [
    "moto_standard",
    "moto_deportiva",
    "bus_urbano",
    "camion_ligero",
    "camion_pesado",
    "ambulancia",
    "camion_bomberos",
    "chevrolet_aveo",
    "chevrolet_spark",
    "chevrolet_vitara",
    "chevrolet_sail",
    "chevrolet_dmax",
    "toyota_yaris",
    "toyota_corolla",
    "toyota_fortuner",
    "mitsubishi_asx",
    "mitsubishi_lancer",
    "mitsubishi_l200",
    "mitsubishi_montero",
    "kia_rio",
    "kia_sportage",
    "kia_picanto",
    "hyundai_tucson",
    "hyundai_creta",
    "hyundai_grand_i10",
    "hyundai_hilux",
    "nissan_sentra",
    "mazda_3",
    "mazda_bt50",
    "volkswagen_gol",
    "suzuki_grand_vitara"
]

weights = [
    0.07,  # moto_standard (7%)
    0.03,  # moto_deportiva (3%)
    0.05,  # bus_urbano (10%)
    0.03,  # camion_ligero (3%)
    0.01,  # camion_pesado (1%)
    0.01,  # ambulancia (1%)
    0.01,  # camion_bomberos (1%)
    0.04,  # chevrolet_aveo (4%)
    0.04,  # chevrolet_spark (4%)
    0.03,  # chevrolet_vitara (3%)
    0.04,  # chevrolet_sail (4%)
    0.03,  # chevrolet_dmax (3%)
    0.04,  # toyota_yaris (4%)
    0.04,  # toyota_corolla (4%)
    0.04,  # toyota_fortuner (3%)
    0.03,  # mitsubishi_asx (3%)
    0.03,  # mitsubishi_lancer (3%)
    0.03,  # mitsubishi_l200 (2%)
    0.02,  # mitsubishi_montero (2%)
    0.04,  # kia_rio (4%)
    0.04,  # kia_sportage (2%)
    0.04,  # kia_picanto (4%)
    0.03,  # hyundai_tucson (2%)
    0.02,  # hyundai_creta (2%)
    0.04,  # hyundai_grand_i10 (4%)
    0.02,  # hyundai_hilux (2%)
    0.03,  # nissan_sentra (3%)
    0.03,  # mazda_3 (3%)
    0.03,  # mazda_bt50 (2%)
    0.03,  # volkswagen_gol (3%)
    0.03   # suzuki_grand_vitara (2%)
]


tree = ET.parse("mapa.rou.xml")
root = tree.getroot()

for vehicle in root.findall("vehicle"):
    # Usar random.choices con pesos para seleccionar un tipo
    chosen_type = random.choices(vehicle_types, weights=weights, k=1)[0]
    vehicle.set("type", chosen_type)

tree.write("mapa.rou.xml", encoding="UTF-8", xml_declaration=True)
EOF

python3 assign_random_vtypes.py
rm assign_random_vtypes.py

echo "Simulación generada en $OUTPUT."

