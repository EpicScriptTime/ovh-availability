import requests
# import pprint

import mapping
import settings
import utils


OVH_API_URL = 'https://ws.ovh.ca/dedicated/r2/ws.dispatcher/getAvailability2'


def query_api():
    return requests.get(OVH_API_URL, timeout=30).json()


def parse_data(data):
    offers = data.get('answer').get('availability')
    servers = utils.recursive_dict()

    for offer in offers:
        ref = offer.get('reference')
        zones = offer.get('zones')
        server = mapping.OFFER_TO_SERVER_MAPPING.get(ref)

        if ref not in mapping.OFFER_TO_SERVER_MAPPING:
            continue
        if server not in settings.WATCHED_SERVER_LIST:
            continue

        for zone in zones:
            avail = zone.get('availability')
            dc = zone.get('zone')

            if dc not in settings.WATCHED_DC_LIST:
                continue

            if avail not in ['unknown', 'unavailable']:
                servers[server][dc] = avail
            else:
                servers[server][dc] = False

    return servers


def fetch_avails(servers, previous_state):
    avails = []

    for server, dcs in servers.items():
        for dc, stock in dcs.items():
            if stock is not False:
                already_avail = False

                try:
                    already_avail = previous_state.get(server).get(dc)
                except AttributeError:
                    pass

                if not already_avail:
                        avails.append({'server': server, 'stock': stock, 'dc': dc.upper()})

    return avails


def update_state(servers):
    state = utils.recursive_dict()

    for server, dcs in servers.items():
        for dc, time in dcs.items():
            state[server][dc] = (time is not False)

    return state


def main():
    data = query_api()
    # data = load_state(filename='data.pickle')

    servers = parse_data(data)
    # pprint.pprint(servers)

    previous_state = utils.load_state()
    # pprint.pprint(previous_state)

    avails = fetch_avails(servers, previous_state)
    # pprint.pprint(avails)

    for avail in avails:
        message = '{} is now available in {} at {}'.format(avail['server'], avail['stock'], avail['dc'])
        print(message)
        # utils.send_sms('OVH-Availability: {}'.format(message))

    state = update_state(servers)
    # pprint.pprint(state)

    utils.save_state(state)
    # utils.save_state(data, filename='data.pickle')


if __name__ == '__main__':
    main()
