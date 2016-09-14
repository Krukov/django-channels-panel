import json
import fnmatch
import hashlib
import traceback
from functools import wraps

from django.core.serializers.json import DjangoJSONEncoder

from channels import Group, DEFAULT_CHANNEL_LAYER
from channels.utils import name_that_thing

from . import GROUP_NAME_GROUPS, GROUP_PREFIX, _MARK
from .settings import get_setting_value


class MessageJSONEncoder(DjangoJSONEncoder):

    def default(self, o):
        if isinstance(o, bytes):
            return o.decode('utf-8')
        return super(MessageJSONEncoder, self).default(o)


def send_debug(data, event, group=GROUP_NAME_GROUPS):
    Group(group).send({'text': json.dumps({'data': data, 'event': event, _MARK: _MARK}, cls=MessageJSONEncoder)})


def is_marked(message):
    if 'text' in message:
        try:
            return json.loads(message['text']).get(_MARK, None) == _MARK
        except ValueError:
            return False


def debug_decorator(consumer, alias):
    @wraps(consumer)
    def _consumer(message, *args, **kwargs):
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
            result = consumer(message, *args, **kwargs)
        except Exception:
            info['message'] = traceback.format_exc()
            send_debug(info, 'error', group)
            raise
        else:
            send_debug(info, 'run', group)
            return result
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


def is_no_debug(consumer):
    return getattr(consumer, _MARK, False)
