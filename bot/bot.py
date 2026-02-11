import asyncio
import re
import openai

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart

from config import TELEGRAM_TOKEN, my_key

# ================= TELEGRAM =================

bot = Bot(
    token=TELEGRAM_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# ================= YANDEX AGENT =================

client = openai.OpenAI(
    api_key=my_key,
    base_url="https://rest-assistant.api.cloud.yandex.net/v1",
    project="b1gblc7ca9fb1rj110cf"
)

AGENT_ID = "fvto5ko9l2ckfuadm2k2"

# ================= STORAGE =================

dialog_context = {}
user_state = {}
user_directions = {}
saved_directions = {}
selected_direction = {}
selected_city = {}
cities_storage = {}


# ================= KEYBOARDS =================

def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📌 Мои направления")],
            [KeyboardButton(text="⭐ Сохранённые направления")],
            [KeyboardButton(text="🔄 Обновить направления")]
        ],
        resize_keyboard=True
    )


def back_menu():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🔙 В меню")]],
        resize_keyboard=True
    )


def direction_actions():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="ℹ️ Информация")],
            [KeyboardButton(text="🏫 Вузы")],
            [KeyboardButton(text="⭐ Сохранить")],
            [KeyboardButton(text="🔙 К списку")]
        ],
        resize_keyboard=True
    )


def saved_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🗑 Очистить сохранённые")],
            [KeyboardButton(text="🔙 В меню")]
        ],
        resize_keyboard=True
    )


def universities_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🌍 Все города")],
            [KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True
    )


def city_detail_menu(direction_name: str):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=f"ℹ️ Информация о направлении")],
            [KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True
    )


# ================= AI =================

def extract_directions(text: str):
    return re.findall(r"\d+\.\s*(.+)", text)


async def ask_agent(user_id: int, text: str) -> str:
    response = client.responses.create(
        prompt={"id": AGENT_ID},
        input=text,
        previous_response_id=dialog_context.get(user_id)
    )

    dialog_context[user_id] = response.id
    return response.output_text


async def ensure_10(user_id: int, first_answer: str):
    directions = extract_directions(first_answer)

    if len(directions) >= 10:
        return directions[:10]

    follow = await ask_agent(
        user_id,
        "Выдай полный список из 10 направлений. Только список."
    )

    directions = extract_directions(follow)
    return directions[:10]


# ================= COMMANDS =================


@dp.message(CommandStart())
async def start_cmd(message: Message):
    uid = message.from_user.id
    user_state[uid] = "menu"

    await message.answer(
        "<b>Привет 👋</b>\n\n"
        "Я помогу тебе выбрать направление для обучения в вузе 🎓\n\n"
        "Ты можешь:\n"
        "• Получить список направлений по своим интересам\n"
        "• Сохранить понравившиеся варианты\n"
        "• Посмотреть в каких городах есть это направление\n\n"
        "Нажми <b>«🔄 Обновить направления»</b>, чтобы начать.",
        reply_markup=main_menu()
    )


@dp.message(F.text == "🔄 Обновить направления")
async def update_dirs(message: Message):
    uid = message.from_user.id

    dialog_context.pop(uid, None)
    user_directions.pop(uid, None)

    user_state[uid] = "dialog"

    await message.answer(
        "Давай обновим направления 😊\nНапиши, что тебе нравится.",
        reply_markup=back_menu()
    )


@dp.message(F.text == "📌 Мои направления")
async def my_dirs(message: Message):
    uid = message.from_user.id
    dirs = user_directions.get(uid)

    if not dirs:
        await message.answer("Направлений пока нет.", reply_markup=main_menu())
        return

    user_state[uid] = "choose"

    text = "<b>Твои направления:</b>\n\n"
    for i, d in enumerate(dirs, 1):
        text += f"{i}. {d}\n"

    text += "\nНапишите номер направления, чтобы узнать про него подробнее."

    await message.answer(text, reply_markup=back_menu())


@dp.message(F.text == "⭐ Сохранённые направления")
async def saved_dirs(message: Message):
    uid = message.from_user.id
    dirs = saved_directions.get(uid)

    if not dirs:
        await message.answer("Сохранённых направлений нет.", reply_markup=main_menu())
        return

    user_state[uid] = "choose_saved"

    text = "<b>Сохранённые направления:</b>\n\n"
    for i, d in enumerate(dirs, 1):
        text += f"{i}. {d}\n"

    text += "\nВведите номер направления."

    await message.answer(text, reply_markup=saved_menu())


@dp.message(F.text == "🗑 Очистить сохранённые")
async def clear_saved_prompt(message: Message):
    uid = message.from_user.id
    user_state[uid] = "clear_saved"

    await message.answer(
        "Введите номера направлений через запятую (например: 1,3,5)",
        reply_markup=back_menu()
    )


