class Store:
    def __init__(self, data):
        self._data = data

    @classmethod
    def to_data(cls, raw):
        def _recur_data(raw, data):
            element = {}
            for key, value in raw.items():
                if key == 'children':
                    ids = []
                    for el in value:
                        ids.append(el['id'])
                        _recur_data(el, data)
                    element[key] = ids
                else:
                    element[key] = value
            data[raw['id']] = element

        data = {}
        _recur_data(raw, data)

        return cls(data)

    def element(self, id):
        if id not in self._data:
            return None

        return self._data[id]

    def head(self):
        return self._data[1]


class Event:
    @classmethod
    def to_event(cls, data):
        event = cls()

        for key, value in data.items():
            setattr(event, '_{}'.format(key), value)

        return event

    @property
    def after(self):
        return None if not hasattr(self, '_after') else self._after

    @property
    def before(self):
        return None if not hasattr(self, '_before') else self._before


class Entity:
    @classmethod
    def to_entity(cls, data):
        entity = cls()

        for key, value in data.items():
            setattr(entity, '_{}'.format(key), value)

        return entity

    @property
    def id(self):
        return self._id

    @property
    def intent(self):
        return None if not hasattr(self, '_intent') else self._intent

    @property
    def event(self):
        return None if not hasattr(self, '_event') else Event.to_event(self._event)

    @property
    def similar(self):
        return None if not hasattr(self, '_similar') else self._similar


class Memento:
    def __init__(self):
        self._state = []
        self._current_index = -1

    def add(self, element):
        if self._current_index + 1 != len(self._state):
            self._state = self._state[:self._current_index+1]

        self._state.append(element)
        self._current_index += 1

    def previous(self):
        if self._current_index == -1:
            return None

        if self._current_index == 0:
            return self._state[self._current_index]

        if self._current_index > 0:
            self._current_index -= 1
            return self._state[self._current_index]

    def forward(self):
        if self._current_index == -1:
            return None

        if self._current_index == len(self._state) - 1:
            return self._state[self._current_index]

        if self._current_index >= 0:
            self._current_index += 1
            return self._state[self._current_index]


class Originator:
    def __init__(self, callback=None):
        self._memento = Memento()
        self._callback = callback

    def store(self, element):
        self._memento.add(element)

    def forward(self):
        return self._memento.forward()
        # f = self._memento.forward()
        # return self._callback(f)

    def previous(self):
        return self._memento.previous()
        # p = self._memento.previous()
        # return self._callback(p)


