from django.utils.translation import ugettext_lazy as _

from channels import DEFAULT_CHANNEL_LAYER
from channels.asgi import channel_layers
from channels.routing import Route, Include
from channels.utils import name_that_thing

from debug_toolbar.panels import Panel

from .utils import in_debug, get_consumer_group, is_no_debug
from .settings import get_setting_value


def filters_to_string(filters):
    return ', '.join(['{0}: {1}'.format(f, pattern.pattern) for f, pattern in filters.items()])


def _get_route(route, prefix=None):
    if isinstance(route, Route):
        yield route.channels, route.consumer, route.filters, prefix
    elif isinstance(route, Include):
        for _route in route.routing:
            for route_params in _get_route(_route, route.prefixes):
                yield route_params


def get_routes(layer):
    for route_params in _get_route(channel_layers[layer].router.root):
        yield route_params


class ChannelsDebugPanel(Panel):
    """
    Panel that displays channels events.
    """
    name = 'Channels'
    template = 'channels_panel/channels_panel.html'
    has_content = True

    def nav_title(self):
        return _('Channels Events')

    def nav_subtitle(self):
        return "sub"

    def url(self):
        return ''

    def title(self):
        return self.nav_title()

    def get_context(self):
        consumers = []

        for channels, consumer, filters, prefix in get_routes(DEFAULT_CHANNEL_LAYER):
            if any((in_debug(channel) for channel in channels)):
                name = name_that_thing(consumer)
                if name in 'channels.routing.null_consumer' or is_no_debug(consumer):
                    continue
                consumers.append({
                    'name': name,
                    'channels': channels,
                    'prefix': filters_to_string(prefix),
                    'filters': filters_to_string(filters),
                    'group': get_consumer_group(name),
                })
        return {
            'consumers': consumers,
            'profile': get_setting_value('PROFILE_CONSUMERS'),
        }

    def process_response(self, request, response):
        if hasattr(self, 'record_stats'):
            self.record_stats(self.get_context())
