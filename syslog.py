#!/usr/bin/env python

import os
import sys
import subprocess
import collections
import time
import mmap

try:

    LOG_FILE = os.path.abspath(sys.argv[1])
    WATCH_FOR = sys.argv[2]

except:

    sys.stderr.write(
        'Usage: %s [log file] [string to watch for]' % sys.argv[0])
    sys.exit(1)

def action():

    # if 'beep' in sys.argv:

    #     subprocess.Popen(['paplay', '/usr/share/sounds/ubuntu/notifications/Mallet.ogg'])

    if 'notify' in sys.argv:

        subprocess.Popen(['notify-send', 'LogMonitor', 'Found!'])

    print(time.strftime('%Y-%m-%d %I:%M:%S %p'), 'Found! \n', i)

# basic Python implementation of Unix tail

def tail(file, n):

    with open(file, "r") as f:

        f.seek (0, 2)           # Seek @ EOF
        fsize = f.tell()        # Get Size
        f.seek (max (fsize-1024, 0), 0) # Set pos @ last n chars
        lines = f.readlines()       # Read to end

    lines = lines[-n:]    # Get last 10 lines

    return lines


print(
    'Watching of ' + LOG_FILE + ' for ' + WATCH_FOR +
    ' started at ' + time.strftime('%Y-%m-%d %I:%M:%S %p'))

mtime_last = 0

while True:

    mtime_cur = os.path.getmtime(LOG_FILE)

    if mtime_cur != mtime_last:

        for i in tail(LOG_FILE, 5):

            if WATCH_FOR.lower() in i.lower():

                action()

    mtime_last = mtime_cur

    time.sleep(5)