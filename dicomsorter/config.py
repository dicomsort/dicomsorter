import logging
import sys

DEFAULTS = {
    'filename_format': '%(ImageType)s (%(InstanceNumber)04d)%(Extension)s',
    'path': ['SeriesDescription'],
    'concurrency': 2
}

logger = logging.getLogger('dicomsorter')
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)
