import os

root_fld = os.path.join(os.getcwd(), "app/virtual_db/")

def read_property(filename, key):
    """Reads a property value from a .txt file"""
    full_filename = f"{root_fld}{filename}" if filename.endswith(".txt") else f"{root_fld}{filename}.txt"
    try:
        with open(full_filename, "r") as file:
            for line in file:
                if line.startswith(str(key) + "="):
                    return line.strip().split("=", 1)[1]
    except FileNotFoundError:
        print("File not found!")
    return None


def write_property(filename, key, value):
    """Writes or updates a property in a .txt file"""
    lines = []
    found = False
    full_filename = f"{root_fld}{filename}" if filename.endswith(".txt") else f"{root_fld}{filename}.txt"
    try:
        with open(full_filename, "r") as file:
            lines = file.readlines()
    except FileNotFoundError:
        pass  # If file doesn't exist, we create a new one

    with open(full_filename, "w") as file:
        for line in lines:
            if line.startswith(str(key) + "="):
                file.write(f"{key}={value}\n")
                found = True
            else:
                file.write(line)
        if not found:
            file.write(f"{key}={value}\n")  # Add new key if not found
