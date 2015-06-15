import os.path
import requests
import pickle
# import pprint

from twilio import TwilioRestException
from twilio.rest import TwilioRestClient
from collections import defaultdict


# Customize your Twilio settings for SMS notification
TWILIO = {
    'ACCOUNT_SID': '',
    'AUTH_TOKEN': '',
    'FROM': '',
    'TO': '',
}

# Customize the list of watched DCs
WATCHED_DC_LIST = [
    # 'gra',
    # 'rbx-hz',
    # 'sbg',
    # 'rbx',
    # 'bhs',
]

# Customize the list of watched servers
WATCHED_SERVER_LIST = [
    # 'KS-1',
    # 'KS-2',
    # 'KS-3',
    # 'KS-4',
    # 'KS-5A',
    # 'KS-5B',
    # 'SYS-IP-1',
    # 'E3-SAT-1',
    # 'E3-SSD-1',
    # 'SYS-IP-2',
    # 'E3-SAT-2',
    # 'E3-SSD-2',
    # 'E3-SAT-3',
    # 'E3-SSD-3',
    # 'SYS-IP-4',
    # 'E3-SAT-4',
    # 'E3-SSD-4',
    # 'BK-8T',
    # 'SYS-IP-5',
    # 'SYS-IP-5S',
    # 'BK-24T',
    # 'SYS-IP-6',
    # 'SYS-IP-6S',
]

OFFER_TO_SERVER_MAPPING = {
    '142cask9':   'KS-1',
    '142cask2':   'KS-2',
    '142cask3':   'KS-3',
    '142cask4':   'KS-4',
    '142cask5':   'KS-5A',
    '142cask8':   'KS-5B',
    '142casys4':  'SYS-IP-1',
    '143casys4':  'E3-SAT-1',
    '143casys13': 'E3-SSD-1',
    '142casys5':  'SYS-IP-2',
    '143casys1':  'E3-SAT-2',
    '143casys10': 'E3-SSD-2',
    '143casys2':  'E3-SAT-3',
    '143casys11': 'E3-SSD-3',
    '142casys8':  'SYS-IP-4',
    '143casys3':  'E3-SAT-4',
    '143casys12': 'E3-SSD-4',
    '141cabk1':   'BK-8T',
    '142casys6':  'SYS-IP-5',
    '142casys10': 'SYS-IP-5S',
    '141cabk2':   'BK-24T',
    '142casys7':  'SYS-IP-6',
    '142casys9':  'SYS-IP-6S',
}

OVH_API_URL = 'https://ws.ovh.ca/dedicated/r2/ws.dispatcher/getAvailability2'

PATH = os.path.dirname(os.path.abspath(__file__))

SAVE_FILENAME = PATH + '/state.pickle'


def query_api():
    return requests.get(OVH_API_URL, timeout=30).json()


def send_sms(body):
    try:
        client = TwilioRestClient(TWILIO['ACCOUNT_SID'], TWILIO['AUTH_TOKEN'])
        message = client.messages.create(body=body, to=TWILIO['TO'], from_=TWILIO['FROM'])
        return message.sid
    except TwilioRestException as e:
        raise e


def load_state(filename=SAVE_FILENAME):
    state = {}

    if os.path.isfile(filename):
        stream = open(filename, 'rb')
        state = pickle.load(stream)
        stream.close()

        if not isinstance(state, dict):
            state = {}

    return state


def save_state(state, filename=SAVE_FILENAME):
    stream = open(filename, 'wb')
    pickle.dump(state, stream)
    stream.close()


def multilevel_dict():
    return defaultdict(multilevel_dict)


def parse_data(data):
    offers = data.get('answer').get('availability')
    servers = multilevel_dict()

    for offer in offers:
        ref = offer.get('reference')
        zones = offer.get('zones')
        server = OFFER_TO_SERVER_MAPPING.get(ref)

        if ref not in OFFER_TO_SERVER_MAPPING:
            continue
        if server not in WATCHED_SERVER_LIST:
            continue

        for zone in zones:
            avail = zone.get('availability')
            dc = zone.get('zone')

            if dc not in WATCHED_DC_LIST:
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
                if previous_state.get(server) is not True:
                    avails.append({'server': server, 'stock': stock, 'dc': dc.upper()})

    return avails


def update_state(servers):
    state = {}

    for server, dcs in servers.items():
        for dc, time in dcs.items():
            if time is not False:
                state[server] = True
            else:
                state[server] = False

    return state


def main():
    data = query_api()
    # data = load_state(filename='data.pickle')

    servers = parse_data(data)
    # pprint.pprint(servers)

    previous_state = load_state()
    # pprint.pprint(previous_state)

    avails = fetch_avails(servers, previous_state)
    # pprint.pprint(avails)

    for avail in avails:
        message = '{} is now available in {} at {}'.format(avail['server'], avail['stock'], avail['dc'])
        print(message)
        # send_sms('OVH-Availability: ' + message)

    state = update_state(servers)
    # pprint.pprint(state)

    save_state(state)
    # save_state(data, filename='data.pickle')


if __name__ == '__main__':
    main()
