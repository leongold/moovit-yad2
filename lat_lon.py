
import json

from requests_html import HTMLSession


MAPA_FMT = ("http://www.mapa.co.il/gnet/maps/handlers/ServerSide.ashx?"
            "request_type=point_by_address&address={}")


def get_lat_lon(addr):
    url = MAPA_FMT.format(addr)
    html_session = HTMLSession()
    response = html_session.get(url)
    data = json.loads(response.text)['point']
    return data['Lat'], data['Lon']
