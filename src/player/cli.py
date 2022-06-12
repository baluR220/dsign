from os import environ
import argparse


# Default config options
defaults = {
    'bg_color': '#2e3436', 'btn_color': '#babdb6', 'media': '', 'show': '',
    'fade_to': 5000, 'fade_in_sp': 0.05, 'fade_out_sp': 0.2, 'max_alpha': 0.6,
    'min_alpha': 0
}


class Conf():
    def __init__(self):
        for key in list(defaults.keys()):
            setattr(self, key, defaults[key])
