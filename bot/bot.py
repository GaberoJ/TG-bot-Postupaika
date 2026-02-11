import asyncio
import re
import openai
import psycopg2

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart

from config import (
    TELEGRAM_TOKEN, YANDEX_API_KEY, YANDEX_PROJECT_ID, YANDEX_AGENT_ID,
    DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
)

# ================= TELEGRAM =================

bot = Bot(
    token=TELEGRAM_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# ================= YANDEX AGENT =================

client = openai.OpenAI(
    api_key=YANDEX_API_KEY,
    base_url="https://rest-assistant.api.cloud.yandex.net/v1",
    project=YANDEX_PROJECT_ID
)

AGENT_ID = YANDEX_AGENT_ID

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


# ================= DATABASE =================

def _get_conn():
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT,
        database=DB_NAME, user=DB_USER, password=DB_PASSWORD
    )


def _query_direction_info(direction_name: str) -> dict | None:
    """Получить информацию о направлении по имени."""
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            d.num_dir, d.name_dir,
            COUNT(DISTINCT p.id) as program_count,
            COUNT(DISTINCT v.id) as vuz_count,
            COUNT(DISTINCT v.city) as city_count,
            MIN(p.education_cost_from) FILTER (WHERE p.education_cost_from > 0) as min_cost,
            SUM(p.count_budget) as total_budget
        FROM directions d
        LEFT JOIN programs p ON p.direction_id = d.id
        LEFT JOIN vuzi v ON v.id = p.vuz_id
        WHERE d.name_dir ILIKE %s
        GROUP BY d.id, d.num_dir, d.name_dir
        LIMIT 1
    """, (f"%{direction_name}%",))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        return None
    return {
        "num_dir": row[0], "name_dir": row[1],
        "program_count": row[2], "vuz_count": row[3],
        "city_count": row[4], "min_cost": row[5],
        "total_budget": row[6]
    }


def _query_cities(direction_name: str) -> list[dict]:
    """Получить города, в которых есть направление."""
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT v.city, COUNT(DISTINCT v.id) as vuz_count
        FROM vuzi v
        JOIN programs p ON p.vuz_id = v.id
        JOIN directions d ON d.id = p.direction_id
        WHERE d.name_dir ILIKE %s AND v.city IS NOT NULL
        GROUP BY v.city
        ORDER BY vuz_count DESC
    """, (f"%{direction_name}%",))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"city": r[0], "vuz_count": r[1]} for r in rows]


def _query_programs_in_city(direction_name: str, city: str) -> list[dict]:
    """Получить программы по направлению в конкретном городе."""
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            v.name as vuz_name,
            p.name as program_name,
            p.has_budget, p.count_budget,
            p.has_contract, p.count_contract,
            p.education_cost_from,
            e_b.passing_grade as budget_pass,
            e_b.average_passing_grade as budget_avg,
            e_c.passing_grade as contract_pass
        FROM programs p
        JOIN vuzi v ON v.id = p.vuz_id
        JOIN directions d ON d.id = p.direction_id
        LEFT JOIN entrance e_b ON e_b.program_id = p.id AND e_b.type = 'budget'
        LEFT JOIN entrance e_c ON e_c.program_id = p.id AND e_c.type = 'contract'
        WHERE d.name_dir ILIKE %s AND v.city = %s
        ORDER BY e_b.passing_grade DESC NULLS LAST
    """, (f"%{direction_name}%", city))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{
        "vuz": r[0], "program": r[1],
        "has_budget": r[2], "count_budget": r[3],
        "has_contract": r[4], "count_contract": r[5],
        "cost": r[6], "budget_pass": r[7],
        "budget_avg": r[8], "contract_pass": r[9]
    } for r in rows]


async def get_direction_info(name: str):
    return await asyncio.to_thread(_query_direction_info, name)


async def get_cities(name: str):
    return await asyncio.to_thread(_query_cities, name)


async def get_programs_in_city(name: str, city: str):
    return await asyncio.to_thread(_query_programs_in_city, name, city)


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
            info = await get_direction_info(selected_direction[uid])
            if info:
                info_text = (
                    f"<b>{info['name_dir']}</b>\n"
                    f"Код: {info['num_dir']}\n\n"
                    f"Программ: {info['program_count']}\n"
                    f"Вузов: {info['vuz_count']}\n"
                    f"Городов: {info['city_count']}\n"
                )
                if info['total_budget']:
                    info_text += f"Бюджетных мест (всего): {info['total_budget']}\n"
                if info['min_cost']:
                    info_text += f"Стоимость от: {info['min_cost']:,} руб./год\n".replace(",", " ")
            else:
                info_text = f"Направление «{selected_direction[uid]}» не найдено в базе."
            await message.answer(info_text, reply_markup=direction_actions())

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
            cities_data = await get_cities(selected_direction[uid])

            if not cities_data:
                await message.answer(
                    "Города не найдены для этого направления.",
                    reply_markup=universities_menu()
                )
                return

            cities = [c["city"] for c in cities_data]
            cities_storage[uid] = cities
            user_state[uid] = "choose_city"

            city_text = "<b>Города:</b>\n\n"
            for i, c in enumerate(cities_data, 1):
                city_text += f"{i}. {c['city']} ({c['vuz_count']} вуз.)\n"

            city_text += "\nВыберите номер города."

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
            programs = await get_programs_in_city(
                selected_direction[uid], selected_city[uid]
            )

            if not programs:
                await message.answer(
                    "Программы не найдены.",
                    reply_markup=city_detail_menu(selected_direction[uid])
                )
            else:
                result = f"<b>{selected_direction[uid]}</b>\n"
                result += f"Город: {selected_city[uid]}\n\n"

                for p in programs[:10]:
                    result += f"<b>{p['vuz']}</b>\n"
                    if p['program']:
                        result += f"  {p['program']}\n"
                    if p['has_budget'] and p['count_budget']:
                        result += f"  Бюджет: {p['count_budget']} мест"
                        if p['budget_pass']:
                            result += f" | проходной {p['budget_pass']}"
                        if p['budget_avg']:
                            result += f" (средний {p['budget_avg']})"
                        result += "\n"
                    if p['has_contract'] and p['cost']:
                        result += f"  Контракт: от {p['cost']:,} руб.".replace(",", " ")
                        if p['contract_pass']:
                            result += f" | проходной {p['contract_pass']}"
                        result += "\n"
                    result += "\n"

                if len(programs) > 10:
                    result += f"<i>...и ещё {len(programs) - 10} программ</i>"

                await message.answer(
                    result,
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
