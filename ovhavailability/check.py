import sys
import getopt

import settings
import utils

from utils import print_debug, print_info
from services import AvailabilityService


sold_out = False
dry_run = False


def update_state(servers):
    state = utils.recursive_dict()

    for server, dcs in servers.items():
        for dc, time in dcs.items():
            state[server][dc] = (time is not False)

    return state


def perform_check():
    if dry_run:
        print_info('Running check.py in dry run (not sending any SMS)')

    service = AvailabilityService()

    service.query_api()
    # data = load_state(filename='data.pickle')

    service.parse_data()
    print_debug(service.servers)

    previous_state = utils.load_state()
    print_debug(previous_state)

    offers = service.fetch_available(previous_state)
    print_debug(offers)

    for offer in offers:
        message = '{} is now available in {} at {}.'.format(offer['server'], offer['stock'], offer['dc'])
        print_info(message)
        if not dry_run:
            utils.notify(message)

    if sold_out:
        offers = service.fetch_sold_out(previous_state)
        print_debug(offers)

        for offer in offers:
            message = '{} is no longer available at {}.'.format(offer['server'], offer['dc'])
            print_info(message)
            if not dry_run:
                utils.notify(message)

    state = update_state(service.servers)
    print_debug(state)

    utils.save_state(state)
    # utils.save_state(data, filename='data.pickle')


def main():
    opts, args = getopt.getopt(sys.argv[1:], 's:n:v:q', ['sold-out', 'dry-run', 'debug', 'quiet'])

    global sold_out, dry_run

    for opt in opts:
        if opt[0] in ('-s', '--sold-out'):
            sold_out = True
        elif opt[0] in ('-n', '--dry-run'):
            dry_run = True
        elif opt[0] in ('-d', '--debug'):
            settings.DEBUG = True
        elif opt[0] in ('-q', '--quiet'):
            settings.QUIET = True

    perform_check()


if __name__ == '__main__':
    main()
