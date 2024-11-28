from typing import List, Tuple, Union


class FileManager:
    def __init__(self, folder_name: str):
        """
        Initializes a FileManager object with the specified folder name. It parses the results.txt file
        inside the folder and stores the extracted information as attributes.

        Args:
            folder_name (str): The name of the folder containing the results.txt file.
        """

        self.folder_name = folder_name  # folder where the dmp files are
        self.stack_info = self.parse_stacks_result_file()  # list of dictionaries with info related to the stack dmp files
        self.bitness, self.dmp_info = self.parse_results_file() # bitness of the process and list of dictionaries with info related to the dmp files
        self.dword_size = self.bitness // 8  # size of a DWORD in bytes
        self.current_file_index = -1     # index for stack_info of the currently open file
        self.current_file = None
        self.current_file_offset = 0    # next byte to read

        print(f"folder_name: {self.folder_name}")
        print(f"stack_info: {self.stack_info}")
        print(f"bitness: {self.bitness}")
        print(f"dmp_info: {self.dmp_info}")
        print(f"dword_size: {self.dword_size}")
        print(f"current_file_index: {self.current_file_index}")
        print(f"current_file: {self.current_file}")
        print(f"current_file_offset: {self.current_file_offset}")

    def parse_stacks_result_file(self) -> List[dict] | None:
        """
        Parses the results.txt file inside the folder specified during object initialization and extracts
        thread ID, memory address, stack size, and file name from the filenames listed in the file.

        Returns:
            List[dict]: A list of dictionaries, where each dictionary contains the file name, thread ID,
            memory address, and stack size extracted from the filenames. Returns None if an error
            occurs while opening or reading the file.
        """

        file_path = self.folder_name + '\\stacks\\results.txt'
        stack_info = []

        try:
            with open(file_path, 'r') as file:
                contents = file.read()
                file.close()

                lines = contents.split('\n')

                for line in lines:
                    if line.startswith('Filename:'):
                        filename_parts = line.split(', SHA-256:')[0].split(' ')[1].split('_')[0:-1] + [line.split('_')[-1].split('.')[0]]
                        file_name = filename_parts[0] + '_' + filename_parts[1] + '_' + filename_parts[2] + '.dmp'
                        tid = int(filename_parts[0])
                        memory_address = filename_parts[1]
                        stack_size = int(filename_parts[2], 16)

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

    def parse_results_file(self):
        """
        Parses the results.txt file inside the folder specified during object initialization and extracts
        the bitness of the process and the file name, SHA-256, and memory protection of the dmp files.

        :param self:

        :return:
            bitness (int): The bitness of the process.
            dmp_list (List[dict]): A list of dictionaries, where each dictionary contains the file name,
            SHA-256, and memory protection extracted from the filenames.

        :trows:
            IOError: If the file cannot be opened or read.
        """
        file_path = self.folder_name + '\\results.txt'
        dmp_list = []

        try:
            with open(file_path, 'r') as file:
                lines = file.readlines()
                bitness = None

                for line in lines:
                    if line.startswith("Bitness of the process:"):
                        bitness = int(line.split(":")[1].strip())

                    elif line.startswith("Filename:"):
                        lines_separated_by_comma = line.split(",")
                        filename = lines_separated_by_comma[0].split(":")[1].strip()
                        sha256 = lines_separated_by_comma[1].split(":")[1].strip()
                        memory_protection = lines_separated_by_comma[2].split(":")[1].strip()
                        lowest_memory_address = int(filename.split("_")[0], 16)
                        highest_memory_address = lowest_memory_address + int(filename.split("_")[1].split(".")[0], 16) - 1

                        dmp_info = {
                            "Filename": filename,
                            "SHA-256": sha256,
                            "Memory protection": memory_protection,
                            "Memory region": (lowest_memory_address, highest_memory_address)
                        }

                        dmp_list.append(dmp_info)

        except IOError:
            print(f"Error: Could not open or read file {file_path}")
            return None, None

        return bitness, dmp_list

    def get_next_direction(self):
        """
        Returns the next DWORD to be read from the current dmp file.

        Returns:
            int: The next DWORD to be read. Returns None if there are no more files to be read or if an
            error occurs while reading the file.
        """

        try:
            if self.current_file is None or \
                    self.current_file_offset >= self.stack_info[self.current_file_index]['stack_size']:
                return None
        except IndexError as e:
            print(f"IndexError occurred: {e}")
            # Handle the error as needed, e.g., return a default value or log it
            return None

        try:
            self.current_file.seek(self.current_file_offset)
            dword = self.current_file.read(4)
            m_a = self.stack_info[self.current_file_index]["memory_address"]
            base_address = int(self.stack_info[self.current_file_index]["memory_address"], 16)
            address = base_address + self.current_file_offset
            self.current_file_offset += self.dword_size

            if len(dword) < self.dword_size:  # End of file reached
                self.current_file.close()
                self.current_file = None
                self.current_file_offset = 0
                return None

            return address, dword

        except IOError:
            print(f"Error: Could not read file {self.stack_info[self.current_file_index]['file_name']}")
            return None

    def read_next_dmp_file(self) -> bool:
        """
        Opens the next dmp file in the stack_info list for reading.

        Returns:
            bool: True if the next file is successfully opened for reading, False if there are no more files.
        """
        self.current_file_offset = 0
        self.current_file_index += 1

        if self.current_file_index >= len(self.stack_info):
            return False

        file_info = self.stack_info[self.current_file_index]
        file_name = self.folder_name + "\\stacks\\" + file_info['file_name']

        try:
            self.current_file = open(file_name, 'rb')
            print("File: ", self.current_file_index)
            return True

        except IOError:
            print(f"Error: Could not open or read file {file_name}")
            return False
