from os import environ
import argparse
from pathlib import Path


# Default config options
defaults = {
    'bg_color': '#2e3436', 'btn_color': '#babdb6',
    'media': None, 'show': None,
    'fade_to': 5000, 'fade_in_sp': 0.05, 'fade_out_sp': 0.2, 'max_alpha': 0.6,
    'min_alpha': 0
}

env_name = 'DSIGN_PLAYER_CONFIG'

base_path = Path(__file__).resolve().parent
# Default path to config, should be changed in future
default_conf_path = base_path.joinpath('player.conf')


class Conf():
    '''
    Priority of options, from most to least:
    1. Defaults from this source file are always loaded, then they are
    overrided with:
    2. Config from adhoc argument
    3. Config from env vars
    4. Config from default path
    '''

    def __init__(self):
        for key in list(defaults.keys()):
            setattr(self, key, defaults[key])

        self.get_config()

    def check_path(self, path):
        if path:
            if Path(path).exists():
                return(path)
            elif base_path.joinpath(path).exists():
                return(base_path.joinpath(path))
            else:
                return(None)
        else:
            return(None)

    def parse_config(self, path_to_config):
        with open(path_to_config, 'r') as config:
            for line in config:
                line = line.strip()
                if not(line.startswith('#') or line == ''):
                    key, val = line.split('=')
                    key, val = key.strip(), val.strip()
                    if getattr(self, key, False):
                        if key in ['media', 'show']:
                            val = self.check_path(val)
                            if not val:
                                pass
                        setattr(self, key, val)

    def get_config(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-c', '--config')
        from_adhoc = self.check_path(parser.parse_args().config)
        if from_adhoc:
            print('from_adhoc')
            self.parse_config(from_adhoc)
        else:
            if env_name in environ:
                from_env = self.check_path(environ[env_name])
                if from_env:
                    print('from_env')
                    self.parse_config(from_env)
            else:
                from_default_conf = self.check_path(default_conf_path)
                if from_default_conf:
                    print('from_default_conf')
                    self.parse_config(from_default_conf)
                else:
                    print('from defaults')


if __name__ == "__main__":
    conf = Conf()
    print(conf.__dict__)
