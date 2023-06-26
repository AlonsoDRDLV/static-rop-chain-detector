from typing import List, Tuple


class FileManager:
    def __init__(self, folder_name: str):
        """
        Initializes a FileManager object with the specified folder name. It parses the results.txt file
        inside the folder and stores the extracted information as attributes.

        Args:
            folder_name (str): The name of the folder containing the results.txt file.
        """

        self.folder_name = folder_name  # folder where the dmp files are
        self.stack_info = self.parse_result_file()  # list of dictionaries with info related to the stack dmp files
        self.current_file_index = 0     # index for stack_info of the currently open file
        self.current_file = None
        self.current_file_offset = 0    # next byte to read

    def parse_result_file(self) -> List[dict] | None:
        """
        Parses the results.txt file inside the folder specified during object initialization and extracts
        thread ID, memory address, stack size, and file name from the filenames listed in the file.

        Returns:
            List[dict]: A list of dictionaries, where each dictionary contains the file name, thread ID,
            memory address, and stack size extracted from the filenames. Returns None if an error
            occurs while opening or reading the file.
        """

        file_path = self.folder_name + '/stacks/results.txt'
        stack_info = []

        try:
            with open(file_path, 'r') as file:
                contents = file.read()
                file.close()

                lines = contents.split('\n')

                for line in lines:
                    if line.startswith('Filename:'):
                        filename_parts = line.split(', SHA-256:')[0].split('_')
                        file_name = filename_parts[1] + '_' + filename_parts[2] + '_' + filename_parts[3] + '.dmp'
                        tid = int(filename_parts[1])
                        memory_address = filename_parts[2]
                        stack_size = int(filename_parts[3], 16)

                        stack_info.append({
                            'file_name': file_name,
                            'tid': tid,
                            'memory_address': memory_address,
                            'stack_size': stack_size
                        })

            return stack_info

        except IOError:
            print(f"Error: Could not open or read file {file_path}")
            return None

    def get_next_direction(self) -> int | None:
        """
        Returns the next DWORD to be read from the current dmp file.

        Returns:
            int: The next DWORD to be read. Returns None if there are no more files to be read or if an
            error occurs while reading the file.
        """

        if self.current_file is None or \
                self.current_file_offset >= self.stack_info[self.current_file_index]['stack_size']:
            if not self.read_next_dmp_file():
                return None

        try:
            self.current_file.seek(self.current_file_offset)
            dword = self.current_file.read(4)
            self.current_file_offset += 4

            if len(dword) < 4:  # End of file reached
                self.current_file.close()
                self.current_file = None
                self.current_file_offset = 0
                return self.get_next_direction()

            return int.from_bytes(dword, byteorder='little')

        except IOError:
            print(f"Error: Could not read file {self.stack_info[self.current_file_index]['file_name']}")
            return None

    def read_next_dmp_file(self) -> bool:
        """
        Opens the next dmp file in the stack_info list for reading.

        Returns:
            bool: True if the next file is successfully opened for reading, False if there are no more files.
        """

        if self.current_file_index >= len(self.stack_info):
            return False

        file_info = self.stack_info[self.current_file_index]
        file_name = file_info['file_name']

        try:
            self.current_file = open(file_name, 'rb')
            self.current_file_offset = 0
            self.current_file_index += 1
            return True

        except IOError:
            print(f"Error: Could not open or read file {file_name}")
            return False
