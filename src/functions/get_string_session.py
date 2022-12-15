from pyrogram import Client, idle
from dotenv import load_dotenv
from os import getenv
from asyncio import get_event_loop

load_dotenv()

api_id = int(getenv("API_ID"))
api_hash = getenv("API_HASH")
app = Client("rainrif", api_id=api_id, api_hash=api_hash)
loop = get_event_loop()

async def init():
  await app.start()
  me = await app.get_me()
  print(f"App started as {me.first_name}")
  print(await app.export_session_string())
  await idle()

loop.run_until_complete(init())
