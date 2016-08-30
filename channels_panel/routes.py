from channels.generic.websockets import WebsocketConsumer

from . import GROUP_NAME_CHANNELS, GROUP_NAME_GROUPS, GROUP_PREFIX, _MARK


def no_debug(consumer):
    setattr(consumer, _MARK, True)
    return consumer


@no_debug
class DebugGroupsConsumer(WebsocketConsumer):

    def connection_groups(self, group, **kwargs):
        if group and group.startswith(GROUP_PREFIX) or group in (GROUP_NAME_GROUPS, GROUP_NAME_CHANNELS):
            return [group, ]
        return []


debug_channel_routes = [
    DebugGroupsConsumer.as_route(path='^/__debug__/join/(?P<group>[^/]+)/?$')
]
