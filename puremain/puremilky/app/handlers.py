from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import app.keyboards as kb
from app.texts import texts
from app.database import add_promoter, add_respondent, export_respondents_to_excel_bytes, export_promoters_to_excel_bytes
from aiogram.types import FSInputFile, BufferedInputFile
import json
import os
from pathlib import Path
# BRANDS_FILE = "app/brands.json"
BASE_DIR = Path(__file__).resolve().parent  # app folder
BRANDS_FILE = BASE_DIR / "brands.json"
DEFAULT_BRANDS = [
    "Pure Milky", "Musaffo", "Essi", "Kamilka",
    "AgroBravo", "Lactel", "Доброе деревенское утро",
    "Другое", "Не знаю"
]


def load_brands(region):
    if not os.path.exists(BRANDS_FILE):
        with open(BRANDS_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=2)

    with open(BRANDS_FILE, "r", encoding="utf-8") as f:
        content = f.read()
        data = json.loads(content) if content.strip() else {}

    if region not in data:
        data[region] = DEFAULT_BRANDS.copy()
        save_all_brands(data)

    return data[region]


def save_brands(region, brands):
    if not os.path.exists(BRANDS_FILE):
        data = {}
    else:
        with open(BRANDS_FILE, "r", encoding="utf-8") as f:
            content = f.read()
            data = json.loads(content) if content.strip() else {}
    data[region] = brands
    save_all_brands(data)


def save_all_brands(data):
    with open(BRANDS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_region_brands(region):
    if not os.path.exists(BRANDS_FILE):
        with open(BRANDS_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=2)

    with open(BRANDS_FILE, "r", encoding="utf-8") as f:
        content = f.read()
        data = json.loads(content) if content.strip() else {}

    if region not in data:
        data[region] = DEFAULT_BRANDS.copy()

    return data


def save_region_brands(data):
    with open(BRANDS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


router = Router()
user_lang = {}

# ===== REGISTRATION STATES =====
class Reg(StatesGroup):
    name = State()
    age = State()
    sex = State()
    phone = State()
    region = State()
# ===== SURVEY STATES =====
class Survey(StatesGroup):
    phone= State()
    name = State()
    gender = State()
    age = State()
    q1 = State()
    q1_other = State()
    q2 = State()
    q3 = State()
    q4 = State()
    q5 = State()
    q6 = State()
    q7 = State()
    q2_multi = State()
    q3_multi = State()
    q8 = State()
    q9 = State()
    q2_other_multi=State()
    q3_other_multi=State()
    q2_other=State()
    q3_other=State()
    q4_other=State()
    q5_other=State()
    q6_other=State()

# ===== START COMMAND =====
@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Tilni tanlang / Выберите язык:", reply_markup=kb.lang_kb())

@router.callback_query(F.data.startswith("lang_"))
async def set_lang(c: CallbackQuery, state: FSMContext):
    lang = c.data.split("_")[1]
    user_lang[c.from_user.id] = lang
    await c.message.edit_text(texts[lang]["chosen"])
    await c.message.answer(texts[lang]["name"])
    await state.set_state(Reg.name)

# ===== REGISTRATION =====
@router.message(Reg.name)
async def reg_name(m: Message, state: FSMContext):
    await state.update_data(name=m.text)
    lang = user_lang[m.from_user.id]
    await m.answer(texts[lang]["age"])
    await state.set_state(Reg.age)

@router.message(Reg.age)
async def reg_age(m: Message, state: FSMContext):
    await state.update_data(age=m.text)
    lang = user_lang[m.from_user.id]
    await m.answer(texts[lang]["sex"], reply_markup=kb.sex_kb(lang))
    await state.set_state(Reg.sex)


@router.callback_query(Reg.sex)
async def reg_sex(c: CallbackQuery, state: FSMContext):
    await state.update_data(sex=c.data.split("_")[1])
    lang = user_lang[c.from_user.id]
    await c.message.answer("Viloyatingizni kiriting:",reply_markup=kb.region_kb())
    await state.set_state(Reg.region)


@router.callback_query(Reg.region)
async def reg_region(c: CallbackQuery, state: FSMContext):
    region = c.data.split("_", 1)[1]
    await state.update_data(region=region)
    lang = user_lang[c.from_user.id]
    await c.message.answer(texts[lang]["phone"], reply_markup=kb.phone_kb(lang))
    await state.set_state(Reg.phone)

@router.message(Reg.phone, F.contact)
async def reg_phone(m: Message, state: FSMContext):
    await state.update_data(phone=m.contact.phone_number)
    lang = user_lang[m.from_user.id]
    data = await state.get_data()
    region = data["region"]
    add_promoter(m.from_user.id, data["name"], data["age"], data["phone"], lang, region)
    
    # Store region for this user permanently
    user_lang[f"{m.from_user.id}_region"] = region
    
    await m.answer(texts[lang]["done"], reply_markup=ReplyKeyboardRemove())
    print(await state.get_data())
    await state.clear()
    
    # Show keyboard based on username
    username = m.from_user.username
    await m.answer(texts[lang]["req11"], reply_markup=kb.start_survey_kb(lang, username))


BOOL=["Да", "Нет"]

def milk_multi_kb(region, selected=None):
    selected = selected or set()
    brands = load_brands(region)  
    kb_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"{'✅ ' if b in selected else ''}{b}",
                    callback_data=f"milk:{b}"
                )
            ] for b in brands
        ] + [[InlineKeyboardButton(text="➡️ Продолжить", callback_data="milk_done")]]
    )
    return kb_markup

