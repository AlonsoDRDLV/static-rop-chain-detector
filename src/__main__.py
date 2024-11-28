import sys
from file_manager.file_manager import FileManager

if __name__ == "__main__":
    # Check if folder name is provided as a command line argument
    if len(sys.argv) < 2:
        print("Please provide the folder name as a command line argument.")
        sys.exit(1)

    folder_name = sys.argv[1]
    x = int(sys.argv[2])  # Maximum DWORD separation
    y = int(sys.argv[3])  # Minimum sequence length

    # Create FileManager instance
    file_manager = FileManager(folder_name)

    matches = []  # Store all matches
    sequences = []  # Store valid sequences
    current_sequence = []  # Track the ongoing sequence
    gap_count = 0  # Count gaps in the sequence

    # Read all files using get_next_direction
    while True:
        if not file_manager.read_next_dmp_file():
            break
        while True:
            next_direction = file_manager.get_next_direction()

            if next_direction is None:
                # End of files, finalize any sequence being built
                if len(current_sequence) > y:
                    sequences.append(current_sequence)
                break

            next_direction_val = next_direction[1]
            next_direction_address = next_direction[0]
            next_dir_int_value = int.from_bytes(next_direction_val, byteorder='little')
            match_found = False
            # Check if the next_dir_int_value falls within any memory region
            for region in file_manager.dmp_info:
                low, high = region["Memory region"]
                if low <= next_dir_int_value <= high:
                    matches.append(next_direction)
                    match_found = True
                    if gap_count <= x:  # Continue sequence
                        current_sequence.append(next_direction)
                    else:  # Start a new sequence
                        if len(current_sequence) > y:
                            sequences.append(current_sequence)
                        current_sequence = [next_direction]
                    gap_count = 0
                    break

            if not match_found:
                gap_count += 1
                if gap_count > x and len(current_sequence) > y:
                    sequences.append(current_sequence)
                    current_sequence = []

            #print(f"Next DWORD to be read: {next_direction_val.decode('ascii', errors='ignore')} with int value: {next_dir_int_value}")
    """
    print("Matches:")
    for match in matches:
        print(
            match[0],  # The integer value
            hex(int.from_bytes(match[1], byteorder='little')),  # Integer in hex
            "0x" + match[1].hex(),  # Bytes in hex, prefixed manually
            match[1].decode('ascii', errors='ignore')  # ASCII representation

        )
    """
    print("\nSequences (x-gap-separated, longer than y):")
    for sequence_index, matches in enumerate(sequences):
        print\
            (f"Sequence {sequence_index + 1} (length: {len(matches)}):\n")
        for match in matches:
            print(
                match[0],  # The integer value
                hex(int.from_bytes(match[1], byteorder='little')),  # Integer in hex
                f"0x{match[1].hex()}"  # Bytes in hex prefixed with 0x
            )
        print()  # Add a blank line between sequences for readability

    # Open a file for writing
    with open("sequences_" + str(x) + "_" + str(y) + ".txt", "w") as file:
        file.write("Matches:\n")
        for sequence_index, matches in enumerate(sequences):
            file.write(f"Sequence {sequence_index + 1} (length: {len(matches)}):\n")
            for match in matches:
                file.write(
                    f"{match[0]} "  # The integer value
                    f"{hex(int.from_bytes(match[1], byteorder='little'))} "  # Integer in hex
                    f"0x{match[1].hex()}\n"  # Bytes in hex prefixed with 0x
                )
            file.write("\n")  # Add a blank line between sequences for readability



