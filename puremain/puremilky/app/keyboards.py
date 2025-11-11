from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
def lang_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang_uz")]
    ])

def sex_kb(lang):
    if lang == "ru":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Мужской", callback_data="sex_m")],
            [InlineKeyboardButton(text="Женский", callback_data="sex_f")]
        ])
    else:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Erkak", callback_data="sex_m")],
            [InlineKeyboardButton(text="Ayol", callback_data="sex_f")]
        ])


def phone_kb(lang):
    txt = "📱 Отправить номер" if lang == "ru" else "📱 Telefon raqamni jo'nating"
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=txt, request_contact=True)]],
        resize_keyboard=True
    )


# def start_survey_kb(lang):
#     txt_start = "📋 Новый опрос" if lang == "ru" else "📋 Yangi so'rov"
#     txt_export = "📊 Экспорт респондентов" if lang == "ru" else "📊 Javoblar ro'yxati"
    
#     return ReplyKeyboardMarkup(
#         keyboard=[
#             [KeyboardButton(text=txt_export)],
#             [KeyboardButton(text=txt_start)]
#         ],
#         resize_keyboard=True
#     )
def start_survey_kb(lang, username=None):
    txt_start = "📋 Новый опрос" if lang == "ru" else "📋 Yangi so'rov"
    txt_export = "📊 Экспорт респондентов" if lang == "ru" else "📊 Javoblar ro'yxati"
    
    keyboard = [[KeyboardButton(text=txt_start)]]
    
    # Only show export button for @feniskcom
    if username == "ZSH_007":
        keyboard.insert(0, [KeyboardButton(text=txt_export)])
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )

def milk_multi_kb(selected=None):
    opts = ["Pure Milky", "Musaffo", "Essi", "Kamilka", "AgroBravo", "Lactel", "Доброе деревенское утро", "Творог", "Другое"]
    selected = selected or set()
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"{'✅ ' if o in selected else ''}{o}", callback_data=f"milk:{o}")]
            for o in opts
        ] + [[InlineKeyboardButton(text="➡️ Продолжить", callback_data="milk_done")]]
    )
    return kb
REGIONS = [
    "Самарканд", "Ташкент", "Фергана", "Андижан", "Наманган",
    "Жиззах", "Гулистан", "Карши", "Термез", "Бухара",
    "Наваи", "Хорезм", "Нукус"
]

# клавиатура регионов
def region_kb():
    kb = []
    for r in REGIONS:
        kb.append([InlineKeyboardButton(text=r, callback_data=f"region_{r}")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

