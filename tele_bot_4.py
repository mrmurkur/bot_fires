import time
import logging
import asyncio
import bot_config as cfg
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.markdown import text, bold, italic, code, pre
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import re
path_to_file = "C:/Users/Engineer/"
TOKEN = cfg.TOKEN
map_today = cfg.map_today
map_week = cfg.map_week

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot)

async def periodic(sleep_for):
    while True:
        await asyncio.sleep(sleep_for)
        for id in create_set_users():
            await bot.send_message(id, f"{read_last_fires_svodka()}")
            text_message = read_last_fires_text()
            if len(text_message) > 1000:
                for x in range(0, len(text_message), 1000):
                    await bot.send_message(id, text_message[x:x+1000])
            else:
                await bot.send_message(id, text_message)
            # await bot.send_message(id, f"{read_last_fires_text()}")
            await bot.send_message(id, "\n Для дополнительных комманд нажмите /help", reply_markup=inline_kb_full, parse_mode="Markdown")

def create_set_users():
    with open(path_to_file + "users.txt", "r") as joinedFile:
        joinedUsers = set ()
        for line in joinedFile:
            joinedUsers.add(line.strip())
    return joinedUsers 

def check_user(message):
    if not str(message.from_user.id) in create_set_users():
        return False
    else:
        return True

def write_user(message):
    with open(path_to_file + "users.txt", "a") as joinedFile:
        joinedFile.write(str(message.from_user.id) + "\n")

def clear_user(message):
    with open(path_to_file + "users.txt") as f:
        lines = f.readlines()
    pattern = re.compile(re.escape(str(message.from_user.id)))
    with open(path_to_file + "users.txt", 'w') as f:
        for line in lines:
            result = pattern.search(line)
            if result is None:
                f.write(line)
    print("пользователь удален")

def read_last_fires_svodka():
    with open(path_to_file + "last_fires.txt", "r") as last_fires_svodka:
        svodka_last_fires = last_fires_svodka.read()
    return svodka_last_fires

def read_last_fires_text():
    with open(path_to_file + "last_fires_text.txt", "r", encoding='utf-8') as last_fires_text:
        text_last_fires = last_fires_text.read()
    print(len(text_last_fires))
    return text_last_fires

def log(message):
    fileName_log = message.from_user.full_name
    with open(path_to_file + fileName_log + '.log', 'a') as file_log:
        print(datetime.now(), message.text, file = file_log)

# @dp.callback_query_handler(func = lambda c: c.data == "subscribe")
# async def process_callback_subscribe(callback_query: types.CallbackQuery):
#     await bot.answer_callback_query(callback_query.id)
#     if not check_user(callback_query):
#         print("Пользователя нет, записываем")
#         write_user(callback_query)
#         await bot.send_message(callback_query.from_user.id, "Уведомления будут направляться каждые 24 часа.")
#     else:
#         print("Пользователь уже есть")
#         clear_user(callback_query)
#         await bot.send_message(callback_query.from_user.id, "Уведомления отключены.")

@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    msg_help = 'Нажми /start для запуска или /subscribe для включения (отключения) периодических уведомлений'
    await message.reply(msg_help)
    log(message)

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name
    logging.info(f'{user_id} {user_full_name} {time.asctime()}')
    await message.reply(f"Приветствую, {user_full_name}! \n {read_last_fires_svodka()} \n")
    text_message = read_last_fires_text()
    if len(text_message) > 1000:
        for x in range(0, len(text_message), 1000):
            await bot.send_message(user_id, text_message[x:x+1000])
    else:
        await bot.send_message(user_id, text_message)
    # await bot.send_message(user_id, f"{read_last_fires_text()}")
    await bot.send_message(user_id, "\n Для дополнительных комманд нажмите /help", reply_markup=inline_kb_full, parse_mode="Markdown")
    log(message)


@dp.message_handler(content_types=['text'])
async def get_text_messages(message: types.Message):
    user_id = message.from_user.id
    if message.text == "help":
        await message.reply("Нажми /start для запуска")   
    elif message.text == "/subscribe":
        log(message)
        if not check_user(message):
            print("Пользователя нет, записываем")
            write_user(message)
            await bot.send_message(user_id, "Уведомления будут направляться каждые 24 часа.")
        else:
            print("Пользователь уже есть")
            clear_user(message)
            await bot.send_message(user_id, "Уведомления отключены.")

    log(message)


inline_kb_full = InlineKeyboardMarkup(row_width = 2).add(InlineKeyboardButton('Карта за сегодня', url = map_today))
inline_kb_full.add(InlineKeyboardButton('Карта за неделю', url = map_week))
# inline_kb_full.add(InlineKeyboardButton('Подписаться/отписаться', callback_data = "subscribe"))
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(periodic(60*60*24))
    executor.start_polling(dp)
