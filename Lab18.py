1
import json
import os

class Assistant:
    def __init__(self, filename="notes.json"):
        self.filename = filename
        if not os.path.exists(self.filename):
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump([], f)

    def _load_notes(self):
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save_notes(self, notes):
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(notes, f, ensure_ascii=False, indent=2)

    def add_note(self, note: str):
        notes = self._load_notes()
        notes.append(note)
        self._save_notes(notes)

    def list_notes(self):
        return self._load_notes()

    def search_notes(self, keyword: str):
        return [n for n in self._load_notes() if keyword.lower() in n.lower()]

    def delete_note(self, keyword: str):
        notes = self._load_notes()
        remaining = [n for n in notes if keyword.lower() not in n.lower()]
        deleted = len(notes) - len(remaining)
        self._save_notes(remaining)
        return deleted

bot
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

from assistant import Assistant

BOT_TOKEN = "7540305055:AAE3FhQoJiv8exvAVoVgkcMCwz70uJMtTis"

# Ініціалізація бота з підтримкою ParseMode
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())
assistant = Assistant()

# Стан для додавання та видалення нотаток
class AddNoteState(StatesGroup):
    awaiting_note_text = State()

class DeleteNoteState(StatesGroup):
    awaiting_delete_text = State()

@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer("👋 Вітаю! Я бот-асистент для нотаток. Напиши /help, щоб дізнатись більше.")

@dp.message(Command("help"))
async def help_handler(message: Message):
    await message.answer(
        "<b>📘 Команди бота:</b>\n"
        "/add — додати нотатку\n"
        "/list — переглянути нотатки\n"
        "/search — пошук за словом\n"
        "/delete — видалити нотатку\n"
        "/info — про бота\n"
        "/exit — завершити взаємодію"
    )

@dp.message(Command("info"))
async def info_handler(message: Message):
    await message.answer("🧠 Я зберігаю твої нотатки у файлі <code>notes.json</code>. Вони доступні як у Telegram, так і в консолі.")

@dp.message(Command("exit"))
async def exit_handler(message: Message):
    await message.answer("👋 До зустрічі! Я завжди тут, коли потрібно.")

@dp.message(Command("add"))
async def add_handler(message: Message, state: FSMContext):
    await message.answer("✍️ Введи текст нотатки:")
    await state.set_state(AddNoteState.awaiting_note_text)

@dp.message(StateFilter(AddNoteState.awaiting_note_text))
async def receive_note(message: Message, state: FSMContext):
    assistant.add_note(message.text)
    await message.answer("✅ Нотатку збережено.")
    await state.clear()

@dp.message(Command("list"))
async def list_handler(message: Message):
    notes = assistant.list_notes()
    if notes:
        response = "\n".join([f"{i+1}. {n}" for i, n in enumerate(notes)])
    else:
        response = "📭 Немає жодної нотатки."
    await message.answer(response)

@dp.message(Command("search"))
async def search_handler(message: Message, state: FSMContext):
    await message.answer("🔍 Введіть слово для пошуку:")
    await state.set_state("awaiting_search")

@dp.message(StateFilter("awaiting_search"))
async def receive_search(message: Message, state: FSMContext):
    results = assistant.search_notes(message.text)
    if results:
        await message.answer("🔎 Знайдені нотатки:\n" + "\n".join(results))
    else:
        await message.answer("❌ Нічого не знайдено.")
    await state.clear()

@dp.message(Command("delete"))
async def delete_handler(message: Message, state: FSMContext):
    await message.answer("🗑️ Введіть ключове слово нотатки для видалення:")
    await state.set_state(DeleteNoteState.awaiting_delete_text)

@dp.message(StateFilter(DeleteNoteState.awaiting_delete_text))
async def receive_delete(message: Message, state: FSMContext):
    deleted = assistant.delete_note(message.text)
    if deleted:
        await message.answer(f"✅ Видалено {deleted} нотатку(и).")
    else:
        await message.answer("❌ Нотатку не знайдено.")
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
