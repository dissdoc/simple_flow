import importlib


class Decoder:
    @staticmethod
    def decode(model):
        raise NotImplementedError()


class PythonDecoder(Decoder):
    @staticmethod
    def decode(model):
        if model is None:
            return None

        module_name, class_name = model.rsplit(".", 1)
        MyClass = getattr(importlib.import_module(module_name), class_name)
        instance = MyClass()

        return instance


class DefaultDecoder(Decoder):
    @staticmethod
    def decode(model):
        return 'default'


class PathManager:
    def __init__(self, model):
        self._model = model

    @classmethod
    def open(cls, path):
        root, model = path.split(':')
        if root == 'python':
            decoder = PythonDecoder
        elif root == 'default':
            decoder = DefaultDecoder
        else:
            raise RuntimeError('It can not decode path')

        instance = decoder.decode(model)
        return cls(instance)

    @property
    def model(self):
        return self._model


class Generator:
    def __init__(self):
        self._instance = None
        self._steps = None
        self._weak_value = None

    @property
    def instance(self):
        return self._instance

    @instance.setter
    def instance(self, inst):
        self._instance = inst

    @property
    def weak_value(self):
        return self._weak_value

    def __iter__(self):
        return self

    def next(self, value=None):
        if self._steps is None:
            self._steps = []
            for key, value in self._instance.__class__.__dict__.items():
                if key in ['__module__', '__doc__']:
                    continue
                self._steps.append(key)

        if value is None:
            if len(self._steps) == 0:
                return self

            self._weak_value = self._steps.pop(0)
            print ('Enter {}'.format(self._weak_value))
        else:
            setattr(self._instance, self._weak_value, value)
            self._weak_value = None

        return self