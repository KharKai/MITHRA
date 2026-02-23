import seabreeze
seabreeze.use('pyseabreeze')
from seabreeze.spectrometers import list_devices, Spectrometer

spec = Spectrometer.from_first_available()
print(spec)