import abc


__all__ = ['IntentHandler', 'Cache', 'Message']


def Message(entity):
    if not hasattr(entity, 'message') or not entity.message:
        return ''

    nodes = entity.nodes
    if nodes:
        choice_list = [c.intent for c in nodes]
        choice_ = '(#{})'.format(' #'.join(choice_list) if choice_list else '')
    else:
        choice_ = ''
    
    return '{} {}'.format(entity.message, choice_)


class Cache:
    def __init__(self, collection):
        self._collection = collection

    @classmethod
    def cached(cls, data):
        def iteration(collection, _data):
            for key, value in _data.items():
                if key == 'id':
                    collection[value] = _data
                elif key == 'children':
                    for el in value:
                        iteration(collection, el)

        collection = {}
        iteration(collection, data)

        return cls(collection)

    def item(self, id):
        if id not in self._collection:
            return None

        return self._collection[id]


class Handler:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def handle(self):
        return


class IntentHandler(Handler):
    def __init__(self, intent, entity):
        self._intent = intent
        self._entity = entity

    def handle(self):
        if not self._intent:
            return None

        for c in self._entity.nodes:
            if not hasattr(c, 'intent') or not c.intent:
                continue

            if c.intent == self._intent:
                return c
     
        return None
