import requests

import settings
import utils


OVH_API_URL = 'https://ws.ovh.ca/dedicated/r2/ws.dispatcher/getAvailability2'


class AvailabilityService():
    def __init__(self):
        self.data = None
        self.servers = utils.recursive_dict()

    def query_api(self):
        self.data = requests.get(OVH_API_URL, timeout=30).json()

    def parse_data(self):
        offers = self.data.get('answer').get('availability')

        for offer in offers:
            ref = offer.get('reference')
            zones = offer.get('zones')
            server = settings.OFFER_TO_SERVER_MAPPING.get(ref)

            if ref not in settings.OFFER_TO_SERVER_MAPPING:
                continue
            if server not in settings.WATCHED_SERVER_LIST:
                continue

            for zone in zones:
                avail = zone.get('availability')
                dc = zone.get('zone')

                if dc not in settings.WATCHED_DC_LIST:
                    continue

                if avail not in ['unknown', 'unavailable']:
                    self.servers[server][dc] = avail
                else:
                    self.servers[server][dc] = False

    def fetch_available(self, previous_state):
        offers = []

        for server, dcs in self.servers.items():
            for dc, stock in dcs.items():
                if stock is not False:
                    already_avail = False

                    try:
                        already_avail = previous_state.get(server).get(dc)
                    except AttributeError:
                        pass

                    if not already_avail:
                        offers.append({'server': server, 'stock': stock, 'dc': dc.upper()})

        return offers

    def fetch_sold_out(self, previous_state):
        offers = []

        for server, dcs in self.servers.items():
            for dc, stock in dcs.items():
                if stock is False:
                    already_avail = False

                    try:
                        already_avail = previous_state.get(server).get(dc)
                    except AttributeError:
                        pass

                    if already_avail:
                        offers.append({'server': server, 'stock': stock, 'dc': dc.upper()})

        return offers