def milk_multi_kb2(region,selected=None):
    selected = selected or set()
    brands = load_brands(region)  
    kb_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"{'✅ ' if o in selected else ''}{o}", callback_data=f"milk:{o}")]
            for o in brands
        ] + [[InlineKeyboardButton(text="➡️ Продолжить", callback_data="milk_done")]]
    )
    return kb_markup


def kb_idx(options, prefix):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=o, callback_data=f"{prefix}:{i}")]
            for i, o in enumerate(options)
        ]
    )
def kb_bool(options, prefix):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=o, callback_data=f"{prefix}:{i}")]
            for i, o in enumerate(options)
        ]
    )

@router.message(F.text.in_(["📋 Новый опрос", "📋 Yangi so'rov"]))
async def start_survey(m: Message, state: FSMContext):
    lang = user_lang[m.from_user.id]
    # Get promoter's region from stored data
    region = user_lang.get(f"{m.from_user.id}_region", "default")
    await state.update_data(region=region)
    await m.answer(texts[lang]["name2"])
    await state.set_state(Survey.name)
#-------------------------------------------------------------
@router.message(Survey.name)
async def get_name(m: Message, state: FSMContext):
    await state.update_data(name=m.text)
    lang = user_lang[m.from_user.id]
    await m.answer(texts[lang]["gender"], reply_markup=kb.sex_kb(lang))
    await state.set_state(Survey.gender)

@router.callback_query(Survey.gender)
async def get_gender(c: CallbackQuery, state: FSMContext):
    _, i = c.data.split("_")
    val = "Мужской" if i == "m" else "Женский"
    await state.update_data(gender=val)
    lang = user_lang[c.from_user.id]
    await c.message.edit_text(
        texts[lang]["age"],
        reply_markup=kb_idx(
            [str(texts[lang]["before"]), "18-24", "25-34", "35-44", "45-54", "54+"],
            "a"
        )
    )
    await state.set_state(Survey.age)


@router.callback_query(Survey.age)
async def get_age(c: CallbackQuery, state: FSMContext):
    _, i = c.data.split(":")
    val = ["до 18", "18-24", "25-34", "35-44", "45-54", "54+"][int(i)]
    await state.update_data(age=val)
    lang = user_lang[c.from_user.id]
    await c.message.edit_text(f"{texts[lang]['age']} ✅")
    await c.message.answer(texts[lang]["phone"])
    await state.set_state(Survey.phone)

@router.message(Survey.phone)
async def get_phone(m: Message, state: FSMContext):
    await state.update_data(phone=m.text)
    lang = user_lang[m.from_user.id]
    data = await state.get_data()
    region = data.get("region", "default")
    brands = load_brands(region)
    await m.answer("1. " + texts[lang]["q1"], reply_markup=kb_idx(brands, "q1"))
    await state.set_state(Survey.q1)

