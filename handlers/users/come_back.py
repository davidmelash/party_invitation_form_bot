import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram_dialog import DialogManager

from handlers.users.main import Sub
from keyboards.default import contact_keyboard
from keyboards.inline.buttons import user_back_callback, back, additional_callback, start_button, \
    cancel_keyboard
from loader import dp, bot


@dp.callback_query_handler(additional_callback.filter(status="cancel_start"), state="first_last_name")
async def come_back_to_start(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)

    await call.message.edit_reply_markup()
    text = "<b>Анкета для получения инвайта на вечеринку STUDIO 69 </b>🔺\n\n" \
           "Привет! На связи Давид и Влад 🙌\n\n" \
           "Каждый, кто прошел анкетирование, получит доступ к <b>закрытому Telegram-каналу </b>с информацией о ближайшем мероприятии.\n\n" \
           "❗️Мы не гарантируем, что вы сможете попасть на все наши вечеринки.<i> Ведь решение о вашем участии </i>принимаем не только мы, но и постоянные гости <b>STUDIO 69</b>.\n\n" \
           "‼️Как только заявка будет рассмотрена, с вами свяжутся по указанным контактам.<i> Вся указанная вами информация конфиденциальна </i>и не передается третьим лицам."
    try:
        await call.message.edit_text(text, reply_markup=start_button)
    except Exception as e:
        logging.info(e)
    
    await state.set_state("start")


@dp.callback_query_handler(user_back_callback.filter(), state="*")
async def come_back(call: types.CallbackQuery, state: FSMContext, callback_data: dict, dialog_manager: DialogManager):
    status = callback_data.get("status")
    await call.answer(cache_time=60)
    user_state = await state.get_state()
    m_id = callback_data.get("m_id")
    
    if status == "first_last_name" and user_state == "date_of_birth":
        await call.message.edit_reply_markup()
        await call.message.edit_text("<b>Ваше имя, фамилия / First, last Name</b>\n"
                                  "<i>Только настоящее имя / Only real name</i>", reply_markup=await cancel_keyboard("start"))
        await state.set_state("first_last_name")
    
    elif status == "date_of_birth" and user_state == "Sub:gender":
        await call.answer(cache_time=30)
        await call.message.edit_text("<b>Дата рождения / Date of birth</b>\n<i>ММ/DD/YYYY</i>",
                                  reply_markup=await back("first_last_name"))
        
        await state.set_state("date_of_birth")
    
    elif status == "check_box" and user_state == "Sub:planning_to_come":
        await Sub.text.set()
        await dialog_manager.start(Sub.text, reset_stack=True)

    elif status == "how_did_your_hear" and user_state == "will_you_come":
        try:
            await call.message.edit_text("<b>Как вы о нас узнали? / How did you hear about us?</b>",
                                      reply_markup=await back("check_box"))
            await Sub.planning_to_come.set()
        except Exception as e:
            logging.info(e)
        
    elif status == "with_who" and user_state == "phone_number":
        try:
            await bot.delete_message(chat_id=call.message.chat.id, message_id=m_id)
            await call.message.edit_text("<b>С кем планируете прийти? / Who are you planning to come with?\n\n</b>"
                                      "<i>Напишите, с кем вы хотите прийти, и оставьте ссылку на страницу в"
                                      " Instagram этого человека.\n"
                                      "(страница должна быть открытой).</i>", reply_markup=await back("how_did_your_hear"))
            await state.set_state("will_you_come")
        except Exception as e:
            logging.info(f"{e}")

    elif status == "share_number" and user_state == "rules":
        try:

            await bot.delete_message(chat_id=call.message.chat.id, message_id=m_id)
            await call.message.delete()
            id = (await call.message.answer(
                                              text="<b>Ваш номер телефона / Your phone number </b>\n",
                                              reply_markup=contact_keyboard)).message_id
            
            await call.message.answer("<i>Нажмите на кнопку 'Поделиться'.\n"
                                 "Press the button 'Share'</i>",
                                 reply_markup=await back("with_who", id))
    
            await state.set_state("phone_number")
        except Exception as e:
            logging.info(e)

    elif status == "social_links" and user_state == "finish":
        try:
            u_id = (await call.message.edit_text("<b>Социальные профили / Social profiles </b>\n"
                                 "<i>\nСсылка на ваш Instagram либо Facebook (страница должна быть открытой) / "
                                 "Link to your Instagram or Facebook (account must be public)</i>\n\n")).message_id
            await call.message.answer(
                                 "<i>Например: https://instagram.com/studio_69_party или <code>@имя</code>\n"
                                 "For example: https://instagram.com/studio_69_party or <code>@name</code></i>",
                                      reply_markup=await back("share_number", u_id), disable_web_page_preview=True)
            
            await state.set_state("rules")
        except Exception as e:
            logging.info(e)