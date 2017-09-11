import time
from settings import settings

time.sleep(1)

sets = settings('19')

while True:
    currentTime = time.time()
    print sets.power + 'p'
    print sets.brightness + ' b'
    print type(sets.brightness)
    time.sleep(1)
