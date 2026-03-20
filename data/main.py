import asyncio
import random
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import (
    InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, KeyboardButton, FSInputFile
)
from aiogram.filters import CommandStart

from words import words_data

BOT_TOKEN = "8056478705:AAF0s9rvkEIhOb_LtoHAcJdv685O4ZCIymQ"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

user_test = {}

# 🔥 LEVEL ANIQLASH
def get_level(day):
    if day <= 25:
        return "A1"
    elif day <= 75:
        return "A2"
    elif day <= 150:
        return "B1"
    elif day <= 250:
        return "B2"
    else:
        return "B2+"


# 📌 MAIN MENU (❗ vergul tuzatildi)
def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📘 A1"), KeyboardButton(text="📗 A2")],
            [KeyboardButton(text="📙 B1"), KeyboardButton(text="📕 B2")],
            [KeyboardButton(text="🏠 Bosh sahifa")]
        ],
        resize_keyboard=True
    )


# 📌 BLOKLAR
def get_days_keyboard(start, end, level):
    keyboard = []
    row = []

    for day in range(start, end + 1):
        row.append(InlineKeyboardButton(
            text=f"{level}-{day}",
            callback_data=f"day_{day}"
        ))

        if len(row) == 5:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# 📌 TEST TUGMA
def get_test_button(day):
    level = get_level(day)
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=f"🧠 Test {level}-{day}")],
            [KeyboardButton(text="🏠 Bosh sahifa")]
        ],
        resize_keyboard=True
    )


# 🚀 START
@dp.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer(
        "📚 Darajani tanlang 👇",
        reply_markup=get_main_keyboard()
    )


# 📘 A1
@dp.message(F.text == "📘 A1")
async def a1_handler(message: types.Message):
    await message.answer(
        "📘 A1 bloklar",
        reply_markup=get_days_keyboard(1, 25, "A1")
    )


# 📗 A2
@dp.message(F.text == "📗 A2")
async def a2_handler(message: types.Message):
    await message.answer(
        "📗 A2 bloklar",
        reply_markup=get_days_keyboard(26, 75, "A2")
    )


# 📙 B1
@dp.message(F.text == "📙 B1")
async def b1_handler(message: types.Message):
    await message.answer(
        "📙 B1 bloklar",
        reply_markup=get_days_keyboard(76, 150, "B1")
    )


# 📕 B2
@dp.message(F.text == "📕 B2")
async def b2_handler(message: types.Message):
    await message.answer(
        "📕 B2 bloklar",
        reply_markup=get_days_keyboard(151, 250, "B2")
    )


# 📖 BLOK
@dp.callback_query(F.data.startswith("day_"))
async def day_handler(callback: types.CallbackQuery):
    day = int(callback.data.split("_")[1])
    words = words_data.get(day)

    if not words:
        await callback.message.answer("❌ Bu kun uchun so‘z topilmadi")
        await callback.answer()
        return

    level = get_level(day)

    text = f"📅 {level} | {day}-kun\n\n"
    for i, w in enumerate(words, 1):
        text += f"{i}. {w}\n"

    await callback.message.answer(text)

    await callback.message.answer(
        "👇 Testni boshlash",
        reply_markup=get_test_button(day)
    )

    await callback.answer()


# 🧠 TEST START
@dp.message(F.text.startswith("🧠 Test"))
async def start_test(message: types.Message):
    try:
        day = int(message.text.split("-")[1])
    except:
        await message.answer("❌ Xato format")
        return

    words = words_data.get(day)

    if not words:
        await message.answer("❌ So‘zlar topilmadi")
        return

    questions = words.copy()
    random.shuffle(questions)

    user_test[message.from_user.id] = {
        "questions": questions,
        "current": 0,
        "correct": 0,
        "day": day,
        "errors": [],
        "results": []
    }

    await send_question(message.from_user.id, message)


# 📤 SAVOL
async def send_question(user_id, message):
    data = user_test[user_id]

    if data["current"] >= len(data["questions"]):

        result_line = ""
        for i, r in enumerate(data["results"], 1):
            result_line += f"{i}-{r} "

        text = f"""
🎯 Test tugadi!

📊 Natijalar:
{result_line}

✅ To‘g‘ri: {data['correct']}
❌ Xato: {len(data['errors'])}
"""
        await message.answer(text)

        if data["errors"]:
            filename = f"xato_{user_id}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                for e in data["errors"]:
                    f.write(e + "\n")

            await message.answer_document(FSInputFile(filename))

        return

    word = data["questions"][data["current"]]
    ru, uz = word.split(" - ")

    variants = [uz]
    while len(variants) < 4:
        rand = random.choice(random.choice(list(words_data.values()))).split(" - ")[1]
        if rand not in variants:
            variants.append(rand)

    random.shuffle(variants)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=v, callback_data=f"ans_{v}")]
            for v in variants
        ]
    )

    await message.answer(f"❓ {ru}", reply_markup=keyboard)


# 🎯 JAVOB
@dp.callback_query(F.data.startswith("ans_"))
async def check_answer(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    answer = callback.data.split("ans_")[1]

    data = user_test[user_id]
    word = data["questions"][data["current"]]
    ru, uz = word.split(" - ")

    await callback.message.edit_reply_markup(reply_markup=None)

    if answer == uz:
        data["correct"] += 1
        data["results"].append("✅")
    else:
        data["results"].append("❌")
        await callback.message.answer(f"❌ {uz}")
        data["errors"].append(f"{get_level(data['day'])}-{data['day']} | {word}")

    data["current"] += 1

    await callback.answer()

    await send_question(user_id, callback.message)


# 🏠 BOSH SAHIFA
@dp.message(F.text == "🏠 Bosh sahifa")
async def home_btn(message: types.Message):
    user_test.pop(message.from_user.id, None)

    await message.answer(
        "📚 Darajani tanlang 👇",
        reply_markup=get_main_keyboard()
    )


# ▶️ RUN
async def main():
    print("Bot ishlayapti...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())