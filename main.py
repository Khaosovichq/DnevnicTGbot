import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor

API_TOKEN = 'секрет)'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class NewNoteStates(StatesGroup):
    waiting_for_note = State()


# Создаем директорию для файлов, если ее нет
if not os.path.exists('notes'):
    os.makedirs('notes')


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Привет! Я бот для ведения дневника. Используй /help, чтобы увидеть доступные команды.")


@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    await message.answer("Доступные команды:\n"
                         "/start - начать работу с ботом\n"
                         "/help - список команд\n"
                         "/new_note - добавить новую заметку\n"
                         "/list_notes - посмотреть список заметок")


@dp.message_handler(commands=['new_note'])
async def new_note_command(message: types.Message):
    await message.answer("Введите текст новой заметки:")
    # Устанавливаем состояние, чтобы следующее сообщение было обработано в новом обработчике
    await NewNoteStates.waiting_for_note.set()


@dp.message_handler(state=NewNoteStates.waiting_for_note, content_types=types.ContentType.TEXT)
async def process_new_note(message: types.Message, state: dict):
    note_text = message.text
    formatted_date = str(message.date).replace(':', '_')
    note_filename = f'notes/note_{message.from_user.id}_{formatted_date}.txt'
    with open(note_filename, 'w', encoding='utf-8') as file:
        file.write(note_text)

    await state.finish()
    await message.answer(f"Заметка сохранена в файле: {note_filename}")


@dp.message_handler(commands=['list_notes'])
async def list_notes_command(message: types.Message):
    notes_list = os.listdir('notes')
    if notes_list:
        notes_list_str = "\n".join(notes_list)
        await message.answer(f"Список заметок:\n{notes_list_str}")
    else:
        await message.answer("Список заметок пуст.")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
