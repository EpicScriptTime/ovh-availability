import os.path
import pprint
import pickle
import collections
import datetime

from twilio import TwilioRestException
from twilio.rest import TwilioRestClient

import settings


# http://stackoverflow.com/a/18376589
class PrettyDefaultDict(collections.defaultdict):
    __repr__ = dict.__repr__


# http://stackoverflow.com/a/21465442
def recursive_dict():
    return PrettyDefaultDict(recursive_dict)


def load_file(filename):
    data = {}

    if os.path.isfile(filename):
        stream = open(filename, 'rb')
        data = pickle.load(stream)
        stream.close()

        if not isinstance(data, dict):
            data = {}

    return data


def save_file(data, filename):
    stream = open(filename, 'wb')
    pickle.dump(data, stream)
    stream.close()


def print_debug(var):
    if not settings.QUIET:
        if settings.DEBUG:
            pprint.pprint(var)


def print_info(var):
    if not settings.QUIET:
        print(var)


def send_sms(body):
    try:
        client = TwilioRestClient(settings.TWILIO['ACCOUNT_SID'], settings.TWILIO['AUTH_TOKEN'])
        message = client.messages.create(body=body, to=settings.TWILIO['TO'], from_=settings.TWILIO['FROM'])
        return message.sid
    except TwilioRestException as e:
        raise e


def get_current_timestamp():
    return datetime.datetime.now().strftime('%y%m%d%H%M%S')


def notify(message):
    send_sms('OVH-AVAILABILITY: {} ({})'.format(message, get_current_timestamp()))
