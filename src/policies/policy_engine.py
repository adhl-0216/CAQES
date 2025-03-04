class QuarantinePolicy:
    def __init__(self):
        self.name = ""
        self.description = ""
        self.rules = []

    def evaluate(self, alert):
        raise NotImplementedError
