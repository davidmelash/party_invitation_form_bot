from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


start_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="START"),
        ],

    ],
    resize_keyboard=True
)




contact_keyboard = ReplyKeyboardMarkup(resize_keyboard=True,
                               keyboard=[
                                   [
                                       KeyboardButton(text="Поделиться / Share ", request_contact=True)
                                   ]
                               ])


back_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Назад"),
        ],

    ],
    resize_keyboard=True
)
