import os
from platform import node

from base import *

try:
    module_name = node().lower().replace('.', '_')
    local_settings = getattr(__import__('settings.%s' % module_name), module_name)
    for attr in local_settings.__ALL__:
        globals()[attr] = getattr(local_settings, attr)
except:
    pass
