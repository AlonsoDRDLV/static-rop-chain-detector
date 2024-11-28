import os
import re
import matplotlib.pyplot as plt

# Function to parse sequence files and count sequences
def parse_sequence_files(file_paths):
    sequence_counts = {}
    
    # Regular expression to match sequence files
    file_pattern = re.compile(r"sequences_(\d+)_(\d+).txt")
    
    for file_path in file_paths:
        # Extract the second and third arguments from the filename
        match = file_pattern.search(file_path)
        if not match:
            print(f"Skipping file: {file_path} (invalid filename format)")
            continue
        
        second_arg = int(match.group(1))
        third_arg = int(match.group(2))
        
        # Count the sequences in the file
        with open(file_path, "r") as f:
            content = f.read()
            sequence_count = content.count("Sequence ")
        
        # Store the count for this third_arg
        sequence_counts[third_arg] = sequence_counts.get(third_arg, 0) + sequence_count
    
    return sequence_counts

# Function to plot the sequence counts
def plot_sequence_counts(data, title, label):
    x = sorted(data.keys())
    y = [data[key] for key in x]
    
    plt.figure(figsize=(10, 6))
    plt.plot(x, y, marker='o', linestyle='-', label=label)
    plt.title(title)
    plt.xlabel("Third Argument (x-axis)")
    plt.ylabel("Number of Sequences (y-axis)")
    plt.xticks(x)
    plt.grid(True)
    plt.legend()
    plt.show()

# File paths for the uploaded sequence files
file_paths = [
    #"sequences_2_1.txt",
    #"sequences_2_2.txt",
    #"sequences_2_3.txt",
    #"sequences_2_4.txt",
    #"sequences_2_5.txt",
    #"sequences_2_6.txt",
    #"sequences_2_7.txt",
    #"sequences_2_8.txt",
    "sequences_3_1.txt",
    "sequences_3_2.txt",
    "sequences_3_3.txt",
    "sequences_3_4.txt",
    "sequences_3_5.txt",
    "sequences_3_6.txt",
    "sequences_3_7.txt",
    "sequences_3_8.txt",
]

# Parse the sequence files
sequence_counts = parse_sequence_files(file_paths)

# Plot the sequence counts
plot_sequence_counts(sequence_counts, "Number of Sequences by Max ROP Chain Length", "Number of Sequences")
