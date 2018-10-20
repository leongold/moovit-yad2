
import logging
import os
import json
import sys

import constants


def setup_logging(module):
    filename = os.path.basename(sys.argv[0]).split('.')[0]
    filepath = os.path.join(constants.ROOT_DIR, 'logs', filename + '.log')

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(message)s',
        handlers=[logging.FileHandler(filepath),
                  logging.StreamHandler()]
    )
    return logging.getLogger(module)


def get_config():
    try:
        cfg_path = sys.argv[1]
    except IndexError:
        cfg_path = os.path.join(constants.ROOT_DIR, 'config')
    with open(cfg_path) as f:
        return json.load(f)
