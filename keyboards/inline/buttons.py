from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

gender_callback = CallbackData("gender", "g")
party_callback = CallbackData("party", "city", "flag")
accept_callback = CallbackData("i", "accept")

admin_callback = CallbackData("admin", "status")
user_back_callback = CallbackData("user", "status", "m_id")

additional_callback = CallbackData("user", "status")

gender_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Male 🤴🏼", callback_data=gender_callback.new(g="Male")),
        InlineKeyboardButton(text="Female 👸🏼", callback_data=gender_callback.new(g="Female"))
    ],
    [
        InlineKeyboardButton(text="Назад / Back", callback_data=user_back_callback.new(status="date_of_birth", m_id="#")),
    ]
])

accept_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Я принимаю и соглашаюсь с правилами",
                             callback_data=accept_callback.new(accept="True"))
    ],
    [
        InlineKeyboardButton(text="I accept and agree with the rules",
                             callback_data=accept_callback.new(accept="True")),
    ],
    [
        InlineKeyboardButton(text="Назад / Back",
                             callback_data=user_back_callback.new(status="social_links", m_id="#")),
    ],
])


admin_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Рассылка", callback_data=admin_callback.new(status="message")),
        InlineKeyboardButton(text="Очистить таблицы", callback_data=admin_callback.new(status="clear")),
    ],
    [
        InlineKeyboardButton(text="Настройка опроса", callback_data=admin_callback.new(status="settings")),
    ],
    [
        InlineKeyboardButton(text="Выход", callback_data=admin_callback.new(status="exit"))
    ]
])


message_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Приглашенные", callback_data=admin_callback.new(status="invited")),
        InlineKeyboardButton(text="Не приглашенные", callback_data=admin_callback.new(status="not_invited")),
    ],
    [
        InlineKeyboardButton(text="Все пользователи", callback_data=admin_callback.new(status="all_users")),
        InlineKeyboardButton(text="Третья таблица", callback_data=admin_callback.new(status="third_table")),
    ],
    [
        InlineKeyboardButton(text="Назад", callback_data=admin_callback.new(status="back")),
    ]

])


clear_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Очистить", callback_data=admin_callback.new(status="clear_tables")),
    ],
    [
        InlineKeyboardButton(text="Назад", callback_data=admin_callback.new(status="back")),
    ]
])


cleared_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Да", callback_data=admin_callback.new(status="cleared_tables")),
        InlineKeyboardButton(text="Нет", callback_data=admin_callback.new(status="back")),
    ],
])


settings_keyboard_1 = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Открыть доступ", callback_data=admin_callback.new(status="open_")),
    ],
    [
        InlineKeyboardButton(text="Назад", callback_data=admin_callback.new(status="back")),
    ]
])

settings_keyboard_2 = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Закрыть доступ", callback_data=admin_callback.new(status="close_")),
    ],
    [
        InlineKeyboardButton(text="Назад", callback_data=admin_callback.new(status="back")),
    ]
])

back_button = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Назад", callback_data=admin_callback.new(status="back_to_message")),
    ],
])


async def back(clback, id="#"):
    keyboar = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Назад / Back", callback_data=user_back_callback.new(status=clback, m_id=id)),
        ],
    ])
    return keyboar


start_button = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="START", callback_data=additional_callback.new(status="start"))
    ],
])


async def cancel_keyboard(pointer="#"):
    button = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Отмена / Cancel", callback_data=additional_callback.new(status=f"cancel_{pointer}"))
        ],
    ])
    return button


ask_button = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Задать вопрос / Ask a question", callback_data=additional_callback.new(status="ask"))
    ],
])