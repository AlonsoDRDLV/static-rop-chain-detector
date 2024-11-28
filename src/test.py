import subprocess

# Base command components
python_executable = r"C:\Users\AlonsoDRDLV\AppData\Local\Programs\Python\Python310\python.exe"
script_path = r"C:\Users\AlonsoDRDLV\Documents\GitHub\static-rop-chains-detector\src\__main__.py"
input_path = r"..\dmp_examples\2264_26-11-2024_12-46-30_UTC"

# Argument ranges
second_arg_values = [3, 2]
third_arg_values = range(1, 9)

# Iterate through combinations and execute the command
for second_arg in second_arg_values:
    for third_arg in third_arg_values:
        # Build the command
        command = [
            python_executable,
            script_path,
            input_path,
            str(second_arg),
            str(third_arg)
        ]
        # Print the command being executed (optional)
        print(f"Executing: {' '.join(command)}")
        
        # Run the command
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Command failed with error: {e}")
