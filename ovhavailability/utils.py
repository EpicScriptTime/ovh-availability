import os.path
import pickle
import collections

from twilio import TwilioRestException
from twilio.rest import TwilioRestClient

import settings


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SAVE_FILENAME = os.path.join(BASE_DIR, 'state.pickle')


# http://stackoverflow.com/a/18376589
class PrettyDefaultDict(collections.defaultdict):
    __repr__ = dict.__repr__


# http://stackoverflow.com/a/21465442
def recursive_dict():
    return PrettyDefaultDict(recursive_dict)


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


def send_sms(body):
    try:
        client = TwilioRestClient(settings.TWILIO['ACCOUNT_SID'], settings.TWILIO['AUTH_TOKEN'])
        message = client.messages.create(body=body, to=settings.TWILIO['TO'], from_=settings.TWILIO['FROM'])
        return message.sid
    except TwilioRestException as e:
        raise e
