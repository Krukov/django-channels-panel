from django.apps import AppConfig, apps
from django.conf import settings

from channels.asgi import channel_layers
from channels import DEFAULT_CHANNEL_LAYER

from . import routes, GROUP_NAME_CHANNELS
from .utils import debug_decorator, in_debug, is_no_debug, send_debug, is_marked


def layer_factory(base, alias):
    class DebugChannelLayer(base.channel_layer.__class__):

        def send(self, channel, message):
            if in_debug(channel) and not is_marked(message):
                send_debug({'channel': channel, 'layer': alias, 'content': message},
                           'send', GROUP_NAME_CHANNELS)
            return super(DebugChannelLayer, self).send(channel, message)

        def group_add(self, group, channel):
            if in_debug(group, group=True):
                send_debug({'channel': channel, 'group': group, 'layer': alias}, 'add')
            return super(DebugChannelLayer, self).group_add(group, channel)

        def group_discard(self, group, channel):
            if in_debug(group, group=True):
                send_debug({'channel': channel, 'group': group, 'layer': alias}, 'discard')
            return super(DebugChannelLayer, self).group_discard(group, channel)

        def send_group(self, group, message):
            if in_debug(group, group=True):
                send_debug({'content': message, 'group': group, 'layer': alias}, 'send')
            return super(DebugChannelLayer, self).send_group(group, message)

    base.channel_layer = DebugChannelLayer(**getattr(settings, "CHANNEL_LAYERS", {})[alias].get("CONFIG", {}))
    return base


class ChannelsDebugConfig(AppConfig):

    name = "channels_panel"
    verbose_name = "Channels Debug Toolbar Panel"

    def ready(self):
        if not apps.is_installed('debug_toolbar'):
            return

        # patch routes: adding debug routes to default layer
        for route in routes.debug_channel_routes:
            channel_layers[DEFAULT_CHANNEL_LAYER].router.add_route(route)

        # patch layers: substitution by debug layer with events monitoring
        for alias in getattr(settings, "CHANNEL_LAYERS", {}).keys():
            new_backend = layer_factory(channel_layers[alias],  alias)
            channel_layers.set(alias, new_backend)

        # patch routes: wrap routes debug decorator
        for alias in getattr(settings, "CHANNEL_LAYERS", {}).keys():
            _match = channel_layers[alias].router.root.match

            def new_match(message):
                if in_debug(message.channel.name):
                    m = _match(message)
                    if m and not is_no_debug(m[0]):
                        return debug_decorator(m[0], alias), m[1]
                return _match(message)
            channel_layers[alias].router.root.match = new_match

