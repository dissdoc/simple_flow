import abc
import json

from utils import *


class dotdict(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


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
    def behavior(self):
        if not self.behavior:
            return None

        return Entity.from_data(self.behavior)


class Trigger:
    def __init__(self, entity):
        self._entity = entity
        self._position = -1
        self._is_jump = False

    @property
    def position(self):
        return self._entity.id

    @property
    def jump(self):
        return self._is_jump

    def fire(self, method=None, *args):
        if self._entity is None:
            pass

        elif 'behavior' in self._entity:
            self.fire_behavior(method, *args)

        elif 'children' in self._entity:
            self.fire_children()
            

    def fire_children(self):
        signal = self._message(self._entity)
        callback = self._intent

        messages = filter(lambda x: x is not None,
                          [callback(dotdict(m)) for m in self._entity.children])

        print ('{} ({}):'.format(signal, ', '.join(messages)))

    def fire_behavior(self, method=None, *args):
        behavior = dotdict(self._entity.behavior)

        self._jump(behavior)
        self._method(behavior, method, *args)
        print (self._message(behavior))

    def _message(self, entity):
        return entity.message if 'message' in entity else None

    def _intent(self, entity):
        return entity.intent if 'intent' in entity else None

    def _jump(self, entity):
        if 'path' in entity:
            self._entity.id = entity.path
            self._is_jump = True

    def _method(self, entity, method, *args):
        if not entity.method:
            return
        method(*args)


# class Flow:
#     def __init__(self, data):
#         self._data = dotdict(data)
#         self._current = self._data
#         self._position = -1

#     def __iter__(self):
#         return self

#     def _change_entity(self, param=None, id=None):
#         def _run(data, id):
#             if data.id == id:
#                 return data

#             if 'children' in data:
#                 for ent in data.children:
#                     _entity = dotdict(ent)
#                     result = _run(_entity, id)

#                     if result is None:
#                         continue

#                     return result

#             return None

#         if param:
#             if self.compare_param(self._current, param):
#                 return self._current
#             for item in self._current.children:
#                 _item = dotdict(item)
#                 if not self.compare_param(_item, param):
#                     continue
#                 return _item

#         elif id:
#             return _run(self._data, id)

#         return None

#     def compare_param(self, item, param):
#         if 'list_messages' in item and param in item.list_messages:
#             return True
#         if item.message == param:
#             return True

#         return False

#     def next(self, param=None, method=None, *args):
#         if self._position == 0:
#             raise StopIteration

#         if param:
#             self._current = self._change_entity(param)

#         trigger = Trigger(self._current)

#         if method:
#             trigger.fire(method, *args)
#         else:
#             trigger.fire()

#         self._position = trigger.position

#         if trigger.jump:
#             self._current = self._change_entity(id=self._position)
#             trigger = Trigger(self._current)
#             trigger.fire()

#         return self


def ShowMessage(title, choice_list=None):
    choice_ = '({})'.format(' #'.join(choice_list) if choice_list else '') 
    message = '{} {}'.format(title, choice_)
    print (message)


class Flow:
    def __init__(self, data):
        self._data = data
        self._current_entity = None

        self._cached = Cache.cached(data)

    def __iter__(self):
        return self

    def next(self, intent=None, path=None, method=None, **kwargs):
        if not self._current_entity:
            self._current_entity = Entity.from_data(data)

        r = Responsibility.create()\
                            .add_handler(IntentHandler(intent, self._current_entity))\
                            .add_handler(PathHandler(path, self._current_entity))\
                            .add_handler(MethodHandler(method, **kwargs))  
        r.response(self._cached) 

        return self


if __name__ == '__main__':
    with open('flow.json') as output:
        data = json.loads(output.read())
        flow = Flow(data)

        flow.next()
        # flow.next('ldap')