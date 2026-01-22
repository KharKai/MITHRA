
class DataLoader:
    def __init__(self):
        self.cfg = dict()

    def load_cfg(self, path):
        with open(path, "r") as f:
            data = f.read()

        self.cfg = eval(data)
        return self.cfg


