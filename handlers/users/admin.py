import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import CallbackQuery

from aiogram_broadcaster import MessageBroadcaster

from data.config import ADMINS
from keyboards.inline import admin_keyboard
from keyboards.inline.buttons import admin_callback, message_keyboard, back_button, clear_keyboard, settings_keyboard_1, \
    settings_keyboard_2, cleared_keyboard
from loader import dp, our_sheet, db
from utils.connector import spreadsheet_id_2, spreadsheet_id_1, spreadsheet_id_3


@dp.callback_query_handler(admin_callback.filter(status="back_to_message"),
                           state=["choose_invited", "choose_not_invited", "choose_all_users", "choose_third_table"])
async def back_to_mailing(call: CallbackQuery, state: FSMContext):
    
    await call.message.edit_text("<b>Admin menu</b>")
    await call.message.edit_reply_markup(message_keyboard)
    await state.set_state("message")
    
    
@dp.callback_query_handler(admin_callback.filter(status="back"), state=["message", "clear", "settings", "cleared"])
async def back_to_admin_panel(call: CallbackQuery, state: FSMContext):

    await call.message.edit_text("<b>Admin menu</b>")
    await call.message.edit_reply_markup(admin_keyboard)
    await state.set_state("admin_main_menu")

 
@dp.callback_query_handler(admin_callback.filter(status="exit"), state="admin_main_menu")
async def exit_from_admin_panel(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await state.finish()

# ------------------------------buttons like "back" on top------------------------------------


@dp.message_handler(Command("admin"), user_id=ADMINS, state="*")
async def admin_panel(message: types.Message, state: FSMContext):
    await message.answer("<b>Admin menu</b>", reply_markup=admin_keyboard)
    await state.set_state("admin_main_menu")


# --------------- start of "mailing" block -----------------

@dp.callback_query_handler(admin_callback.filter(status="message"), state="admin_main_menu")
async def mailing_panel(call: CallbackQuery, state: FSMContext):

    await call.message.edit_reply_markup(message_keyboard)
    await state.set_state("message")
    
    
@dp.callback_query_handler(admin_callback.filter(status=["invited", "not_invited", "all_users", "third_table"]),
                           state="message")
async def updating_state_for_mailing(call: CallbackQuery, state: FSMContext, callback_data: dict):

    status = callback_data.get("status")
    if status == "invited":
        await state.set_state("choose_invited")
    elif status == "not_invited":
        await state.set_state("choose_not_invited")
    elif status == "all_users":
        await state.set_state("choose_all_users")
    elif status == "third_table":
        await state.set_state("choose_third_table")

    await call.message.edit_text("<b>Пришлите пост / сообщение для начала рассылки</b>")
    await call.message.edit_reply_markup(back_button)


@dp.message_handler(state=["choose_invited", "choose_not_invited"], content_types=types.ContentType.ANY)
async def mailing_invited_not_invited(message: types.Message, state: FSMContext):
    
    try:
        invited_users = (our_sheet.get_telegram_ids(spreadsheet_id_2, "A2:A"))["values"][0]  # second table
        data = (our_sheet.get_telegram_ids(spreadsheet_id_1, "A2:A"))["values"][0]
        not_invited_users = list(set(data) - set(invited_users))
        user_state = await state.get_state()
        
        if user_state == "choose_invited":
            await MessageBroadcaster(invited_users, message).run()
        else:
            await MessageBroadcaster(not_invited_users, message).run()
    except Exception as e:
        logging.info(e)
        await message.answer("Something went wrong. Tables must have at least one id")
    else:
        await message.answer("<b>Сообщение было отправленно упешно!</b>\n"
                             "<i>Пришлите новый пост / сообщение для новой рассылки</i>", reply_markup=back_button)


@dp.message_handler(state="choose_all_users", content_types=types.ContentType.ANY)
async def mailing_all(message: types.Message, state: FSMContext):
    try:
        users = [user[0] for user in db.select_all_users()]
        await MessageBroadcaster(users, message).run()
    except Exception as e:
        logging.info(e)
        await message.answer(f"Something went wrong. Error: {e}")
    else:
        await message.answer("<b>Сообщение было отправленно упешно!</b>\n"
                             "<i>Пришлите новый пост / сообщение для новой рассылки</i>", reply_markup=back_button)
        
        
@dp.message_handler(state="choose_third_table", content_types=types.ContentType.ANY)
async def mailing_third_table(message: types.Message, state: FSMContext):
    try:
        third_table = (our_sheet.get_telegram_ids(spreadsheet_id_3, "A2:A"))["values"][0]
        await MessageBroadcaster(third_table, message).run()
    except Exception as e:
        logging.info(e)
        await message.answer(f"Something went wrong. Error: {e}")
    else:
        await message.answer("<b>Сообщение было отправленно упешно!</b>\n"
                             "<i>Пришлите новый пост / сообщение для новой рассылки</i>", reply_markup=back_button)
    
# --------------- end of "mailing" block -----------------


# --------------- start of "clean" block -----------------

@dp.callback_query_handler(admin_callback.filter(status="clear"), state="admin_main_menu")
async def clear_table(call: CallbackQuery, state: FSMContext):

    await call.message.edit_text("<b>Нажмите на кнопку ниже для очистки таблиц</b>")
    await call.message.edit_reply_markup(clear_keyboard)
    await state.set_state("clear")


@dp.callback_query_handler(admin_callback.filter(status="clear_tables"), state="clear")
async def ask_to_confirm(call: CallbackQuery, state: FSMContext):

    await call.message.edit_text("<b>Вы уверены, что хотите очистить таблицы ?</b>")
    await call.message.edit_reply_markup(cleared_keyboard)
    await state.set_state("cleared")


@dp.callback_query_handler(admin_callback.filter(status="cleared_tables"), state="cleared")
async def notify_user(call: CallbackQuery, state: FSMContext):

    our_sheet.clear_sheet(spreadsheet_id_2)
    our_sheet.clear_sheet(spreadsheet_id_1)
    await call.answer("Таблицы были очищены")
    await back_to_admin_panel(call, state)
 
# --------------- end of "clean" block -----------------


# --------------- start of "settings" block -----------------

@dp.callback_query_handler(admin_callback.filter(status=["settings", "close_", "open_"]), state=["admin_main_menu", "settings"])
async def change_access(call: CallbackQuery, state: FSMContext, callback_data: dict):

    text = {"open": "РАЗРЕШЕН", "close": "ЗАПРЕЩЕН"}
    call_status = callback_data.get("status")
    
    if call_status == "close_":
        db.update_bot_status(status="close")
        
    elif call_status == "open_":
        db.update_bot_status(status="open")
        
    status = db.select_bot_status()[0]
    
    await call.message.edit_text(f"<b>Сейчас доступк к опросу <i>{text[status]}</i></b>")
    if status == "open":
        await call.message.edit_reply_markup(settings_keyboard_2)
    elif status == "close":
        await call.message.edit_reply_markup(settings_keyboard_1)
    await state.set_state("settings")
    

# --------------- end of "settings" block -----------------
