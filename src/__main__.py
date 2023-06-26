import sys
from file_manager.file_manager import FileManager

if __name__ == "__main__":
    # Check if folder name is provided as a command line argument
    if len(sys.argv) < 2:
        print("Please provide the folder name as a command line argument.")
        sys.exit(1)

    folder_name = sys.argv[1]

    # Create FileManager instance
    file_manager = FileManager(folder_name)

    # Read all files using get_next_direction
    while True:
        next_direction = file_manager.get_next_direction()
        if next_direction is None:
            break
        print(f"Next DWORD to be read: {next_direction}")