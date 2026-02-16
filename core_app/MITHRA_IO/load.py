import json


class DataLoader:
    def __init__(self):
        self.cfg = dict()


    def load_cfg(self, path):
        with open(path, "r") as f:
            self.cfg = json.load(f)
        return self.cfg

# loader = DataLoader()
# cfg = loader.load_cfg("G:\\DATA\\PyCharm Projects\\MITHRA\\core_app\\" + "2026-01-27.cfg")
# print(cfg)