@router.callback_query(Survey.q1)
async def q1(c: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    region = data.get("region", "default")
    _, i = c.data.split(":")
    brands = load_brands(region)
    val = brands[int(i)]
    lang = user_lang[c.from_user.id]
    
    if val == "Другое":
        await c.message.edit_text(texts[lang]["type"])
        await state.set_state(Survey.q1_other)
        return
    
    await state.update_data(q1=val)
    await c.message.edit_text("2. " + texts[lang]["q8"], reply_markup=milk_multi_kb(region))
    await state.set_state(Survey.q2_multi)


@router.message(Survey.q1_other)
async def q1_other(m: Message, state: FSMContext):
    user_input = m.text.strip()
    data = await state.get_data()
    region = data.get("region", "default")
    brands = load_brands(region)

    if user_input not in brands:
        brands.insert(-2, user_input)
        save_brands(region, brands)
    
    await state.update_data(q1=user_input)
    lang = user_lang[m.from_user.id]
    await m.answer("2. " + texts[lang]["q8"], reply_markup=milk_multi_kb(region=region))
    await state.set_state(Survey.q2_multi)



# ----------- ВОПРОС 2 (мультивыбор) -------------
@router.callback_query(Survey.q2_multi)
async def q2_multi(c: CallbackQuery, state: FSMContext):
    lang = user_lang[c.from_user.id]
    data = await state.get_data()
    region = data.get("region", "default")
    selected = set(data.get("q2_selected", set()))
    brands = load_brands(region)

    if c.data == "milk_done":
        if not selected:
            await c.answer(texts[lang]["res1"])
            return

        if "Другое" in selected:
            await c.message.edit_text(texts[lang]["write"])
            await state.update_data(q2_selected=selected)
            await state.set_state(Survey.q2_other_multi)
            return

        await state.update_data(q2=", ".join(selected))
        await c.message.edit_text("3. " + texts[lang]["q9"], reply_markup=milk_multi_kb(region=region))
        await state.set_state(Survey.q3_multi)
        return

    if not c.data.startswith("milk:"):
        await c.answer()
        return

    item = c.data.split("milk:")[1]
    if item in selected:
        selected.remove(item)
    else:
        selected.add(item)

    await state.update_data(q2_selected=selected)
    await c.message.edit_reply_markup(reply_markup=milk_multi_kb(selected=selected, region=region))
    await c.answer()

@router.message(Survey.q2_other_multi)
async def q2_other_multi(m: Message, state: FSMContext):
    lang = user_lang[m.from_user.id]
    d = await state.get_data()
    user_region = d.get("region", "default")
    s = set(d.get("q2_selected", set()))

    # Remove "Другое" first
    if "Другое" in s:
        s.remove("Другое")

    user_input = m.text.strip()
    
    # Add the new brand to region brands if it doesn't exist
    if user_input:
        data = load_region_brands(user_region)
        region_brands = data[user_region]

        if user_input not in region_brands:
            region_brands.insert(-2, user_input)
            save_region_brands(data)
        
        # Add user input to selected set
        s.add(user_input)

    # Save the updated selection with actual brand name
    await state.update_data(q2=", ".join(s), q2_selected=list(s))

    await m.answer("3. " + texts[lang]["q9"], reply_markup=milk_multi_kb(region=user_region))
    await state.set_state(Survey.q3_multi)


# ----------- ВОПРОС 3 (мультивыбор) -------------
@router.callback_query(Survey.q3_multi)
async def q3_multi(c: CallbackQuery, state: FSMContext):
    lang = user_lang[c.from_user.id]
    d = await state.get_data()
    region = d.get("region", "default")
    s = set(d.get("q3_selected", set()))
    brands = load_brands(region)

    if c.data == "milk_done":
        if not s:
            await c.answer(texts[lang]["res1"])
            return

        if "Другое" in s:
            await c.message.edit_text(texts[lang]["write"])
            await state.update_data(q3_selected=s)
            await state.set_state(Survey.q3_other_multi)
            return

        await state.update_data(q3=", ".join(s))
        await c.message.edit_text("4. " + texts[lang]["q2"], reply_markup=kb_idx(brands, "q5"))
        await state.set_state(Survey.q2)
        return

    if not c.data.startswith("milk:"):
        await c.answer()
        return

    item = c.data.split("milk:")[1]
    if item in s:
        s.remove(item)
    else:
        s.add(item)

    await state.update_data(q3_selected=s)
    await c.message.edit_reply_markup(reply_markup=milk_multi_kb(region, s))
    await c.answer()


@router.message(Survey.q3_other_multi)
async def q3_other_multi(m: Message, state: FSMContext):
    lang = user_lang[m.from_user.id]
    d = await state.get_data()
    user_region = d.get("region", "default")
    s = set(d.get("q3_selected", set()))
    
    # Remove "Другое" first
    if "Другое" in s:
        s.remove("Другое")
    
    user_input = m.text.strip()
    
    # Add the new brand to region brands if it doesn't exist
    if user_input:
        region_brands_data = load_region_brands(user_region)
        region_brands = region_brands_data[user_region]
        
        if user_input not in region_brands:
            region_brands.insert(-2, user_input)
            save_region_brands(region_brands_data)
        
        # Add user input to selected set
        s.add(user_input)

    # Save the updated selection with actual brand name
    await state.update_data(q3=", ".join(s), q3_selected=list(s))
    await m.answer("4. " + texts[lang]["q2"], reply_markup=kb_idx(region_brands, "q5"))
    await state.set_state(Survey.q2)

@router.callback_query(Survey.q2)
async def q2(c: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    region = data.get("region", "default")
    brands = load_brands(region)
    _, i = c.data.split(":")
    val = brands[int(i)]
    lang = user_lang[c.from_user.id]
    if val == "Другое":
        await c.message.edit_text(texts[lang]["type"])
        await state.set_state(Survey.q3_other)
        return
    await state.update_data(q2=val)
    await c.message.edit_text("5. " + texts[lang]["q3"], reply_markup=kb_idx(brands, "q3"))
    await state.set_state(Survey.q3)


@router.message(Survey.q3_other)
async def get_q3_other(m: Message, state: FSMContext):
    await state.update_data(q2=m.text)
    user_input = m.text.strip()
    data = await state.get_data()
    region = data.get("region", "default")
    brands = load_brands(region)
    if user_input not in brands:
        brands.insert(-2, user_input)
        save_brands(region, brands)
    lang = user_lang[m.from_user.id]
    await m.answer("5. " + texts[lang]["q3"], reply_markup=kb_idx(brands, "q3"))
    await state.set_state(Survey.q3)


@router.callback_query(Survey.q3)
async def q3(c: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    region = data.get("region", "default")
    brands = load_brands(region)
    _, i = c.data.split(":")
    val = brands[int(i)]
    lang = user_lang[c.from_user.id]
    if val == "Другое":
        await c.message.edit_text(texts[lang]["type"])
        await state.set_state(Survey.q4_other)
        return
    await state.update_data(q3=val)
    await c.message.edit_text("6. " + texts[lang]["q10"], reply_markup=kb_idx(BOOL, "q4"))
    await state.set_state(Survey.q4)


@router.message(Survey.q4_other)
async def get_q4_other(m: Message, state: FSMContext):
    await state.update_data(q3=m.text)
    user_input = m.text.strip()
    data = await state.get_data()
    region = data.get("region", "default")
    brands = load_brands(region)
    if user_input not in brands:
        brands.insert(-2, user_input)
        save_brands(region, brands)
    lang = user_lang[m.from_user.id]
    await m.answer("6. " + texts[lang]["q10"], reply_markup=kb_bool(BOOL, "q4"))
    await state.set_state(Survey.q4)


@router.callback_query(Survey.q4)
async def q4(c: CallbackQuery, state: FSMContext):
    _, i = c.data.split(":")
    val = BOOL[int(i)]
    lang = user_lang[c.from_user.id]
    data = await state.get_data()
    region = data.get("region", "default")
    brands = load_brands(region)
    if val == "Другое":
        await c.message.edit_text(texts[lang]["type"])
        await state.set_state(Survey.q5_other)
        return
    await state.update_data(q4=val)
    await c.message.edit_text("7. " + texts[lang]["q5"], reply_markup=kb_idx(brands, "q5"))
    await state.set_state(Survey.q5)


@router.message(Survey.q5_other)
async def get_q5_other(m: Message, state: FSMContext):
    await state.update_data(q4=m.text)
    user_input = m.text.strip()
    data = await state.get_data()
    region = data.get("region", "default")
    brands = load_brands(region)
    if user_input not in brands:
        brands.insert(-2, user_input)
        save_brands(region, brands)
    lang = user_lang[m.from_user.id]
    await m.answer("7. " + texts[lang]["q5"], reply_markup=kb_idx(brands, "q5"))
    await state.set_state(Survey.q5)

@router.callback_query(Survey.q5)
async def q5(c: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    region = data.get("region", "default")
    brands = load_brands(region)
    _, i = c.data.split(":")
    val = brands[int(i)]
    lang = user_lang[c.from_user.id]
    if val == "Другое":
        await c.message.edit_text(texts[lang]["type"])
        await state.set_state(Survey.q6_other)
        return
    await state.update_data(q5=val)

    await c.message.edit_text("8. " + texts[lang]["q6"], reply_markup=kb_idx(brands, "q6"))
    await state.set_state(Survey.q6)

@router.message(Survey.q6_other)
async def get_q6_other(m: Message, state: FSMContext):
    await state.update_data(q5=m.text)
    user_input = m.text.strip()
    data = await state.get_data()
    region = data.get("region", "default")
    brands = load_brands(region)
    if user_input not in brands:
        brands.insert(-2, user_input)
        save_brands(region, brands)
    lang = user_lang[m.from_user.id]
    await m.answer("8. " + texts[lang]["q6"], reply_markup=kb_idx(brands, "q6"))
    await state.set_state(Survey.q6)

@router.callback_query(Survey.q6)
async def q6(c: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    region = data.get("region", "default")
    brands = load_brands(region)
    _, i = c.data.split(":")
    val = brands[int(i)]
    lang = user_lang[c.from_user.id]
    if val == "Другое":
        await c.message.edit_text(texts[lang]["type"])
        await state.set_state(Survey.q6_other)
        return
    await state.update_data(q6=val)
    await c.message.edit_text("9. " + texts[lang]["q7"])
    await state.set_state(Survey.q7)


@router.message(Survey.q6_other)
async def get_q6_other2(m: Message, state: FSMContext):
    await state.update_data(q6=m.text)
    user_input = m.text.strip()
    data = await state.get_data()
    region = data.get("region", "default")
    brands = load_brands(region)
    if user_input not in brands:
        brands.insert(-2, user_input)
        save_brands(region, brands)
    lang = user_lang[m.from_user.id]
    await m.answer("9. " + texts[lang]["q7"])
    await state.set_state(Survey.q7)

@router.message(Survey.q7)
async def get_q7(m: Message, state: FSMContext):
    await state.update_data(q7=m.text)
    data = await state.get_data()
    lang = user_lang[m.from_user.id]
    success = add_respondent(m.from_user.id, data)
    if not success:
        await m.answer(texts[lang]["error"])
        return
    print("Survey result:", data)
    await m.answer(texts[lang]["finish"])
    await state.clear()


@router.message(F.text.in_(["📊 Экспорт респондентов","📊 Javoblar ro'yxati"]))
async def export_respondents(m: Message):
    # Debug: print username
    username = m.from_user.username
    print(f"Export button pressed by: @{username} (user_id: {m.from_user.id})")
    
    # Only allow user @fenikscom
    if username != "fenikscom":
        print(f"Access denied for @{username}")
        await m.answer("⛔️ Access denied")
        return
    
    print("Access granted, exporting data...")
    lang = user_lang.get(m.from_user.id, "ru")
    
    # Export respondents
    respondents_buf = export_respondents_to_excel_bytes()
    if respondents_buf:
        respondents_file = BufferedInputFile(respondents_buf.getvalue(), filename="respondents.xlsx")
        await m.answer_document(respondents_file, caption="📋 Respondents list")
        print("Respondents file sent")
    else:
        await m.answer("No respondents data")
        print("No respondents data")
    
    # Export promoters
    try:
        promoters_buf = export_promoters_to_excel_bytes()
        if promoters_buf:
            promoters_file = BufferedInputFile(promoters_buf.getvalue(), filename="promoters.xlsx")
            await m.answer_document(promoters_file, caption="👥 Promoters list")
            print("Promoters file sent")
        else:
            await m.answer("No promoters data")
            print("No promoters data")
    except Exception as e:
        error_msg = f"Error exporting promoters: {str(e)}"
        await m.answer(error_msg)
        print(error_msg)