import subprocess
import argparse
from tqdm import tqdm

# Argument ranges
# variable_x_values = [8, 6, 4, 2]
# variable_y_values = range(2, 9)

# Base command components
python_executable = r"C:\Users\AlonsoDRDLV\AppData\Local\Programs\Python\Python310\python.exe"
script_path = r"C:\Users\AlonsoDRDLV\Documents\GitHub\static-rop-chains-detector\src\__main__.py"
qinput_path = r"..\dmp_examples\2264_26-11-2024_12-46-30_UTC"

parser = argparse.ArgumentParser(description="Argumentos para x e y.")

# variable_x_values aceptará múltiples enteros:
parser.add_argument(
    "--x",
    nargs="+",               # permite uno o más valores
    type=int,                # cada valor se interpreta como entero
    default=[5, 4, 3, 2],    # valor por defecto si no se pasa ningún argumento
    help="Lista de valores para la variable X (ej.: --x 8 6 4 2)"
)

# variable_x_values aceptará múltiples enteros:
parser.add_argument(
    "--y",
    nargs="+",               # permite uno o más valores
    type=int,                # cada valor se interpreta como entero
    default=[2, 3, 4, 5, 6, 7, 8, 9, 10],    # valor por defecto si no se pasa ningún argumento
    help="Lista de valores para la variable y (ej.: --y 8 6 4 2)"
)

args = parser.parse_args()

# Asignamos a las variables
variable_x_values = args.x
variable_y_values = args.y

# Iterate through combinations and execute the command
total_iterations = len(variable_x_values) * len(variable_y_values)

# Create a progress bar
with tqdm(total=total_iterations, desc="Executing") as progress_bar:
    for second_arg in variable_x_values:
        for third_arg in variable_y_values:
            # Build the command
            command = [
                python_executable,
                script_path,
                input_path,
                str(second_arg),
                str(third_arg)
            ]

            # Run the command
            try:
                subprocess.run(command, check=True)
            except subprocess.CalledProcessError as e:
                print(f"Command failed with error: {e}")

            # Update the progress bar
            progress_bar.update(1)