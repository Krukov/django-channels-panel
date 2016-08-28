import json
import fnmatch
import hashlib
import traceback
from functools import wraps

from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings

from channels import Group, DEFAULT_CHANNEL_LAYER
from channels.asgi import channel_layers
from channels.routing import Route, Include
from channels.utils import name_that_thing

from . import GROUP_NAME_GROUPS, GROUP_NAME_CHANNELS, GROUP_PREFIX
from .settings import get_setting_value


class MessageJSONEncoder(DjangoJSONEncoder):

    def default(self, o):
        if isinstance(o, bytes):
            return o.decode('utf-8')
        return super(MessageJSONEncoder, self).default(o)


def send_debug(data, event, group=GROUP_NAME_GROUPS):
    Group(group).send({'text': json.dumps({'data': data, 'event': event}, cls=MessageJSONEncoder)})


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


def layer_factory(base, alias):
    class DebugChannelLayer(base.channel_layer.__class__):

        def send(self, channel, message):
            if in_debug(channel):
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


def debug_decorator(consumer, alias):
    @wraps(consumer)
    def _consumer(message, *args, **kwargs):
        if in_debug(message.channel.name):
            name = name_that_thing(consumer)
            group = get_consumer_group(name)
            info = {
                'layer': alias,
                'channel': message.channel.name,
                'consumer': name,
                'call_args': args,
                'call_kwargs': kwargs,
                'message': message.content,
            }

            try:
                consumer(message, *args, **kwargs)
            except Exception:
                info['traceback'] = traceback.format_exc()
                send_debug(info, 'error', group)
                raise
            else:
                send_debug(info, 'run', group)
            return
        return consumer(message, *args, **kwargs)
    return _consumer


def in_debug(name, group=False):
    only = get_setting_value('ONLY_GROUPS' if group else 'ONLY_CHANNELS')
    exclude = get_setting_value('EXCLUDE_GROUPS' if group else 'EXCLUDE_CHANNELS')
    if only:
        if any(fnmatch.fnmatchcase(name, pattern) for pattern in only):
            return True
        return False
    if exclude:
        if not any(fnmatch.fnmatchcase(name, pattern) for pattern in exclude):
            return True


def md5(message):
    _md5 = hashlib.md5()
    _md5.update(message.encode())
    return _md5.hexdigest()


def get_consumer_group(consumer, layer=DEFAULT_CHANNEL_LAYER):
    return '.'.join([GROUP_PREFIX, layer, md5(consumer)])
