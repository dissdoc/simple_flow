from version2.core.fields import Field


class BaseModel(type):
    def __new__(cls, name, bases, attrs, **kwargs):
        instance = super().__new__

        parents = [b for b in bases if isinstance(b, BaseModel.__class__)]
        if not parents:
            return instance(cls, name, bases, attrs)

        module_ = attrs.pop('__module__')
        attrs_ = {'__module__': module_}

        classcell_ = attrs.pop('__classcell__', None)
        if classcell_ is not None:
            attrs_['__classcell__'] = classcell_

        for key, value in attrs.items():
            if not isinstance(value, Field):
                continue
            attrs_[key] = value

        instance = instance(cls, name, bases, attrs_, **kwargs)

        return instance


class Model(metaclass=BaseModel):
    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls, *args, **kwargs)

        for name, attr in cls.__dict__.items():
            if isinstance(attr, Field):
                setattr(instance, name, attr.value())

        return instance
