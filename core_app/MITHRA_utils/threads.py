from PyQt5.QtCore import *
from PyQt5.QtGui import *

class ThreadSignals(QObject):
    started = pyqtSignal(int)
    line_finished = pyqtSignal(int, int)
    progress = pyqtSignal(object)
    completed = pyqtSignal()
    distance = pyqtSignal(float)
    webcam_update = pyqtSignal(QImage)

class ThreadPoint(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(ThreadPoint, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = ThreadSignals()
        self.kwargs['xrf_point'] = self.signals.progress

    @pyqtSlot()
    def run(self):
        self.fn(*self.args, **self.kwargs)


class ThreadMap(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(ThreadMap, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = ThreadSignals()
        self.kwargs['data_point'] = self.signals.progress
        self.kwargs['line_finished'] = self.signals.line_finished
        self.kwargs['acquisition_completed'] = self.signals.completed

    @pyqtSlot()
    def run(self):
        self.fn(*self.args, **self.kwargs)


class ThreadLaser(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(ThreadLaser, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = ThreadSignals()
        self.kwargs['distance'] = self.signals.distance

    @pyqtSlot()
    def run(self):
        self.fn(*self.args, **self.kwargs)


class ThreadWebcam(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(ThreadWebcam, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = ThreadSignals()
        self.kwargs['frame'] = self.signals.webcam_update

    @pyqtSlot()
    def run(self):
        self.fn(*self.args, **self.kwargs)