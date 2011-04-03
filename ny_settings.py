try:
    from settings import *
except ImportError:
    import sys
    sys.stderr.write("Unable to read settings.py\n")
    sys.exit(1)

SITE_ID = 4
