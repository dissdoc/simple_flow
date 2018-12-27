import abc
import json

from utils import *


class Entity:
    def __init__(self):
        self._cached_children = []

    @classmethod
    def from_data(cls, data):
        instance = cls()

        for key, value in data.items():          
            setattr(instance, key, value)   

        if not hasattr(instance, 'children'):
            setattr(instance, 'children', None)

        if not hasattr(instance, 'behavior'):
            setattr(instance, 'behavior', None)

        return instance

    @property
    def nodes(self): 
        if not self.children:
            return None
        
        for item in self.children:
            self._cached_children.append(
                Entity.from_data(item)
            )

        return self._cached_children

    @property
    def action(self):
        if not self.behavior:
            return None

        return Entity.from_data(self.behavior)


class Flow:
    def __init__(self, data):
        self._data = data
        self._current_entity = None
        self._message_stack = []

        self._cached = Cache.cached(data)

    def __iter__(self):
        return self

    def message(self):
        for m in self._message_stack:
            print(m)

        self._message_stack = []

    def _handle_method(self, method, *args):
        if hasattr(self._current_entity, 'method') and self._current_entity.method:
            method(*args)

    def _handle_behavior(self):
        if self._current_entity.action:
            behavior = self._current_entity.action
            if hasattr(behavior, 'path'):
                item = self._cached.item(behavior.path)
                if item:
                    self._current_entity = Entity.from_data(item)
            if hasattr(behavior, 'message'):
                self._message_stack.append(Message(behavior))


    def next(self, intent=None, method=None, *args):
        if not self._current_entity:
            self._current_entity = Entity.from_data(data)

        if method:
            method(*args)
        
        if intent:
            handler = IntentHandler(intent, self._current_entity)
            self._current_entity = handler.handle()            

        self._handle_behavior()
        self._handle_method(method, *args)

        self._message_stack.append(Message(self._current_entity))

        return self


def simple(id):
    print ('!!!!{}'.format(id))

if __name__ == '__main__':
    with open('flow.json') as output:
        data = json.loads(output.read())
        flow = Flow(data)

        flow.next()
        flow.message()
        # flow.next(intent='ldap')
        # flow.message()
        # flow.next(intent='create user')
        # flow.message()
        flow.next("msgraph", simple, 1)
        flow.message()
