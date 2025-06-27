import os
import re
import matplotlib.pyplot as plt


# -----------------------------
# 1) Función para parsear archivos
#    Retorna un diccionario {y: count} con el número de ROP chains por cada valor de y.
# -----------------------------
def parse_ropchain_files(result_file_paths):
    chain_counts = {}

    # Regular expression para archivos: ROPchains_x_y.txt
    regex_pattern = re.compile(r"ROPchains_(\d+)_(\d+)\.txt")

    for file_path in result_file_paths:
        # Extraer x e y del nombre de archivo
        regex_match = regex_pattern.search(file_path)
        if not regex_match:
            print(f"Skipping file: {file_path} (invalid filename format)")
            continue

        variable_x = int(regex_match.group(1))
        variable_y = int(regex_match.group(2))

        # Contar cuántas veces aparece "ROPchain "
        with open(file_path, "r") as f:
            content = f.read()
            sequence_count = content.count("ROPchain ")

        # Sumamos el conteo a la clave "y" correspondiente
        chain_counts[variable_y] = chain_counts.get(variable_y, 0) + sequence_count

    return chain_counts


# -----------------------------
# 2) Función para graficar los conteos para un x concreto
# -----------------------------
def plot_sequence_counts(data, title, label):
    """
    data: diccionario {y: count}
    title: título de la gráfica
    label: etiqueta de la leyenda
    """
    x_vals = sorted(data.keys())
    y_vals = [data[key] for key in x_vals]

    plt.figure(figsize=(10, 6))
    plt.plot(x_vals, y_vals, marker='o', linestyle='-', label=label)
    plt.title(title)
    plt.xlabel("ROP chain length threshold (variable y)")
    plt.ylabel("Number of detected chains")
    plt.xticks(x_vals)
    plt.grid(True)
    plt.legend()
    plt.show()


# -----------------------------
# 3) Regex para identificar los archivos ROPchains_x_y.txt
# -----------------------------
file_pattern = re.compile(r"ROPchains_(\d+)_(\d+)\.txt")

# Directorio donde buscar los archivos
directory = "analysis_results"

# Diccionario para agrupar archivos por su valor de x (el primer número)
grouped_files = {}

# -----------------------------
# 4) Recorrer el directorio, agrupar archivos por x
# -----------------------------
for file_name in os.listdir(directory):
    match = file_pattern.match(file_name)
    if match:
        first_number = match.group(1)  # x
        if first_number not in grouped_files:
            grouped_files[first_number] = []
        grouped_files[first_number].append(os.path.join(directory, file_name))

# Revisar las agrupaciones encontradas
for group, files in grouped_files.items():
    print(f"Group {group}: {files}")

# -----------------------------
# 5) Crear un diccionario global para la tabla cruzada:
#    all_counts[x][y] = conteo total de ROP chains
# -----------------------------
all_counts = {}

# -----------------------------
# 6) Parsear cada grupo (cada x) y graficar individualmente
#    mientras llenamos all_counts[x][y].
# -----------------------------
for group, file_paths in grouped_files.items():
    # Parsear los archivos en este grupo => diccionario {y: count}
    sequence_counts = parse_ropchain_files(file_paths)

    # Convertir "group" en número entero para usar como x
    x_val = int(group)

    # Llenar el diccionario global all_counts
    if x_val not in all_counts:
        all_counts[x_val] = {}
    for y_val, count in sequence_counts.items():
        # Sumar (por si en algún caso hay más de un archivo con el mismo x, y)
        all_counts[x_val][y_val] = all_counts[x_val].get(y_val, 0) + count

    # Graficar para este valor de x
    plot_sequence_counts(
        sequence_counts,
        f"Number of detected ROP chains with distance between gadget addresses (variable x) = {x_val}",
        "Number of Sequences"
    )

# -----------------------------
# 7) Imprimir la tabla cruzada con filas=x y columnas=y
# -----------------------------

# Obtener todos los valores únicos de x e y
all_x = sorted(all_counts.keys())
all_y = sorted({y for x_dict in all_counts.values() for y in x_dict.keys()})

print("\nTABLA CRUZADA DE ROP CHAINS DETECTADAS (x en filas, y en columnas)\n")

# Encabezado de columnas
header = [" x \\ y "] + [f"{y:>5}" for y in all_y]
print(" | ".join(header))

# Línea divisoria (opcional)
print("-" * (len(header) * 8))

# Filas para cada valor de x
for x_val in all_x:
    # Primera columna = valor de x
    row_data = [f"{x_val:>5}"]
    # Rellenar columnas con los valores de y
    for y_val in all_y:
        count = all_counts[x_val].get(y_val, 0)
        row_data.append(f"{count:>5}")
    print(" | ".join(row_data))
