from aiogram.fsm.state import State, StatesGroup


class FSM(StatesGroup):
    """Finite-state machine states"""

    get_ratings = State()
    update_tables = State()
