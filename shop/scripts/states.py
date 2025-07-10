from telebot.handler_backends import State, StatesGroup

class UserStates(StatesGroup):
    START = State()
    PROFILE = State()
    CATALOG = State()
    ADMIN = State()

    