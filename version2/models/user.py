from version2.core.models import Model
from version2.core.fields import FId
from version2.core.fields import FString


class User(Model):
    id = FId(unique=True)
    name = FString()