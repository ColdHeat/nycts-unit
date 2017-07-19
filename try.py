import time
from settings import settings

time.sleep(1) # Allow a moment for initial results

sets = settings('19')

while True:
    currentTime = time.time()
    print sets.power + 'p'
    print sets.brightness + ' b'
    print type(sets.brightness)
    time.sleep(1)