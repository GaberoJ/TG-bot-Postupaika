import asyncio
import re
import openai

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart

from config import TELEGRAM_TOKEN, my_key
from functions_db_bot import DatabaseBot

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

# ================= DATABASE =================
db_bot = DatabaseBot()

# ================= STORAGE =================

# ================= STORAGE =================

dialog_context = {}
user_state = {}
user_directions = {}
saved_directions = {}
saved_programs = {}
selected_direction = {}
selected_city = {}
cities_storage = {}
selected_vuz = {}
universities_list = {}


# ================= KEYBOARDS =================

def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📌 Мои направления")],
            [KeyboardButton(text="⭐ Сохранённые направления")],
            [KeyboardButton(text="⭐ Сохранённые программы")],  # Добавлено
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


def vuz_actions():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📚 Программы")],
            [KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True
    )

def programs_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔙 К выбору вуза")],
            [KeyboardButton(text="🔙 В меню")]
        ],
        resize_keyboard=True
    )

def program_actions():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⭐ Сохранить программу")],
            [KeyboardButton(text="🔙 К выбору вуза")],
            [KeyboardButton(text="🔙 В меню")]
        ],
        resize_keyboard=True
    )


def saved_programs_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🗑 Очистить сохранённые программы")],
            [KeyboardButton(text="🔙 В меню")]
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
    follow = await ask_agent(user_id, "Выдай полный список из 10 направлений. Только список.")
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


@dp.message(F.text == "⭐ Сохранённые программы")
async def saved_progs(message: Message):
    uid = message.from_user.id
    progs = saved_programs.get(uid)

    if not progs:
        await message.answer("Сохранённых программ нет.", reply_markup=main_menu())
        return

    user_state[uid] = "choose_saved_program"

    text = "<b>⭐ Сохранённые программы:</b>\n\n"
    for i, prog in enumerate(progs, 1):
        text += f"{i}. {prog['program_name']}\n"
        text += f"   🏫 {prog['vuz_name']}\n"
        text += f"   📍 {prog['city']}\n\n"

    text += "Введите номер программы, чтобы посмотреть подробную информацию:"

    await message.answer(text, reply_markup=saved_programs_menu())


