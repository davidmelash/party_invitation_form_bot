import logging
import re
import time

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardRemove, CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager

from aiogram_dialog.widgets.kbd import Multiselect, Column, Button, Group
from aiogram_dialog.widgets.text import Format, Const
from operator import itemgetter

from keyboards.default import contact_keyboard
from keyboards.inline.buttons import gender_keyboard, gender_callback, accept_keyboard, \
    accept_callback, back, start_button, additional_callback, ask_button, cancel_keyboard
from loader import dp, registry, db, our_sheet
from aiogram.utils.markdown import hlink

from utils.connector import spreadsheet_id_1


class Sub(StatesGroup):
    gender = State()
    text = State()
    planning_to_come = State()
    new_gender = State()


@dp.message_handler(CommandStart(), state="*")
async def bot_start(message: types.Message,  state: FSMContext):
    text = "<b>Анкета для получения инвайта на вечеринку STUDIO 69 </b>🔺\n\n" \
           "Привет! На связи Давид и Влад 🙌\n\n" \
           "Каждый, кто прошел анкетирование, получит доступ к <b>закрытому Telegram-каналу </b>с информацией о ближайшем мероприятии.\n\n" \
           "❗️Мы не гарантируем, что вы сможете попасть на все наши вечеринки.<i> Ведь решение о вашем участии </i>принимаем не только мы, но и постоянные гости <b>STUDIO 69</b>.\n\n" \
           "‼️Как только заявка будет рассмотрена, с вами свяжутся по указанным контактам.<i> Вся указанная вами информация конфиденциальна </i>и не передается третьим лицам."
    try:
        await message.answer(text, reply_markup=start_button)
    except Exception as e:
        logging.info(e)
    
    await state.set_state("start")


