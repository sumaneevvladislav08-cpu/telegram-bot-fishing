import os
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
import pytz
from datetime import datetime
from aiohttp import web

# Токен бота
BOT_TOKEN = os.getenv('8310809355:AAHu_5LR5Sbty_hIs3d2wvmX99Wl9oHV2RQ')
if not BOT_TOKEN:
    raise ValueError("Токен бота не найден.")

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

moscow_tz = pytz.timezone('Europe/Moscow')

BAITS_FOLDER = "baits"

if not os.path.exists(BAITS_FOLDER):
    raise FileNotFoundError(f"Папка {BAITS_FOLDER} не найдена.")

bait_files = [f for f in os.listdir(BAITS_FOLDER) if f.endswith(('.jpg', '.jpeg', '.png'))]

if not bait_files:
    raise ValueError(f"В папке {BAITS_FOLDER} нет фото.")

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Отправь время (например, 12:34) и ссылку, и я отправлю приманку!")

@dp.message_handler()
async def handle_time_link(message: types.Message):
    text = message.text.strip()
    try:
        parts = text.split()
        if len(parts) != 2:
            await message.reply("Неверный формат. Пример: 12:34 https://example.com")
            return

        time_str, link = parts
        if not (len(time_str.split(':')) == 2 and link.startswith('http')):
            await message.reply("Неверный формат. Пример: 12:34 https://example.com")
            return

        current_time = datetime.now(moscow_tz).strftime("%H:%M")
        await message.reply(f"Текущее время в Москве: {current_time}")

        import random
        bait_file = random.choice(bait_files)
        photo_path = os.path.join(BAITS_FOLDER, bait_file)
        with open(photo_path, 'rb') as photo:
            await message.reply_photo(photo, caption=f"Приманка для {time_str} на {link}")

    except Exception as e:
        await message.reply(f"Ошибка: {str(e)}")

# Dummy веб-сервер
async def dummy_web(request):
    return web.Response(text="Bot is running.")

app = web.Application()
app.add_routes([web.get('/', dummy_web)])

if __name__ == '__main__':
    print("Бот запущен...")
    web.run_app(app, port=os.getenv('PORT', 8000))
    dp.run_polling()
