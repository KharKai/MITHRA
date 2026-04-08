import json
import numpy as np
from PyMca5.PyMcaIO import specfilewrapper as Specfile

class DataLoader:
    def __init__(self):
        self.cfg = dict()


    def load_cfg(self, path):
        with open(path, "r") as f:
            self.cfg = json.load(f)
        return self.cfg

    def mca_loader(self, path):
        sf = Specfile.Specfile(path)
        scan = sf[0]
        mca = scan.mca(1)
        return np.array(mca)

# loader = DataLoader()
# cfg = loader.load_cfg("G:\\DATA\\PyCharm Projects\\MITHRA\\core_app\\" + "2026-01-27.cfg")
# print(cfg)
