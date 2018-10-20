#!/usr/bin/python3
from io import BytesIO
import lxml
import logging
import time

import requests
from pyquery import PyQuery as pq

from common import get_config
from common import setup_logging


DATA_GOV = 'https://data.gov.il'
DATASET_URL = '{}/dataset/321'.format(DATA_GOV)

logger = setup_logging(__name__)


def _get_entries(city):
    d = pq(requests.get(DATASET_URL).text)
    xml_dl = '{}{}/download'.format(
        DATA_GOV, d.find('li.resource-item a').attr('href')
    )
    bytes_ = BytesIO(requests.get(xml_dl).content)
    xml = lxml.etree.parse(bytes_)
    root = xml.getroot()
    entries = root.getchildren()
    return [entry.xpath('שם_רחוב')[0].text.strip()
            for entry in entries
            if entry.xpath('שם_ישוב')[0].text.strip() == city]

if __name__ == '__main__':
    config = get_config()
    location =  config['location']
    city = config['data_gov_il_city']
    url = config['url']

    for street in _get_entries(city):
        dst_addr = '{},{}'.format(street, city)

        logger.info('{} -> {}'.format(dst_addr, location))
        requests.post(
            url,
            data={
                'dst_addr': dst_addr,
                'src_addr': location
            }
        )
        time.sleep(20)
