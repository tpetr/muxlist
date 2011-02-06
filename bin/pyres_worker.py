#!/usr/bin/python

import os, sys
ROOT_PATH = os.path.abspath("%s/.." % os.path.dirname(__file__))

if os.path.join(ROOT_PATH, 'lib/') not in sys.path:
    sys.path.insert(0, os.path.join(ROOT_PATH, 'lib/'))

from pyres.scripts import pyres_worker

if __name__ == '__main__':
    pyres_worker()