@dp.message(F.text == "🔙 В меню")
async def back_to_menu(message: Message):
    user_state[message.from_user.id] = "menu"
    await message.answer("Главное меню:", reply_markup=main_menu())


# ================= MAIN TEXT HANDLER =================

@dp.message(F.text)
async def text_handler(message: Message):
    uid = message.from_user.id
    text = message.text.strip()
    state = user_state.get(uid)

    if state is None:
        user_state[uid] = "menu"
        await message.answer("Главное меню:", reply_markup=main_menu())
        return

    # ===== ВЫБОР НАПРАВЛЕНИЯ =====
    if state in {"choose", "choose_saved"} and text.isdigit():
        idx = int(text) - 1
        dirs = user_directions if state == "choose" else saved_directions

        if uid in dirs and 0 <= idx < len(dirs[uid]):
            selected_direction[uid] = dirs[uid][idx]
            user_state[uid] = "actions"

            await message.answer(
                f"<b>{dirs[uid][idx]}</b>\nВыберите действие:",
                reply_markup=direction_actions()
            )
        return

    # ===== ДИАЛОГ С АГЕНТОМ =====
    if state == "dialog":
        answer = await ask_agent(uid, text)
        directions = await ensure_10(uid, answer)

        user_directions[uid] = directions
        user_state[uid] = "choose"

        await message.answer(
            answer + "\n\nНапишите номер направления, чтобы узнать про него подробнее.",
            reply_markup=back_menu()
        )
        return

    # ===== ОЧИСТКА =====
    if state == "clear_saved":
        numbers = re.findall(r"\d+", text)
        numbers = sorted(set(int(n) - 1 for n in numbers), reverse=True)

        if uid in saved_directions:
            for n in numbers:
                if 0 <= n < len(saved_directions[uid]):
                    saved_directions[uid].pop(n)

        user_state[uid] = "menu"
        await message.answer("Удалено ✅", reply_markup=main_menu())
        return

    # ===== ДЕЙСТВИЯ С НАПРАВЛЕНИЕМ =====
    if state == "actions":

        if text == "⭐ Сохранить":
            saved_directions.setdefault(uid, [])

            if selected_direction[uid] not in saved_directions[uid]:
                saved_directions[uid].append(selected_direction[uid])
                await message.answer("⭐ Направление сохранено", reply_markup=direction_actions())
            else:
                await message.answer("⚠️ Уже сохранено", reply_markup=direction_actions())

        elif text == "ℹ️ Информация":
            await message.answer(
                f"ℹ️ Информация о направлении",
                reply_markup=direction_actions()
            )

        elif text == "🏫 Вузы":
            user_state[uid] = "universities"
            await message.answer(
                "Выберите действие:",
                reply_markup=universities_menu()
            )

        elif text == "🔙 К списку":
            user_state[uid] = "choose"
            await my_dirs(message)

        return

    # ===== УРОВЕНЬ ВУЗОВ =====
    if state == "universities":

        if text == "🌍 Все города":
            cities = ["Москва, название вуза", "Санкт-Петербург, название вуза", "Казань, название вуза",
                      "Новосибирск, название вуза"]
            cities_storage[uid] = cities
            user_state[uid] = "choose_city"

            city_text = ""
            for i, c in enumerate(cities, 1):
                city_text += f"{i}. {c}\n"

            city_text += "\nВыберите номер города, про который хотите узнать конкретнее."

            await message.answer(city_text, reply_markup=back_menu())

        elif text == "🔙 Назад":
            user_state[uid] = "actions"
            await message.answer(
                f"<b>{selected_direction[uid]}</b>\nВыберите действие:",
                reply_markup=direction_actions()
            )
        return

    # ===== ВЫБОР ГОРОДА =====
    if state == "choose_city" and text.isdigit():
        idx = int(text) - 1

        if 0 <= idx < len(cities_storage.get(uid, [])):
            selected_city[uid] = cities_storage[uid][idx]
            user_state[uid] = "city_detail"

            await message.answer(
                f"Город: {selected_city[uid]}",
                reply_markup=city_detail_menu(selected_direction[uid])
            )
        return

    # ===== ГОРОД — ДЕТАЛИ =====
    if state == "city_detail":

        if text.startswith("ℹ️ Информация"):
            await message.answer(
                f"Информация о направлении \"{selected_direction[uid]}\" "
                f"в городе {selected_city[uid]}.\n\n"
                f"(Заглушка — здесь будет информация из БД)",
                reply_markup=city_detail_menu(selected_direction[uid])
            )

        elif text == "🔙 Назад":
            user_state[uid] = "choose_city"

            cities = cities_storage.get(uid, [])
            city_text = ""
            for i, c in enumerate(cities, 1):
                city_text += f"{i}. {c}\n"

            city_text += "\nВыберите номер города."

            await message.answer(city_text, reply_markup=back_menu())

        return


# ================= MAIN =================

async def main():
    print("🤖 Bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
