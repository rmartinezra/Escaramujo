import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import sys
import os

# Función para leer y procesar el archivo
def read_and_process_file(file_path):
    # Leer el archivo y filtrar las líneas que comienzan con "DS"
    with open(file_path, 'r') as file:
        ds_lines = [line.strip() for line in file if line.startswith('DS')]

    # Extraer valores hexadecimales, convertirlos a decimales y ajustarlos dividiéndolos entre 60
    data = []
    for line in ds_lines:
        hex_values = line.split()[1:]  # Omitir la primera palabra "DS"
        decimal_values = [int(value, 16)*16 / 60 for value in hex_values]
        data.append(decimal_values)

    # Convertir a DataFrame, ajustando dinámicamente el número de columnas
    df = pd.DataFrame(data)

    # Eliminar la primera columna
    df = df.iloc[:, 1:]

    # Renombrar las columnas dinámicamente según el número de columnas restantes
    df.columns = [f'Column {i+1}' for i in range(df.shape[1])]

    return df

# Función para generar la serie temporal basada en la fecha/hora inicial y el número de puntos de datos
def generate_time_series(start_datetime, num_points):
    try:
        time_series = [start_datetime + timedelta(minutes=i) for i in range(num_points)]
    except Exception as e:
        print(f"Error al generar la serie temporal: {e}")
        sys.exit(1)
    return time_series

# Función para aplicar "rolling window" a las columnas sin coincidencias
def apply_rolling_window(df, window_size):
    data_columns = df.columns[:-1]  # Todas las columnas excepto la última (coincidencias)
    # Aplicar un rolling window a las columnas sin coincidencias y calcular el promedio
    df[data_columns] = df[data_columns].rolling(window=window_size, min_periods=1).mean()
    return df

# Función para graficar los datos en función del tiempo
def plot_time_series(df, start_datetime):
    time_series = generate_time_series(start_datetime, len(df))
    
    # Asignar la serie temporal como índice del DataFrame
    df.index = pd.to_datetime(time_series)

    # Crear una figura con 2 subgráficas
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

    # Graficar todas las columnas excepto la de coincidencias en la primera subgráfica (con rolling window aplicado)
    data_columns = df.columns[:-1]
    df[data_columns].plot(ax=ax1, marker='+', legend=True)
    ax1.set_title('Counts per Second (sin coincidencias) con Rolling Window')
    ax1.set_ylabel('Counts per Second')
    ax1.grid(True)
    ax1.set_ylim(150, 350)

    # Graficar las coincidencias en la segunda subgráfica
    coincidence_column = df.columns[-1]
    df[coincidence_column].plot(ax=ax2, marker='+', legend=True, color='orange')
    ax2.set_title('Coincidences per Second')
    ax2.set_xlabel('Time')
    ax2.set_ylabel('Coincidences')
    ax2.grid(True)
    ax2.set_ylim(0, 6)

    # Mostrar la gráfica
    plt.show()

# Función para extraer el día, mes, año y hora del nombre del archivo
def extract_datetime_from_filename(file_path):
    filename = os.path.basename(file_path)
    # Extraer la parte de la fecha y la hora del nombre del archivo
    date_part = filename.split('_')[0]  # Extraer "29082024" de "29082024_1023_output.txt"
    time_part = filename.split('_')[1][:4]  # Extraer "1023" de "29082024_1023_output.txt"

    # Convertir la fecha y hora en un objeto datetime
    try:
        date_time = datetime.strptime(date_part + time_part, '%d%m%Y%H%M')
    except ValueError as ve:
        print(f"Error al procesar la fecha/hora del archivo: {ve}")
        sys.exit(1)
    return date_time

# Función principal
def main():
    if len(sys.argv) != 3:
        print("Uso: python3 rollingesc.py <ruta_al_archivo> <tamaño_ventana>")
        sys.exit(1)

    file_path = sys.argv[1]
    window_size = int(sys.argv[2])

    if not os.path.isfile(file_path):
        print(f"Archivo no encontrado: {file_path}")
        sys.exit(1)

    # Extraer la fecha y hora inicial del nombre del archivo
    start_datetime = extract_datetime_from_filename(file_path)

    # Procesar el archivo y obtener el DataFrame
    df = read_and_process_file(file_path)

    # Aplicar rolling window
    df = apply_rolling_window(df, window_size)

    # Graficar los datos en función del tiempo con subgráfica para coincidencias
    plot_time_series(df, start_datetime)

if __name__ == "__main__":
    main()