@dp.callback_query_handler(additional_callback.filter(status="start"), state="start")
async def ask_first_last_name(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    try:
        await call.message.answer("<b>Ваше имя, фамилия / First, last Name</b>\n"
                             "<i>Только настоящее имя / Only real name</i>", reply_markup=await cancel_keyboard("start"))
    except Exception as e:
        logging.info(e)
    
    await state.set_state("first_last_name")


@dp.message_handler(state="start")
async def ask_first_last_name(message: types.Message):
    try:
        await message.answer("<b>Для начала регистрации нажмите на кнопку 'START'\n"
                             "For starting registration press the button 'START'</b>")
    except Exception as e:
        logging.info(e)


@dp.message_handler(state="first_last_name")
async def ask_date_of_birth(message: types.Message, state: FSMContext):
    f_l_name = message.text
    await state.update_data(first_last_name=f_l_name)

    try:
        telegram_ = f'@{message.from_user.username}'
        await state.update_data(telegram=telegram_)
        await message.answer("<b>Дата рождения / Date of birth</b>\n"
                             "<i>DD/ММ/YYYY</i>", reply_markup=await back("first_last_name"))
    except Exception as e:
        logging.info(e)
    
    await state.set_state("date_of_birth")


@dp.message_handler(regexp=r'^(0?[1-9]|[12][0-9]|3[01])(/|.)(0?[1-9]|1[0-2])(/|.)\d\d\d\d$', state="date_of_birth")
async def ask_gender(message: types.Message, state: FSMContext):
    date = message.text
    await state.update_data(date_of_birth=date)
    
    try:
        await message.answer("<b>Ваш пол / Your gender</b>", reply_markup=gender_keyboard)
    except Exception as e:
        logging.info(e)
    await Sub.gender.set()


@dp.message_handler(state="date_of_birth")
async def ask_date_of_birth(message: types.Message, state: FSMContext):
    try:
        await message.answer("Invalid date. Try again")
    except Exception as e:
        logging.info(e)
    
    await state.set_state("date_of_birth")


async def redirect_to_ask_gender(call: CallbackQuery, button: Button, manager: DialogManager):
    await call.answer(cache_time=40)

    try:
        await call.message.answer("<b>Ваш пол / Your gender</b>", reply_markup=gender_keyboard)
        
    except Exception as e:
        logging.info(e)
    await Sub.gender.set()
    

async def get_data_(call: CallbackQuery, button: Button, manager: DialogManager):
    
    data = multiselect.get_checked(manager)

    manager.proxy.update({"cities": data})
    await call.answer(cache_time=60)

    try:
        await call.message.answer("<b>Как вы о нас узнали? / How did you hear about us?</b>",
                                  reply_markup=await back("check_box"))
    except Exception as e:
        logging.info(e)
    await Sub.planning_to_come.set()



items = [("Да, в Москве / Yes, in Moscow", 1),
         ("Да, в Нью-Йорке / Yes, in New York", 2),
         ("Да, в Берлине / Yes, in Berlin", 3),
         ("Да, в Париже / Yes, in Paris", 4),
         ("Да, в Киеве / Yes, in Kyiv", 5),
         ("Нет / No", 6)]


multiselect = Multiselect(
    Format("✓ {item[0]}"), Format("{item[0]}"),
    "mselect",
    itemgetter(0),
    items,
)
dialog = Dialog(Window(Const("<b>Посещали наши вечеринки в других странах? / </b>"
                             "<i>Have you been to our parties in other countries?</i>"),
                       Group(Column(multiselect), Button(Const("Отправить / Send"), "b1", on_click=get_data_)
                             , Button(Const("Назад / Back"), "b2", on_click=redirect_to_ask_gender)) ,state=Sub.text))

registry.register(dialog)


@dp.callback_query_handler(gender_callback.filter(), state=Sub.gender)
async def ask_about_party(call: types.CallbackQuery, callback_data: dict, state: FSMContext, dialog_manager: DialogManager):

    await call.answer(cache_time=30)
    your_gender__ = callback_data.get("g")

    call.message.message_id = (await call.message.answer("ᅠ")).message_id

    dialog_manager.proxy.update({"your_gender": your_gender__})
    await Sub.text.set()
    await dialog_manager.start(Sub.text, reset_stack=True)


@dp.message_handler(state=Sub.planning_to_come)
async def planning_to_come_func(message: types.Message, state: FSMContext):
    text = message.text
    await state.update_data(how_did_hear=text)
    try:
        await message.answer("<b>С кем планируете прийти? / Who are you planning to come with?\n\n</b>"
                             "<i>Напишите имя этого человека и ссылку на его страницу в"
                             " Instagram "
                             "(она должна быть открытой).</i>", reply_markup=await back("how_did_your_hear"))
    except Exception as e:
        logging.info(e)
    
    await state.set_state("will_you_come")


@dp.message_handler(state="will_you_come")
async def get_phone_number(message: types.Message, state: FSMContext):
    text = message.text
    await state.update_data(planning_to_come=text)
    
    try:
        id = (await message.answer("<b>Ваш номер телефона / Your phone number </b>\n", reply_markup=contact_keyboard)).message_id
        await message.answer("<i>Нажмите на кнопку 'Поделиться'.\n"
                             "Press the button 'Share'</i>",
                             reply_markup=await back("with_who", id))
                             
    except Exception as e:
        logging.info(e)
    await state.set_state("phone_number")


@dp.message_handler(content_types=types.ContentType.CONTACT, state="phone_number")
async def get_accounts(message: types.Message, state: FSMContext):
    
    contact = message.contact.phone_number
    await state.update_data(phone_number=contact)

    try:
        u_id = (await message.answer("<b>Социальные профили / Social profiles </b>\n"
                             "<i>\nСсылка на ваш Instagram либо Facebook (страница должна быть открытой) / "
                             "Link to your Instagram or Facebook (account must be public)</i>\n\n",
                             reply_markup=ReplyKeyboardRemove())).message_id
        await message.answer(
                             "<i>Например: https://instagram.com/studio_69_party или <code>@имя</code>\n"
                             "For example: https://instagram.com/studio_69_party or <code>@name</code></i>",
                             reply_markup=await back("share_number", u_id), disable_web_page_preview=True)

        await state.set_state("rules")
    except Exception as e:
        logging.info(e)

r_facebook = r"(?:(?:http|https):\/\/)?(?:www.)?facebook.com\/(?:(?:\w)*#!\/)?(?:pages\/)?(?:[?\w\-]*\/)?(?:profile.php\?id=(?=\d.*))?([\w\-]*)?"
r_instagram = r"(?:https?:)?\/\/(?:www\.)?(?:instagram\.com|instagr\.am)\/(?P<username>[A-Za-z0-9_](?:(?:[A-Za-z0-9_]|(?:\.(?!\.))){0,28}(?:[A-Za-z0-9_]))?)"


async def link_checker(links) -> bool:
    for li in links:
        if li:
            if not (re.search(r_facebook, li) or (re.search(r_instagram, li) or re.search(r"@\w", li))):
                return False
    return True


@dp.message_handler(state="rules")
async def accept_rules(message: types.Message, state: FSMContext):
    links = message.text
    links = re.split("[ |\n| , ]", links)
    check = await link_checker(links)
    if check:
        await state.update_data(links_to_accounts=links)
        try:
            await message.answer("<b>Соглашение с правилами и обработкой персональных данных. </b>/ "
                                 "<i>The agreement with personal data processing rules.</i>\n\n " +
                                 hlink("Правила/Rules", "studio69.link/правила_обработка_персональных_данных"),
                                 reply_markup=accept_keyboard, disable_web_page_preview=True)
        except Exception as e:
            logging.info(e)
    
        await state.set_state("finish")
    else:
        await message.answer("Invalid link or username. Try again")
        await state.set_state("rules")
    

@dp.callback_query_handler(accept_callback.filter(), state="finish")
async def finish_dialog(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    
    try:
        await call.message.answer("<b>Спасибо за предоставленные ответы </b>❤\n\n️"
                                  "Мы тщательно подбираем участников наших вечеринок, поэтому <i>свяжемся с вами в течение"
                                  " 48 часов,</i> чтобы сообщить информацию об условиях. 😉")
        await call.message.answer('Остались вопросы? Жми "Задать вопрос"\n'
                                  'Still have questions? Click "Ask a question"', reply_markup=ask_button)
    except Exception as e:
        logging.info(e)
        
    data = await state.get_data()
    links = ["first_last_name", "date_of_birth", "your_gender", "cities", "how_did_hear",
             "planning_to_come", "phone_number", "telegram", "links_to_accounts"]
    
    user_id = call.from_user.id
    phone_number = data.get("phone_number")

    data = [data.get(i) if not (type(data.get(i))) is list else " --- ".join(data.get(i)) for i in links]
    data.insert(0, time.strftime("%Y-%m-%d %X"))
    data.insert(0, user_id)
    
    our_sheet.append_values(spreadsheet_id_1, data, "A2")
    
    if not db.select_user(user_id=user_id):
        db.add_user(user_id=user_id, username=call.from_user.username, phone_number=phone_number)
    
    await state.finish()
