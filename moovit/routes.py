#!/usr/bin/python3
import calendar
import datetime
import os
import pytz
import json
import sys
import subprocess
import traceback

from requests_html import HTMLSession

try:
    from moovit.lat_lon import get_lat_lon
except ModuleNotFoundError:
    sys.path.append(
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            '..'
            )
        )
    from moovit.lat_lon import get_lat_lon


MOOVIT_FMT = (
    "https://moovit.com/?from=0&to=1&fll={xlat}_{xlon}&"
    "tll={ylat}_{ylon}&timeType=depart&time={when}&metroId=1&lang=en"
)


def _days_delta(dt):
    # monday = 1
    # ...
    # sunday = 7
    isoweekday = dt.isoweekday()
    if isoweekday in (4, 5):
        return 7 - isoweekday
    return 1


def _rounded_millisecond_timestamp():
    dt = datetime.datetime.now(pytz.timezone("Asia/Jerusalem"))
    dt.replace(second=0, microsecond=0, minute=0, hour=8)
    weekday = dt + datetime.timedelta(days=_days_delta(dt))
    return calendar.timegm(weekday.timetuple()) * 1000


def _create_moovit_url(addr_x, addr_y):
    xlat, xlon = get_lat_lon(addr_x)
    ylat, ylon = get_lat_lon(addr_y)
    when = _rounded_millisecond_timestamp()
    return MOOVIT_FMT.format(
        xlat=xlat, xlon=xlon,
        ylat=ylat, ylon=ylon,
        when=when
    )


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
    try:
        suggested_routes = root.xpath('//div[@class="suggested-routes"]')[0]
    except IndexError:
        return [["no data", []]]
    md_list = suggested_routes.xpath('md-list')[0]
    routes = md_list.xpath('md-list-item')
    return [_get_route(route.xpath('button/div/route-summary')[0])
            for route in routes]


def get_routes(addr_x, addr_y):
    RENDER_SLEEP = 5

    html_session = HTMLSession()
    response = html_session.get(_create_moovit_url(addr_x, addr_y))
    response.html.render(sleep=RENDER_SLEEP)
    return _get_routes(response.html.lxml)


def get_routes_proc(addr_x, addr_y):
    proc = subprocess.Popen(
        [os.path.join(os.path.dirname(os.path.realpath(__file__)), __file__),
         addr_x, addr_y],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    stdout = proc.communicate()[0]
    try:
        decoded = stdout.decode('utf-8')
    except Exception as e:
        raise ValueError("can't decode {}: {}".format(stdout, str(e)))
    try:
        result = json.loads(decoded.strip().replace('\'', '"'))
    except Exception as e:
        raise ValueError("can't json.load {}: {}".format(decoded, str(e)))
    return result


if __name__ == '__main__':
    addr_x = sys.argv[1]
    addr_y = sys.argv[2]
    print(get_routes(addr_x, addr_y))
