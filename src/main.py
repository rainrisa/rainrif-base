from typing import Dict
from pyrogram import Client, filters, idle
from pyrogram.types import Message
from pyrogram.enums import ChatType
from dotenv import load_dotenv
from asyncio import get_event_loop
from os import getenv
from astaroth_game import AstarothGame
from tag import Tag
from functions.get_payload import get_payload
from rainrif_config import rainrif_config
import re

load_dotenv()

api_id = int(getenv("API_ID"))
api_hash = getenv("API_HASH")
string_session = getenv("USER_STRING_SESSION")
bot_token = getenv("BOT_TOKEN")
user_account = Client("rainrif_user", api_id=api_id, api_hash=api_hash, session_string=string_session)
bot_account = Client("rainrif_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)
loop = get_event_loop()
astaroth_id = 2075925757
live_channel_id = int(getenv("LIVE_CHANNEL_ID"))
discussion_id = int(getenv("DISCUSSION_ID"))
astaroth_game: Dict[int, AstarothGame] = {}
tags: Dict[int, Tag] = {}
rainrif_config.sudo_users = list(map(int, getenv('SUDO_USERS').split()))

@user_account.on_message(filters.command(["all", "tag"], ["."]))
async def tag_handler(_, message: Message):
  chat_id = message.chat.id

  try:
    if message.from_user.is_bot: return
  except: pass
  try: await user_account.delete_messages(message.chat.id, message.id)
  except: pass
  if chat_id in tags: del tags[chat_id]

  tag_message = get_payload(message.text)
  tags[chat_id] = Tag(user_account, tag_message, chat_id)
  await tags[chat_id].get_all_users()
  await tags[chat_id].tag_all_users()

@user_account.on_message(filters.command("q", [".", "/", "#"]))
async def delete_mention_handler(_, message):
  chat_id = message.chat.id

  if chat_id in tags:
    tags[chat_id].cancel = True
    await user_account.delete_messages(chat_id, message.id)
    await tags[chat_id].delete_all_tag_messages()
    del tags[chat_id]

@user_account.on_message(filters.text & filters.bot)
async def regular_message_handler(_, message: Message):
  chat_id = message.chat.id
  user_id = message.from_user.id

  if user_id == astaroth_id:
    if message.text.find("Permainan dimulai!") != -1:
      astaroth_game[chat_id] = AstarothGame(bot_account, live_channel_id, discussion_id, chat_id)
      numbers = re.findall(r'\d+', message.text)
      min_number = int(numbers[0])
      max_number = int(numbers[1])
      unplayed_numbers = list(range(min_number, max_number + 1))

      astaroth_game[chat_id].unplayed_numbers = unplayed_numbers
      await astaroth_game[chat_id].send_live_message()

    elif chat_id not in astaroth_game: return

    elif message.text.find("[Ronde 1]") != -1:
      astaroth_game[chat_id].set_players(message)
      await astaroth_game[chat_id].update_live_message()

    elif message.text.find("[Ronde") != -1:
      number = re.findall(r'\d+', message.text)[0]
      astaroth_game[chat_id].update_round(number)
      await astaroth_game[chat_id].update_live_message()

    elif message.text.find("menyimpan row") != -1:
      astaroth_game[chat_id].update_total_bulls(message)
      await astaroth_game[chat_id].send_live_rank_message()

    elif message.text.find("Kartu ini adalah kartu ke-6") != -1:
      astaroth_game[chat_id].update_total_bulls(message)
      await astaroth_game[chat_id].send_live_rank_message()

    elif message.text.find("+-+-+-+-") != -1:
      if astaroth_game[chat_id].init_numbers_played: return

      astaroth_game[chat_id].init_numbers_played = True
      numbers = re.findall(r'\d+', message.text)
      astaroth_game[chat_id].update_init_numbers(numbers)
      await astaroth_game[chat_id].update_live_message()

    elif message.text.find("Ini adalah kartu yang dimainkan") != -1:
      numbers = re.findall(r'\d+', message.text)
      astaroth_game[chat_id].update_numbers(numbers)
      await astaroth_game[chat_id].update_live_message()
      
    elif message.text.find("Semua kartu telah digunakan!") != -1:
      await astaroth_game[chat_id].update_live_message(finish = True)

    elif message.text.find("Permainan berakhir!") != -1:
      await astaroth_game[chat_id].delete_live_message()
      del astaroth_game[chat_id]

    return

@bot_account.on_message(filters.private & filters.command("enablerank"))
async def enable_rank_handler(_, message: Message):
  await rainrif_config.enable_rank(message)

@bot_account.on_message(filters.private & filters.command("disablerank"))
async def enable_rank_handler(_, message: Message):
  await rainrif_config.disable_rank(message)

@bot_account.on_message(filters.private & filters.command("changetitle"))
async def enable_rank_handler(_, message: Message):
  await rainrif_config.change_title(message)

@bot_account.on_message(filters.group & filters.text)
async def bot_regular_message_handler(_, message: Message):
  if message.chat.id == discussion_id and message.sender_chat:
    if message.sender_chat.type == ChatType.CHANNEL:
      if message.text.find(rainrif_config.astaroth_live_title) != -1:
        chat_id = int(re.findall(r'-\d+', message.text)[0])
        astaroth_game[chat_id].discussion_message_id = message.id
        astaroth_game[chat_id].display_chat_id = False

  return

async def init():
  await user_account.start()
  user = await user_account.get_me()
  await bot_account.start()
  bot = await bot_account.get_me()
  print(f"App started as {user.first_name}")
  print(f"App started as {bot.username}")
  await idle()

loop.run_until_complete(init())
