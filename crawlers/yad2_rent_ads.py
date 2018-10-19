#!/usr/bin/python3
import json
import logging
import os
import sys
import time

import requests
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from pyquery import PyQuery as pq

from common import get_config
from common import setup_logging

cache = set()


def _get_location(item):
    location = item.find('td')[8].text
    return ','.join([e.strip() for e in location.strip().split('-')])


def crawl(driver, url, dst_location, params):
    global cache

    logging.info('crawling...')
    yad2_url = 'http://www.yad2.co.il/Nadlan/rent.php?' + params
    for page in range(1, 5):
        yad2_url += '&Page=' + page
        driver.get(yad2_url)
        driver.implicitly_wait(10)

        document = pq(driver.page_source)
        main_table = document.find("div[id=main_table]")

        items = pq(main_table).find("tr[data-feed-place]")
        if not items:
            logging.warning('no locations, yad2 url: ' + yad2_url)
            continue

        src_locations = [_get_location(pq(item)) for item in items]
        logging.debug('src_locations: {}'.format(src_locations))

        for src_location in src_locations:
            if src_location in cache:
                continue
            cache.add(src_location)
            requests.post(
                url,
                data={'dst_addr': dst_location, 'src_addr': src_location}
            )
            time.sleep(20)


if __name__ == '__main__':
    setup_logging()
    config = get_config()
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(
        executable_path=os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'chromedriver'
        ),
        chrome_options=chrome_options
    )

    while True:
        crawl(
            driver,
            config['url'],
            config['location'],
            config['yad2_rent_ads_params']
        )
        time.sleep(600)
