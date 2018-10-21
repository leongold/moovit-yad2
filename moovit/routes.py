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


def next_weekday_at_8_am_timestamp():
    dt = datetime.datetime.now(pytz.timezone("Asia/Jerusalem"))
    dt = dt.replace(second=0, microsecond=0, minute=0, hour=8)
    weekday = dt + datetime.timedelta(days=_days_delta(dt))
    return calendar.timegm(weekday.timetuple()) * 1000


def ts_repr(ts):
    dt_naive_utc = datetime.datetime.utcfromtimestamp(ts / 1000)
    dt = dt_naive_utc.replace(tzinfo=pytz.timezone("Asia/Jerusalem"))
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def _create_moovit_url(lat_lon_x, lat_lon_y, when):
    xlat, xlon = lat_lon_x
    ylat, ylon = lat_lon_y
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
        attrs = ""

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


def get_routes(lat_lon_x, lat_lon_y, timestamp=None):
    RENDER_SLEEP = 5

    timestamp = timestamp if timestamp else next_weekday_at_8_am_timestamp()
    html_session = HTMLSession()
    response = html_session.get(
        _create_moovit_url(lat_lon_x, lat_lon_y, timestamp)
    )
    response.html.render(sleep=RENDER_SLEEP)
    return _get_routes(response.html.lxml)


def get_routes_proc(lat_lon_x, lat_lon_y, timestamp=None):
    xlat, xlon = lat_lon_x
    ylat, ylon = lat_lon_y
    timestamp = timestamp if timestamp else next_weekday_at_8_am_timestamp()

    proc = subprocess.Popen(
        [os.path.join(os.path.dirname(os.path.realpath(__file__)), __file__),
         str(xlat), str(xlon), str(ylat), str(ylon), str(timestamp)],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    stdout = proc.communicate()[0]
    try:
        decoded = stdout.decode('utf-8')
    except Exception as e:
        raise ValueError("can't decode {}".format(stdout))
    try:
        result = json.loads(decoded.strip().replace('\'', '"'))
    except Exception as e:
        raise ValueError("can't load {}".format(decoded))
    return result


if __name__ == '__main__':
    xlat, xlon, ylat, ylon = sys.argv[1:5]
    try:
        timestamp = sys.argv[5]
    except IndexError:
        timestamp = next_weekday_at_8_am_timestamp()
    print(
        get_routes(
            (float(xlat), float(xlon)),
            (float(ylat), float(ylon)),
            int(timestamp)
        )
    )
