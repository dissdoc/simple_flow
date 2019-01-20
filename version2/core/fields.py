import itertools
import weakref
import abc


class Field:
    def __init__(self):
        self._values = weakref.WeakKeyDictionary()

    def __get__(self, instance, owner):
        return self if instance is None else self._values[instance]

    def __set__(self, instance, value):
        self._values[instance] = value

    @abc.abstractmethod
    def value(self):
        pass


class FId(Field):
    def __init__(self, unique=False):
        super().__init__()
        self._unique = unique

    def __set__(self, instance, value):
        if not self._unique:
            self._values[instance] = value

        else:
            if value not in self._values.values():
                self._values[instance] = value
            else:
                raise ValueError('Unique id {} already taken'.format(value))

    def _generate_unique_id(self):
        existing_ids = set(self._values.values())
        return next(i for i in itertools.count() if i not in existing_ids)


class FString(Field):
    def __init__(self, max_length=256, min_length=0, null=False, default=None):
        super().__init__()
        self._max_length = max_length
        self._min_length = min_length
        self._null = null
        self._default = default


class FInteger(Field):
    def __init__(self, default=0, null=False, max_value=64, min_value=0):
        super().__init__()
        self._max_value = max_value
        self._min_value = min_value
        self._null = null
        self._default = default


class FBoolean(Field):
    def __init__(self, default=False):
        super().__init__()
        self._default = default