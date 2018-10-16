#!/usr/bin/python3
import datetime
import json
import sys

from requests_html import HTMLSession

from lat_lon import get_lat_lon


MOOVIT_FMT = (
    "https://moovit.com/?from=0&to=1&fll={xlat}_{xlon}&"
    "tll={ylat}_{ylon}&timeType=depart&time={when}&metroId=1&lang=en"
)


def _create_moovit_url(addr_x, addr_y):
    xlat, xlon = get_lat_lon(addr_x)
    ylat, ylon = get_lat_lon(addr_y)
    when = _closest_next_weekday_at_10()
    return MOOVIT_FMT.format(
        xlat=xlat, xlon=xlon,
        ylat=ylat, ylon=ylon,
        when=when
    )


def _closest_next_weekday_at_10():
    today = datetime.date.today()
    today_at_10 = datetime.datetime(
        today.year, today.month, today.day, 10, 0
    )
    # monday = 1
    # ...
    # sunday = 7
    isoweekday = today_at_10.isoweekday()
    if today_at_10.isoweekday() in (4, 5):
        delta = 7 - isoweekday
    else:
        delta = 1
    return int((today_at_10 + datetime.timedelta(days=delta)).timestamp())


def _process_leg_type(leg_type):
    try:
        # walk
        data = leg_type.xpath('span')[0]
        type_ = 'walk'
    except IndexError:
        # bus/train
        data = leg_type.xpath('line-svg/div/div/div/span')
        if data[0].get('class') == 'transit':
            type_ = 'bus'
        else:
            type_ = 'train'

    if type_ == 'bus':
        attrs = '/'.join([e.text for e in data[1::2]])
    elif type_ == 'walk':
        attrs = data.text
    else:
        attrs = None

    return [type_, attrs]


def _get_route(route_summary):
    data = route_summary.xpath('div')[0]

    route_time_cls = data.xpath('div[@class="route-time"]')[0]
    route_time = route_time_cls.xpath('span')[0].text

    legs_cls = data.xpath('div[contains(@class, "legs")]')[0]
    legs_types = legs_cls.xpath('div[@class="legs-types"]')[0].xpath('span')

    return [route_time, [_process_leg_type(leg) for leg in legs_types]]


def _get_routes(root):
    suggested_routes = root.xpath('//div[@class="suggested-routes"]')[0]
    md_list = suggested_routes.xpath('md-list')[0]
    routes = md_list.xpath('md-list-item')
    return [_get_route(route.xpath('button/div/route-summary')[0])
            for route in routes]


def get_routes(addr_x, addr_y):
    RENDER_SLEEP = 2

    html_session = HTMLSession()
    response = html_session.get(_create_moovit_url(addr_x, addr_y))
    response.html.render(sleep=RENDER_SLEEP)
    return _get_routes(response.html.lxml)


if __name__ == '__main__':
    addr_x = sys.argv[1]
    addr_y = sys.argv[2]
    try:
        print(json.dumps(get_routes(addr_x, addr_y)))
    except:
        print(_create_moovit_url(addr_x, addr_y))
