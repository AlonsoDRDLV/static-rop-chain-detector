import os
import sys
from process_dump_manager import ProcessDumpManager

# Define the size of the instruction in bytes for each instruction depending on the bitness
# Use the opcode as the key to the dictionary and the bitness as the key to the nested dictionary
CALL_INSTRUCTION_SIZES = {
    0xE8: {  # CALL rel16 or rel32 (near relative direct)
        # 32: [5, 3],  # rel16 (with operand override) or rel32
        32: [5],  # rel16 (with operand override) or rel32
        64: [5],  # rel32 (always 32-bit relative offset in 64-bit mode)
    },
    0x9A: {  # CALL ptr16:16 or ptr16:32 (far absolute direct)
        # 32: [7, 3],  # ptr16:32
        32: [7],  # ptr16:32
        64: None,  # Not valid in 64-bit mode
    },
    0xFF: {
        2: {
            # CALL r/m16, r/m32, r/m64 (near absolute indirect)
            # 32: [2, 3, 6, 7, 10, 4, 7, 8, 11],  # r/m32 [reg, reg+disp8, reg+disp32 and mem, mem+disp8, mem+disp32, SIB+reg, ...]
            # 64: [2, 3, 6, 10, 11, 14, 4, 7, 12],  # r/m64 [reg, reg+disp8, reg+disp32, mem+disp8, mem+disp32, SIB+reg, ...]
            # Mejor los valores más comunes (sin disp ni SIB)
            32: [2, 6],  # reg y mem
            64: [2, 10],  # reg y mem
        },
        3: {
            # and CALL m16:16, m16:32, m16:64 (far absolute indirect)
            # 32: [8, 6],  # m16:16, m16:32
            32: [8],  # m16:16, m16:32
            64: [12],  # m16:64
        },
    }
}


def is_prev_instruction_call(fm: ProcessDumpManager, address: int) -> bool:
    """
    Check if the previous instruction at the given address is an x86 CALL instruction.
    The instruction is read from the memory dump files using the FileManager instance.

    Args:
        fm (ProcessDumpManager): The FileManager instance to access the memory dump files.
        address (int): Address of the instruction to check.

    Returns:
        bool: True if the previous instruction is a CALL instruction, False otherwise.
    """
    # check if 0xE8
    possible_instruction_sizes = CALL_INSTRUCTION_SIZES[0xE8][fm.bitness]
    for size in possible_instruction_sizes:
        call_instruction = fm.access_img_dump_file(address - size)
        if call_instruction is None:
            return False
        if call_instruction[0] == 0xE8:
            return True

    # check if 0x9A
    possible_instruction_sizes = CALL_INSTRUCTION_SIZES[0x9A][fm.bitness]
    if possible_instruction_sizes is not None:
        for size in possible_instruction_sizes:
            call_instruction = fm.access_img_dump_file(address - size)
            if call_instruction is None:
                return False
            if call_instruction[0] == 0x9A:
                return True

    # check if 0xFF /2
    possible_instruction_sizes = CALL_INSTRUCTION_SIZES[0xFF][2][fm.bitness]
    for size in possible_instruction_sizes:
        call_instruction = fm.access_img_dump_file(address - size)
        if call_instruction is None:
            return False
        if call_instruction[0] == 0xFF:
            if len(call_instruction) < 2:
                return False
            modrm = call_instruction[1]
            reg = (modrm & 0b00111000) >> 3  # Extract Reg bits
            # near absolute indirect requires Reg field to be 2
            if reg == 2:
                return True

    # check if 0xFF /3
    possible_instruction_sizes = CALL_INSTRUCTION_SIZES[0xFF][3][fm.bitness]
    for size in possible_instruction_sizes:
        call_instruction = fm.access_img_dump_file(address - size)
        if call_instruction is None:
            return False
        if call_instruction[0] == 0xFF:
            if len(call_instruction) < 2:
                return False
            modrm = call_instruction[1]
            reg = (modrm & 0b00111000) >> 3
            # far absolute indirect requires Reg field to be 3
            if reg == 3:
                return True

    return False


