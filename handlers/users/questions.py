import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import CallbackQuery

from data.config import CHAT
from keyboards.inline.buttons import additional_callback, cancel_keyboard, ask_button
from loader import dp, bot, db


class IsGroup(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        return message.chat.type in (
            types.ChatType.GROUP,
            types.ChatType.SUPERGROUP,
        )


@dp.callback_query_handler(additional_callback.filter(status="ask"))
async def ask_question(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("Пришлите ваш вопрос / Send your question", reply_markup=await cancel_keyboard("ask"))
    await state.set_state("get_questions")


@dp.callback_query_handler(additional_callback.filter(status="cancel_ask"), state="get_questions")
async def come_back_to_start(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text('Остались вопросы? Жми "Задать вопрос"\n'
                              'Still have questions? Click "Ask a question"', reply_markup=ask_button)
    
    await state.finish()


@dp.message_handler(state="get_questions", content_types=types.ContentType.ANY)
async def get_question(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        phone_numb = db.select_user(user_id=user_id)[2]
    except Exception as e:
        logging.info(e)
        phone_numb = "#"
    try:
        
        text = f"<b>Юзернейм: @{message.from_user.username}\nНомер телефона: {phone_numb}\nСообщение: </b>"
        await bot.send_message(chat_id=CHAT, text=text)
        await bot.forward_message(chat_id=CHAT, from_chat_id=user_id, message_id=message.message_id)
    
    except Exception as e:
        logging.info(e)
        await message.answer("Something went wrong...")
    else:
        await message.answer("Вопрос был отправлен успешно!\n"
                             "The question was sent successfully!")
    await state.finish()


@dp.message_handler(chat_type=types.ChatType.PRIVATE)
async def get_answer(message: types.Message):
    try:
        if message.reply_to_message and\
                message.reply_to_message.from_user.is_bot\
                and "ᅠ" in message.reply_to_message.text:
            
            user_id = message.from_user.id
            try:
                phone_numb = db.select_user(user_id=user_id)[2]
            except Exception as e:
                logging.info(e)
                phone_numb = "#"
            
            text = f"<b>Юзернейм: @{message.from_user.username}\nНомер телефона: {phone_numb}\nСообщение: </b>"
            await bot.send_message(chat_id=CHAT, text=text)
            await bot.forward_message(chat_id=CHAT, from_chat_id=user_id, message_id=message.message_id)
    except Exception as e:
        logging.info(e)

    
@dp.message_handler(IsGroup())
async def send_answer(message: types.Message):

    try:
        if message.reply_to_message and message.reply_to_message.forward_from:
            source_message = message.reply_to_message
            text = f"<b>Ответ на ваш вопрос / Answer for your questionᅠ</b>\n\n{message.text}"
            await bot.send_message(chat_id=source_message.forward_from.id, text=text)
    except Exception as e:
        logging.info(e)
