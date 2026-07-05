import subprocess
from shutil import which
print("magick path = ", which('magick'))
result = subprocess.run(['magick', '-version'], check=True)
print("result = ", result)