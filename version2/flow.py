from version2.store import Entity
from version2.store import Originator
from version2.core.creators import PathManager
from version2.core.creators import Generator


class BackCommandHandler:
    def __init__(self):
        self._back = False

    def back(self):
        self._back = True

    def reback(self):
        self._back = False

    def is_back(self):
        return self._back


class AbstractEvent:
    def __init__(self, before=None, after=None):
        self._before = before
        self._after = after

    @property
    def before(self):
        return self._before

    @property
    def after(self):
        return self._after


class Message(AbstractEvent):
    @classmethod
    def to_message(cls, event, children):
        commands = []
        commands_message = ''
        before = None
        after = None

        if children:
            for e in children:
                if e.intent:
                    commands.append(e.intent)

            commands_message = ': ({})'.format(', '.join(commands))

        if event.before and 'message' in event.before:
            before = '{}{}'.format(event.before['message'], commands_message)

        if event.after and 'message' in event.after:
            after = event.after['message']

        return cls(before, after)


class Redirect(AbstractEvent):
    @classmethod
    def to_link(cls, event):
        before = None
        after = None

        if event.before and 'path' in event.before:
            before = event.before['path']
        if event.after and 'path' in event.after:
            after = event.after['path']

        return cls(before, after)


class Model(AbstractEvent):
    @classmethod
    def to_model(cls, event):
        before = None
        after = None

        if event.before and 'model' in event.before:
            before = event.before['model']
        if event.after and 'model' in event.after:
            after = event.after['model']

        return cls(before, after)


class Node:
    def __init__(self, entity, children):
        self._entity = entity
        self._children = children

    @property
    def id(self):
        return self._entity.id

    @property
    def message(self):
        return Message.to_message(self._entity.event, self._children)

    @property
    def redirect(self):
        return Redirect.to_link(self._entity.event)

    @property
    def model(self):
        return Model.to_model(self._entity.event)

    def raw_child_id(self, intent):
        for child in self._children:
            if (child.intent == intent) or (child.similar and intent in child.similar):
                return child.id
        return None

    def child(self, intent):
        for child in self._children:
            if child.intent == intent:
                return child
        return None


class Builder:
    def __init__(self, store):
        self._store = store

    def build(self, data=None):
        if not data:
            data = self._store.head()

        children = []
        if 'children' in data:
            for e in data['children']:
                child = self._store.element(e)
                if not child:
                    continue
                children.append(Entity.to_entity(child))

        entity = Entity.to_entity(data)

        return Node(entity, children)


class Flow:
    def __init__(self, store):
        self._store = store
        self._builder = Builder(store)
        self._current = None
        self._originator = Originator()

    def __iter__(self):
        return self

    def _current_entity(self, index):
        data = self._store.element(index)
        self._current = self._builder.build(data)

    def previous(self):
        index = self._originator.previous()
        if index:
            self._current_entity(index)

    def forward(self):
        index = self._originator.forward()
        if index:
            self._current_entity(index)

    def before_event(self, handler=None):
        if self._current.message:
            if self._current.message.before:
                print(self._current.message.before)
        if self._current.model:
            if self._current.model.before:
                flow_model = FlowModel(self._current.model.before)
                flow_model.start_flow(handler)

    def next(self, intent=None, method=None, *args):
        if not intent and not method:
            self._current = self._builder.build()

        if intent:
            id = self._current.raw_child_id(intent)
            if not id:
                return self

            self._current_entity(id)

        if self._current.redirect:
            if self._current.redirect.after:
                self._current_entity(self._current.redirect.after)

        self._originator.store(self._current.id)

        return self

    def after_event(self):
        if self._current.message:
            if self._current.message.after:
                print(self._current.message.after)

    def similar(self, intent):
        print(self._current.child(intent).similar)


class FlowModel:
    def __init__(self, model):
        self._model = model
        self._instance = None

    def start_flow(self, handler):
        generator = Generator()
        command = ''

        while command != 'stop':
            if self._instance is None:
                self._create_model()
                generator.instance = self._instance

            generator.next() if generator.weak_value is None else generator.next(command)

            command = input('# ')

        print (generator.instance.id, generator.instance.name)
        handler.back()

    def _create_model(self):
        manager = PathManager.open(self._model)
        self._instance = manager.model
