from widgets.Variable import ListVariable, CustomVariable
from ValLib import ExtraAuth


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Constant(metaclass=SingletonMeta):
    Accounts: ListVariable[ExtraAuth] = ListVariable()
    EndPoints: ListVariable[EndPoints] = ListVariable()
    Current_Acc: CustomVariable = CustomVariable(None)
    Setting_Valorant: dict = {}
    Current_Acc_Setting: dict = {}