if __name__ == "__main__":
    # Check if folder name is provided as a command line argument
    if len(sys.argv) < 2:
        print("Please provide the folder name as a command line argument.")
        sys.exit(1)

    folder_name = sys.argv[1]
    distance_between_gadgets = int(sys.argv[2])  # Maximum DWORD separation
    min_chain_length = int(sys.argv[3])  # Minimum ROPchain length

    # Create FileManager instance
    p_dump_manager = ProcessDumpManager(folder_name)

    matches = []  # Store all matches
    ROPchains = []  # Store valid ROPchains
    current_ROPchain = []  # Track the ongoing ROPchain
    gap_count = 0  # Count gaps in the sequence

    # Read all files using get_next_direction
    while True:
        if not p_dump_manager.read_next_stack_dmp_file():
            break
        # Read all directions from the current file
        while True:
            next_direction = p_dump_manager.get_next_direction()

            if next_direction is None:
                # End of files, finalize any ROPchain being built
                if len(current_ROPchain) > min_chain_length:
                    ROPchains.append(current_ROPchain)
                break

            next_direction_val = next_direction[1]
            next_direction_address = next_direction[0]
            next_dir_int_value = int.from_bytes(next_direction_val, byteorder='little')
            match_found = False

            # Check if the next_dir_int_value falls within any memory region
            if p_dump_manager.is_in_img_region(next_dir_int_value): # and not is_prev_instruction_call(p_dump_manager, next_dir_int_value):
                # Check if the previous instruction is a CALL instruction
                matches.append(next_direction)
                match_found = True

                if gap_count <= distance_between_gadgets:  # Continue ROPchain
                    current_ROPchain.append(next_direction)

                else:  # if ROPchain is broken, start a new ROPchain
                    if len(current_ROPchain) >= min_chain_length:   # if ROPchain is longer than y, add it to ROPchains
                        ROPchains.append(current_ROPchain)
                    current_ROPchain = [next_direction]

                gap_count = 0

            if not match_found:
                gap_count += 1
                if gap_count > distance_between_gadgets and len(current_ROPchain) >= min_chain_length:
                    ROPchains.append(current_ROPchain)
                    current_ROPchain = []
                    gap_count = 0

    # Print and save results

    # print(f"\nROPchains ({x}-gap-separated, longer than {y}):")
    # for sequence_index, matches in enumerate(ROPchains):
        # print(f"ROPchain {sequence_index + 1} (length: {len(matches)}):")
        # for match in matches:
            # print(f"{hex(match[0])}:    {hex(int.from_bytes(match[1], byteorder='little'))}"),
        # print()  # Add a blank line between ROPchain for readability

    # Open a file for writing inside the analysis_results directory. Create it if it doesn't exist.
    # Get the current working directory
    current_dir = os.getcwd()
    # Create the new directory path
    new_dir_path = os.path.join(current_dir, "analysis_results")
    # Create the directory if it doesn't exist
    os.makedirs(new_dir_path, exist_ok=True)
    file_path = os.path.join(new_dir_path, "ROPchains_" + str(distance_between_gadgets) + "_" + str(min_chain_length) + ".txt")
    with open(file_path, "w") as file:
        file.write(f"Matches for x={distance_between_gadgets} and y={min_chain_length}:\n")
        for sequence_index, matches in enumerate(ROPchains):
            file.write(f"ROPchain {sequence_index + 1} (length: {len(matches)}):\n")
            for match in matches:
                file.write(
                    f"{hex(match[0])}:    {hex(int.from_bytes(match[1], byteorder='little'))}\n"  # The address and the value
                )
            file.write("\n")  # Add a blank line between sequences for readability
    # print("Results saved to file.")
    file.close()