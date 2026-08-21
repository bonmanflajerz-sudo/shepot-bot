import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# ===== ТВОЙ ТОКЕН =====
BOT_TOKEN = "8788975690:AAH-g2cYPrjO2zKF_xKxJ1MVgqpU-QJL7oc"
ADMIN_ID = 6976756851
# ========================

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ===== КЛАВИАТУРА =====
def get_main_keyboard():
    buttons = [
        [KeyboardButton(text="🏙️ Городской мем")],
        [KeyboardButton(text="🎥 Стримерский мем")],
        [KeyboardButton(text="🎭 Классический мем")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

# ===== ВРЕМЕННОЕ ХРАНИЛИЩЕ =====
user_data = {}

# ===== /start =====
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    user_id = message.from_user.id
    # При старте очищаем данные пользователя, чтобы он мог начать заново
    user_data.pop(user_id, None)
    await message.answer(
        "👋 Привет! Я Шёпот Сауми!\n\n"
        "Выбери тип мема:",
        reply_markup=get_main_keyboard()
    )

# ===== ВЫБОР КАТЕГОРИИ =====
@dp.message()
async def handle_category(message: types.Message):
    user_id = message.from_user.id
    text = message.text

    if text == "🏙️ Городской мем":
        user_data[user_id] = {"category": "городской"}
        await message.answer(
            "🏙️ Городской мем выбран!\n\n"
            "📝 Напиши название своего города.\n"
            "📎 После этого пришли файл (видео, фото) с подписью.",
            reply_markup=get_main_keyboard()
        )

    elif text == "🎥 Стримерский мем":
        user_data[user_id] = {"category": "стримерский"}
        await message.answer(
            "🎥 Стримерский мем выбран!\n\n"
            "📝 Пришли ссылку на стрим с таймкодом.\n"
            "📎 Или сразу пришли видео/откат со стрима.",
            reply_markup=get_main_keyboard()
        )

    elif text == "🎭 Классический мем":
        user_data[user_id] = {"category": "классический"}
        await message.answer(
            "🎭 Классический мем выбран!\n\n"
            "📎 Просто пришли файл (видео, фото, откат).\n"
            "📝 Напиши, что улучшить и какой мем сделать.",
            reply_markup=get_main_keyboard()
        )

    else:
        await handle_file_or_text(message)

# ===== ОБРАБОТКА ФАЙЛОВ =====
async def handle_file_or_text(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or "без юзернейма"
    full_name = message.from_user.full_name or "без имени"

    # Проверяем, выбрал ли пользователь категорию
    if user_id not in user_data:
        await message.answer(
            "⚠️ Сначала выбери тип мема на клавиатуре!\n"
            "Напиши /start, чтобы начать.",
            reply_markup=get_main_keyboard()
        )
        return

    category = user_data[user_id].get("category", "неизвестно")

    # Проверяем, есть ли файл
    has_file = (
        message.photo or message.video or message.document or
        message.audio or message.voice or message.animation
    )

    if not has_file:
        await message.reply(
            "📎 Пожалуйста, пришли файл (видео, фото, откат, гифку)!\n"
            "Если хочешь начать заново — напиши /start",
            reply_markup=get_main_keyboard()
        )
        return

    # Отправка админу
    admin_text = (
        f"📩 Новый мем\n"
        f"━━━━━━━━━━━━━━━\n"
        f"👤 От: @{username} ({full_name})\n"
        f"🏷️ Категория: {category}\n"
        f"━━━━━━━━━━━━━━━\n"
    )

    if message.text:
        admin_text += f"📝 Текст: {message.text}\n"
    if message.caption:
        admin_text += f"📝 Подпись: {message.caption}\n"

    admin_text += "\n🎯 Жду обработки!"

    await bot.send_message(chat_id=ADMIN_ID, text=admin_text)
    await message.forward(chat_id=ADMIN_ID)

    await message.reply(
        "✅ Отлично! Твой мем получен!\n"
        "Скоро будет обработан! 🚀",
        reply_markup=get_main_keyboard()
    )

    # ❗ Категория НЕ ОЧИЩАЕТСЯ, чтобы пользователь мог отправлять несколько файлов.
    # Если хочешь сбросить категорию — напиши /start.

# ===== ЗАПУСК =====
async def main():
    print("🤖 Бот запущен и готов к работе!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())