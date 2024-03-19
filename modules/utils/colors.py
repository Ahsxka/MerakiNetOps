class colors:
    RESET = '\033[0m'
    ROUGE = '\033[91m'
    VERT = '\033[92m'
    JAUNE = '\033[93m'
    BLEU = '\033[94m'


class color_format:
    @staticmethod
    def print_error(message, end='\n'):
        print(f"{colors.ROUGE}Error   : {message}{colors.RESET}", end=end)

    @staticmethod
    def print_success(message, end='\n'):
        print(f"{colors.VERT}Succes  : {message}{colors.RESET}", end=end)

    @staticmethod
    def print_warning(message, end='\n'):
        print(f"{colors.JAUNE}Warning : {message}{colors.RESET}", end=end)

    @staticmethod
    def print_info(message, end='\n'):
        print(f"{colors.BLEU}Info    : {message}{colors.RESET}", end=end)

    @staticmethod
    def prsep(end='\n'):
        print(f"{80 * "-"}", end=end)