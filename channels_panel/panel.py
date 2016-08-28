from django.utils.translation import ugettext_lazy as _
from channels import DEFAULT_CHANNEL_LAYER
from channels.utils import name_that_thing
from debug_toolbar.panels import Panel

from .utils import get_routes, in_debug, get_consumer_group
from .settings import get_setting_value


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
                consumers.append({
                    'name': name,
                    'prefix': prefix,
                    'channels': channels,
                    'filters': filters,
                    'group': get_consumer_group(name),
                })
        return {
            'consumers': consumers,
            'profile': get_setting_value('PROFILE_CONSUMERS'),
        }

    def process_response(self, request, response):
        if hasattr(self, 'record_stats'):
            self.record_stats(self.get_context())
