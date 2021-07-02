from aiogram.dispatcher.middlewares import BaseMiddleware

import logging

from aiogram import types
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware

from data.config import ADMINS
from loader import db


class BigBrother(BaseMiddleware):
    # 1
    async def on_pre_process_update(self, update: types.Update, data: dict):
        logging.info("[----------------------Новый апдейт!----------------------]")
        logging.info("1. Pre Process Update")
        data["middleware_data"] = "Это пройдет до on_post_process_update"
        if update.message:
            user = update.message.from_user.id
        elif update.callback_query:
            user = update.callback_query.from_user.id
        else:
            return

        if db.select_bot_status()[0] == "close" and str(user) not in ADMINS:
            logging.info("CLOSE")
            await update.message.answer("Приём заявок на вечеринку временно приостановлен."
                                        " Будем рады видеть вас на следующих мероприятиях и в"
                                        " нашем комьюнити STUDIO 69!")
            raise CancelHandler()