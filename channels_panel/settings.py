from . import GROUP_PREFIX
from django.conf import settings

DEFAULTS = {
    'ONLY_CHANNELS': None,
    'EXCLUDE_CHANNELS': ['http.*', ],
    'ONLY_GROUPS': None,
    'EXCLUDE_GROUPS': [GROUP_PREFIX + '.*'],
    'PROFILE_CONSUMERS': False,
}


def get_setting_value(name):
    name = name.upper()
    if name in DEFAULTS:
        return getattr(settings, 'CHANNELS_PANEL', {}).get(name, DEFAULTS[name])
    raise ValueError("%s not in debug_channels_panel settings")
