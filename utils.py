import abc


__all__ = ['IntentHandler', 'PathHandler', 'MethodHandler', 'Responsibility', 'Cache']


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

        for c in self._entity.children:
            if not hasattr(c, 'intent') or not c.intent:
                continue

            if c.intent == self._intent:
                return c
        
        return None


class PathHandler(Handler):
    def __init__(self, path, data):
        self._path = path
        self._data = data

    def handle(self):
        pass


class MethodHandler(Handler):
    def __init__(self, method, **kwargs):
        self._method = method

    def handle(self):
        pass


class Responsibility:
    def __init__(self):
        self._handlers = []

    @classmethod
    def create(cls):
        return cls()

    def add_handler(self, h):
        self._handlers.append(h)
        return self

    def response(self, cached):
        for h in self._handlers:
            i = h.handle()
            if i:
                print ('l')
        
        else:
            return None