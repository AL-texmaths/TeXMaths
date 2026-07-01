class CodeService:

    def __init__(self, code_labels):

        self.code_labels = code_labels

        self.entries = []

    def display_name(self, code):

        return self.code_labels.get(
            code,
            code
        )

    def internal_name(self, display):

        for code, label in self.code_labels.items():

            if label == display:
                return code

        return display