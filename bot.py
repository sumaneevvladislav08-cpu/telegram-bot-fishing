import random
import datetime
import os
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import FSInputFile, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.client.default import DefaultBotProperties

# Токен бота (получен от @BotFather)
BOT_TOKEN = "8310809355:AAHu_5LR5Sbty_hIs3d2wvmX99Wl9oHV2RQ"

# Настройка свойств бота
default = DefaultBotProperties(parse_mode=ParseMode.HTML)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN, default=default)
dp = Dispatcher()

# Папка с приманками
BAITS_FOLDER = "baits"

# Создаем инлайн-кнопку "HACK"
def get_hack_button():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="HACK", callback_data="hack_instruction")]
    ])
    return keyboard

# Обработчик команды /start
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    welcome_text = "👋 Добро пожаловать! Нажми кнопку HACK, чтобы получить инструкцию."
    await message.reply(welcome_text, reply_markup=get_hack_button())

# Обработчик текстовых сообщений (включая время и ссылку)
@dp.message()
async def handle_message(message: types.Message):
    if message.text is None:
        print("Получено не текстовое сообщение, игнорирую.")
        return

    print(f"Получено сообщение: {message.text}")
    text = message.text.strip().split(maxsplit=1)
    print(f"Разделённое сообщение: {text}")
    if len(text) >= 2:
        time_str = text[0]
        print(f"Обнаружено время: {time_str}")
        try:
            user_time = datetime.datetime.strptime(time_str, "%H:%M")
            print("Формат времени верный")
            new_time = (user_time + datetime.timedelta(minutes=1)).strftime("%H:%M")

            baits = [f for f in os.listdir(BAITS_FOLDER) if f.lower().endswith((".png", ".jpg"))]
            print(f"Найдено приманок: {len(baits)}")
            if not baits:
                await message.reply("Нет приманок в папке!")
                return

            bait_file = random.choice(baits)
            bait_path = os.path.join(BAITS_FOLDER, bait_file)
            print(f"Путь к приманке: {bait_path}")
            try:
                photo = FSInputFile(bait_path)  # Используем FSInputFile для локального файла
                print(f"Файл {bait_file} подготовлен для отправки")
                caption = f"⏰ Время: {new_time}\n🎣 Приманка: {bait_file.replace('.jpg', '').replace('.png', '')}"
                await message.reply_photo(photo, caption=caption)
                print("Фото отправлено успешно")
            except FileNotFoundError:
                print(f"Файл {bait_file} не найден")
                await message.reply("Ошибка: файл приманки не найден, проверь папку baits/")
            except PermissionError:
                print(f"Нет прав доступа к {bait_file}")
                await message.reply("Ошибка: нет прав доступа к файлам, проверь настройки безопасности.")
            except Exception as e:
                print(f"Неизвестная ошибка при отправке фото: {e}")
                await message.reply("Ошибка при отправке фото, проверь папку baits/")
                return
        except ValueError:
            print("Формат времени неверный")
            pass

    print("Сообщение не распознано как время+ссылка")
    await message.reply("Пришли время и ссылку (например: 12:34 https://example.com) или нажми HACK для инструкции.", reply_markup=get_hack_button())

# Обработчик нажатия на кнопку HACK
@dp.callback_query(lambda c: c.data == "hack_instruction")
async def send_instruction(callback_query: types.CallbackQuery):
    instruction = (
        "📜 Инструкция по использованию:\n"
        "1. Зайди в игру и скопируй ссылку на неё.\n"
        "2. Скопируй время, которое отображается в правом верхнем углу игры (в формате HH:MM).\n"
        "3. Отправь боту сообщение в формате: \"время ссылка\" (например, 12:34 https://example.com).\n"
        "4. Бот выдаст тебе приманку и точное время для игры.\n"
        "Удачи! 🍀"
    )
    await callback_query.message.answer(instruction)
    await callback_query.answer()

if __name__ == "__main__":
    dp.run_polling(bot)