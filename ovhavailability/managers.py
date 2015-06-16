import os.path

import utils


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_FILENAME = os.path.join(BASE_DIR, 'state.pickle')


class StateManager():
    def __init__(self):
        self.state = {}
        self.filename = SAVE_FILENAME

    def load_state(self):
        self.state = utils.load_file(self.filename)

    def update_state(self, servers):
        self.state = utils.recursive_dict()

        for server, dcs in servers.items():
            for dc, time in dcs.items():
                self.state[server][dc] = (time is not False)

    def save_state(self):
        utils.save_file(self.state, self.filename)
