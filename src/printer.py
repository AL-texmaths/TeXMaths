from src.tools import CONFIG, YEAR_DIR, get_cours_file_path
from src.impress import print_pdf,write_impress_datas

MESSAGES = {
    "printer": "Printer index ? ",
    "nb_copy": "How many copies ? ",
    "print_settings": "Print settings ? ",
    "file":    "File name ? ",
    "files":   "Files name ? (</> separator) "
    }
PRINTERS = CONFIG["parameters"]["printers"]

def show_printers():
    """
    """
    for printer_index in range(len(PRINTERS)):
        print("{}. {}".format(printer_index, PRINTERS[printer_index]))

def is_printer_index(printer_index_input):
    """
    """
    try:
        PRINTERS[int(printer_index_input)]
        return True
    except (ValueError, IndexError):
        print("WARNING: Wrong printer number.\n")
        return False

def is_positive(user_input):
    """
    """
    try:
        int(user_input)
        return int(user_input) > 0
    except ValueError:
        print("Input must be an integer.")
        return False

def choose_printer():
    """
    """
    message = MESSAGES["printer"]
    show_printers()
    printer_index_input = input(message)
    while not is_printer_index(printer_index_input):
        printer_index_input = input(message)
    return PRINTERS[int(printer_index_input)]
    
def choose_nb_copy():
    """
    """
    message = MESSAGES["nb_copy"]
    nb_copy = input(message)
    while not is_positive(nb_copy):
        nb_copy = input(message)
    return nb_copy

def choose_print_settings():
    """
    """
    message = MESSAGES["print_settings"]
    return input(message)

def check_input_format(code_input):
    """
    """
    level, chapter, document = code_input.split('-')
    file_type = f'{level}/{chapter}*/{code_input}.pdf'
    files = list(YEAR_DIR.rglob(file_type))
    if not files:
        print(f"Fichier introuvable : {file_type}")
        return False
    return True

def choose_file():
    """
    """
    message = MESSAGES["file"]
    file_name_input = input(message)
    while not check_input_format(file_name_input):
        file_name_input = input(message)
    return get_cours_file_path(file_name_input)

def choose_files():
    """
    """
    message = MESSAGES["files"]
    file_names_input = input(message)
    file_names = file_names_input.split('/')
    while not all(map(check_input_format, file_names)):
        file_names_input = input(message)
        file_names = file_names_input.split('/')
    return file_names

if __name__ == "__main__":
    printer = choose_printer()
    for file_name in choose_files():
        message = "Start printing " + file_name
        n = len(message)
        print("="*n)
        print('\n' + message + '\n')
        print("="*n)
        print_settings = choose_print_settings()
        if print_settings == "":
            print_settings = "1x"
        result = 0
        result = print_pdf(get_cours_file_path(file_name), printer, print_settings)
        if result == 0:
            write_impress_datas(file_name, printer, print_settings)
