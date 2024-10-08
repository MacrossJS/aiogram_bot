from aiogram.fsm.state import StatesGroup, State


class FSMFillForm(StatesGroup):
    # Создаем экземпляры класса State, последовательно
    # перечисляя возможные состояния, в которых будет находиться
    # бот в разные моменты взаимодейтсвия с пользователем
    fill_note_name = State()        # Состояние ожидания ввода имени
    fill_note_text = State()         # Состояние ожидания ввода возраста