@dp.message(F.text == "🗑 Очистить сохранённые программы")
async def clear_saved_programs_prompt(message: Message):
    uid = message.from_user.id
    user_state[uid] = "clear_saved_programs"

    await message.answer(
        "Введите номера программ через запятую (например: 1,3,5)",
        reply_markup=back_menu()
    )
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
            direction_name = dirs[uid][idx]
            direction_name = direction_name.rstrip('.')
            direction_name = direction_name.strip()

            selected_direction[uid] = direction_name
            user_state[uid] = "actions"
            await message.answer(
                f"<b>{direction_name}</b>\nВыберите действие:",
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

    # ===== ОЧИСТКА СОХРАНЁННЫХ =====
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

    # ===== УРОВЕНЬ ВУЗОВ (МЕНЮ) =====
    if state == "universities":
        if text == "🌍 Все города":
            direction = selected_direction.get(uid)
            if not direction:
                await message.answer("Ошибка: направление не выбрано", reply_markup=main_menu())
                return

            universities = db_bot.get_universities_by_direction(direction)
            if not universities:
                await message.answer(
                    f"❌ По направлению «{direction}» нет информации о вузах",
                    reply_markup=universities_menu()
                )
                return

            universities_list[uid] = universities
            user_state[uid] = "choose_vuz"

            # Разбиваем список вузов на части по 20 записей
            chunk_size = 20
            total_universities = len(universities)

            # Отправляем заголовок
            header = f"<b>🏫 {direction}</b>\n\n"
            header += f"Всего найдено: {total_universities} вузов\n\n"
            await message.answer(header, reply_markup=back_menu())

            # Отправляем список частями
            for chunk_start in range(0, total_universities, chunk_size):
                chunk_end = min(chunk_start + chunk_size, total_universities)
                chunk_text = ""

                for i in range(chunk_start, chunk_end):
                    uni = universities[i]
                    chunk_text += f"{i + 1}. {uni['city']}, {uni['vuz_name']}\n"

                await message.answer(chunk_text, reply_markup=None)
                await asyncio.sleep(0.3)

            # Отправляем финальное сообщение с инструкцией
            await message.answer(
                "Введите номер вуза, чтобы посмотреть программы:",
                reply_markup=back_menu()
            )

        elif text == "🔙 Назад":
            user_state[uid] = "actions"
            await message.answer(
                f"<b>{selected_direction[uid]}</b>\nВыберите действие:",
                reply_markup=direction_actions()
            )
        return

    # ===== ВЫБОР ВУЗА =====
    if state == "choose_vuz" and text.isdigit():
        idx = int(text) - 1
        universities = universities_list.get(uid, [])

        if 0 <= idx < len(universities):
            selected_vuz[uid] = universities[idx]
            user_state[uid] = "vuz_actions"

            vuz_info = universities[idx]
            await message.answer(
                f"<b>{vuz_info['vuz_name']}</b>\n"
                f"📍 {vuz_info['city']}\n\n"
                f"Выберите действие:",
                reply_markup=vuz_actions()
            )
        else:
            await message.answer("Неверный номер. Попробуйте снова:")
        return

    # ===== ДЕЙСТВИЯ С ВУЗОМ =====
    if state == "vuz_actions":
        # ===== ДЕЙСТВИЯ С ВУЗОМ =====
        if state == "vuz_actions":
            if text == "📚 Программы":
                direction = selected_direction.get(uid)
                vuz = selected_vuz.get(uid)

                if not direction or not vuz:
                    await message.answer("Ошибка: данные не найдены", reply_markup=main_menu())
                    return

                programs = db_bot.get_programs_by_university_and_direction(vuz['vuz_id'], direction)

                if not programs:
                    await message.answer(
                        f"❌ В данном вузе нет программ по направлению «{direction}»",
                        reply_markup=vuz_actions()
                    )
                    return

                # СОХРАНЯЕМ программы
                universities_list[f"{uid}_programs"] = programs
                user_state[uid] = "choose_program"

                # ФОРМИРУЕМ СПИСОК ПРОГРАММ
                text_msg = f"<b>📚 Программы обучения</b>\n"
                text_msg += f"{vuz['vuz_name']}\n"
                text_msg += f"Направление: {direction}\n\n"

                for i, prog in enumerate(programs, 1):
                    program_name = prog.get('program_name', prog['direction_name'])
                    text_msg += f"{i}. {program_name}\n"

                text_msg += "\nВведите номер программы для подробной информации:"

                # ИСПРАВЛЕНО: используем programs_menu вместо back_menu
                await message.answer(text_msg, reply_markup=programs_menu())
                return


        elif text == "🔙 Назад":
            user_state[uid] = "choose_vuz"
            universities = universities_list.get(uid, [])
            direction = selected_direction.get(uid)

            text_msg = f"<b>🏫 {direction}</b>\n\n"
            for i, uni in enumerate(universities, 1):
                text_msg += f"{i}. {uni['city']}, {uni['vuz_name']}\n"
            text_msg += "\nВведите номер вуза:"

            await message.answer(text_msg, reply_markup=back_menu())
            return
        return

    # ===== ВЫБОР ПРОГРАММЫ =====
    if state == "choose_program":
        if text.isdigit():
            idx = int(text) - 1
            programs = universities_list.get(f"{uid}_programs", [])

            if 0 <= idx < len(programs):
                selected_program = programs[idx]

                # Получаем детальную информацию о программе
                program_details = db_bot.get_program_details(selected_program['id'])

                if program_details:
                    # Добавляем vuz_name и city если их нет
                    if 'vuz_name' not in program_details:
                        vuz = selected_vuz.get(uid)
                        if vuz:
                            program_details['vuz_name'] = vuz['vuz_name']
                            program_details['city'] = vuz['city']

                    # Сохраняем выбранную программу
                    universities_list[f"{uid}_selected_program"] = program_details
                    user_state[uid] = "program_details"

                    # Форматируем и отправляем полную информацию
                    prog_info = db_bot.format_program_full(program_details)

                    # ОТПРАВКА С ОТКЛЮЧЕННЫМ HTML
                    await message.answer(
                        prog_info,
                        reply_markup=program_actions(),
                        disable_web_page_preview=True,
                        parse_mode=None  # Отключаем HTML парсинг
                    )
                else:
                    # Если не удалось получить детали, показываем базовую информацию
                    vuz = selected_vuz.get(uid)
                    if vuz:
                        selected_program['vuz_name'] = vuz['vuz_name']
                        selected_program['city'] = vuz['city']

                    universities_list[f"{uid}_selected_program"] = selected_program
                    user_state[uid] = "program_details"

                    prog_info = f"<b>📚 {selected_program.get('program_name', selected_program['direction_name'])}</b>\n"
                    prog_info += f"🏫 {selected_program['vuz_name']}\n"
                    prog_info += f"📍 {selected_program['city']}\n"
                    prog_info += f"📋 Направление: {selected_program['direction_name']}\n\n"
                    prog_info += "ℹ️ Детальная информация временно недоступна"

                    await message.answer(prog_info, reply_markup=program_actions())
            else:
                await message.answer("Неверный номер. Попробуйте снова:")
            return


    # ===== ВЫБОР СОХРАНЕННОЙ ПРОГРАММЫ =====
    if state == "choose_saved_program":
        if text.isdigit():
            idx = int(text) - 1
            progs = saved_programs.get(uid, [])

            if 0 <= idx < len(progs):
                selected_program = progs[idx]

                # Получаем детальную информацию о программе
                program_details = db_bot.get_program_details(selected_program['id'])

                if program_details:
                    # Добавляем vuz_name и city из сохраненных данных
                    program_details['vuz_name'] = selected_program['vuz_name']
                    program_details['city'] = selected_program['city']

                    # Сохраняем выбранную программу
                    universities_list[f"{uid}_selected_program"] = program_details
                    user_state[uid] = "program_details"

                    # Форматируем и отправляем полную информацию по частям
                    prog_messages = db_bot.format_program_full(program_details)

                    for i, msg in enumerate(prog_messages):
                        await message.answer(
                            msg,
                            reply_markup=program_actions() if i == len(prog_messages) - 1 else None,
                            disable_web_page_preview=True
                        )
                        await asyncio.sleep(0.3)
                else:
                    # Если не удалось получить детали, показываем сохраненную информацию
                    universities_list[f"{uid}_selected_program"] = selected_program
                    user_state[uid] = "program_details"

                    prog_info = f"<b>📚 {selected_program['program_name']}</b>\n"
                    prog_info += f"🏫 {selected_program['vuz_name']}\n"
                    prog_info += f"📍 {selected_program['city']}\n"
                    prog_info += f"📋 Направление: {selected_program['direction_name']}\n\n"
                    prog_info += "ℹ️ Детальная информация временно недоступна"

                    await message.answer(prog_info, reply_markup=program_actions())
            else:
                await message.answer("Неверный номер. Попробуйте снова:")
            return


    # ===== ОЧИСТКА СОХРАНЕННЫХ ПРОГРАММ =====
    if state == "clear_saved_programs":
        numbers = re.findall(r"\d+", text)
        numbers = sorted(set(int(n) - 1 for n in numbers), reverse=True)

        if uid in saved_programs:
            for n in numbers:
                if 0 <= n < len(saved_programs[uid]):
                    saved_programs[uid].pop(n)

        user_state[uid] = "menu"
        await message.answer("✅ Программы удалены", reply_markup=main_menu())
        return

    # ===== ДЕТАЛИ ПРОГРАММЫ =====
    if state == "program_details":
        if text == "⭐ Сохранить программу":
            saved_programs.setdefault(uid, [])
            selected_program = universities_list.get(f"{uid}_selected_program")

            if not selected_program:
                await message.answer("Ошибка: программа не выбрана", reply_markup=main_menu())
                return

            # Проверяем, не сохранена ли уже эта программа
            program_exists = False
            for prog in saved_programs[uid]:
                if prog['id'] == selected_program['id']:
                    program_exists = True
                    break

            if not program_exists:
                # Сохраняем нужные поля
                program_to_save = {
                    'id': selected_program['id'],
                    'program_name': selected_program.get('program_name', selected_program['direction_name']),
                    'vuz_name': selected_program['vuz_name'],
                    'city': selected_program['city'],
                    'direction_name': selected_program['direction_name']
                }
                saved_programs[uid].append(program_to_save)
                await message.answer("⭐ Программа сохранена", reply_markup=program_actions())
            else:
                await message.answer("⚠️ Программа уже сохранена", reply_markup=program_actions())

        elif text == "🔙 К выбору вуза":
            user_state[uid] = "choose_vuz"
            universities = universities_list.get(uid, [])
            direction = selected_direction.get(uid)

            text_msg = f"<b>🏫 {direction}</b>\n\n"
            for i, uni in enumerate(universities, 1):
                text_msg += f"{i}. {uni['city']}, {uni['vuz_name']}\n"
            text_msg += "\nВведите номер вуза:"

            await message.answer(text_msg, reply_markup=back_menu())

        elif text == "🔙 В меню":
            user_state[uid] = "menu"
            await message.answer("Главное меню:", reply_markup=main_menu())

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
    try:
        await dp.start_polling(bot)
    finally:
        db_bot.close()
        print("👋 Bot stopped")


if __name__ == "__main__":
    asyncio.run(main())