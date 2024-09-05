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
    time_series = [start_datetime + timedelta(minutes=i) for i in range(num_points)]
    return time_series

# Función mejorada para graficar los datos en función del tiempo, incluyendo coincidencias en una subgráfica adicional
def plot_time_series(df, start_datetime):
    time_series = generate_time_series(start_datetime, len(df))
    
    # Dividimos las columnas, dejando la última como coincidencias
    data_columns = df.columns[:-1]
    coincidence_column = df.columns[-1]

    # Crear una figura con 2 subgráficas
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

    # Graficar todas las columnas excepto la de coincidencias en la primera subgráfica
    df[data_columns].index = time_series
    df[data_columns].plot(ax=ax1, marker='+', legend=True)
    ax1.set_title('Counts per Second (sin coincidencias)')
    ax1.set_xlabel('Time')  # No mostrar la etiqueta del tiempo en la subgráfica superior
    ax1.set_ylabel('Counts per Second')
    ax1.grid(True)
    ax1.set_ylim(150, 400)

    # Graficar las coincidencias en la segunda subgráfica
    df[coincidence_column].index = time_series
    df[coincidence_column].plot(ax=ax2, marker='+', legend=True, color='orange')
    ax2.set_title('Coincidences per Second')
    ax2.set_xlabel('Time')
    ax2.set_ylabel('Coincidences')
    ax2.grid(True)
    ax2.set_ylim(0, 3)

    # Ajustar la visualización
    plt.tight_layout()
    plt.savefig('output_time_series_with_coincidences.png')

# Función para graficar el histograma (binning diferente para la última columna)
def plot_histogram(df):
    # Bins comunes para todas las columnas excepto la última
    bins_common = 3820
    # Bins específicos para la última columna
    bins_last = 5850

    # Graficar histogramas
    fig, axes = plt.subplots(nrows=len(df.columns), ncols=1, figsize=(8, 12))

    # Graficar histogramas con diferentes límites de x según la columna
    for i in range(len(df.columns)):
        if i < len(df.columns) - 1:
            df.iloc[:, i].plot(kind='hist', bins=bins_common, alpha=0.5, ax=axes[i])
            axes[i].set_xlim(150, 275)
            axes[i].set_title(f'Histogram of scaler count for ch{i}')
        else:
            df.iloc[:, i].plot(kind='hist', bins=bins_last, alpha=0.5, ax=axes[i])
            axes[i].set_xlim(0, 3)
            axes[i].set_title(f'Histogram for coincidence')

        axes[i].set_xlabel('Counts per Second')
        axes[i].set_ylabel('Frequency')
        axes[i].grid(True)

    plt.tight_layout()
    plt.savefig('output_histograms.png')

# Función mejorada para extraer el día, mes, año y hora del nombre del archivo
def extract_datetime_from_filename(file_path):
    filename = os.path.basename(file_path)
    # Extraer la parte de la fecha y la hora del nombre del archivo
    date_part = filename.split('_')[0]  # Extraer "29082024" de "29082024_1023_output.txt"
    time_part = filename.split('_')[1][:4]  # Extraer "1023" de "29082024_1023_output.txt"

    # Convertir la fecha y hora en un objeto datetime
    date_time = datetime.strptime(date_part + time_part, '%d%m%Y%H%M')
    return date_time

# Función principal
def main():
    if len(sys.argv) != 2:
        print("Uso: python3 escaramujoseg.py <ruta_al_archivo>")
        sys.exit(1)

    file_path = sys.argv[1]

    if not os.path.isfile(file_path):
        print(f"Archivo no encontrado: {file_path}")
        sys.exit(1)

    # Extraer la fecha y hora inicial del nombre del archivo
    start_datetime = extract_datetime_from_filename(file_path)

    # Procesar el archivo y obtener el DataFrame
    df = read_and_process_file(file_path)

    # Graficar los datos en función del tiempo con subgráfica para coincidencias
    plot_time_series(df, start_datetime)

    # Graficar los histogramas
    plot_histogram(df)

if __name__ == "__main__":
    main()

