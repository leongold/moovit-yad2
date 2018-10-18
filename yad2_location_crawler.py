
import json
import os
import sys
import time

import requests
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from pyquery import PyQuery as pq


YAD2_FMT = ('http://www.yad2.co.il/Nadlan/rent.php?AreaID=19&City=&HomeTypeID=1'
            '&fromRooms=&untilRooms=&fromPrice=4500&untilPrice=6500&PriceType=1&FromFloor=&ToFloor=&EnterDate=&Info=')


def crawl(driver, host, dst_addr):
    driver.implicitly_wait(5)
    driver.get(YAD2_FMT)

    document = pq(driver.page_source)
    main_table = document.find("div[id=main_table]")
    items = pq(main_table).find("tr[data-feed-place]")
    for item in items:
        item = pq(item)
        location = item.find('td')[8].text
        location = ','.join([e.strip() for e in location.strip().split('-')])
        requests.post(
            "http://{}".format(host),
            data={'dst_addr': dst_addr, 'src_addr': location}
        )
        time.sleep(15)


if __name__ == '__main__':
    config = json.loads(open('config'))
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
            '{}:{}'.format(config['server'], config['port']),
            config['dst_address']
        )
        time.sleep(600)
