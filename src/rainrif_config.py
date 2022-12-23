from pyrogram.types import Message
from functions.get_payload import get_payload

class RainrifConfig():
  def __init__(self):
    self.live_rank = True
    self.enable_rank_sticker = "CAACAgUAAxkBAAELc5Vjnp2MTwmhBQuTvaaL0cR4Z1wNzwAC9AADkUfRVU1JUdBpoWNvLAQ"
    self.disable_rank_sticker = "CAACAgUAAxkBAAELc5djnp5Cz6jGDliHJZGStZs5SZbM_QACVgEAAhYoyVU0QHA1a7IQySwE"
    self.success_sticker = "CAACAgUAAxkBAAELc5Vjnp2MTwmhBQuTvaaL0cR4Z1wNzwAC9AADkUfRVU1JUdBpoWNvLAQ"
    self.fail_sticker = "CAACAgUAAxkBAAELc7ZjnqogdFKM3NxrtQjs1A5K_GuwUwAC6AQAAvB1mFYmM6DD0xMNtCwE"
    self.astaroth_live_title = "Dark Fears"
    self.sudo_users = []

  async def enable_rank(self, message: Message):
    if message.from_user.id in self.sudo_users:
      self.live_rank = True
      await message.reply_sticker(self.enable_rank_sticker)
    else:
      await message.reply_sticker(self.fail_sticker)

  async def disable_rank(self, message: Message):
    if message.from_user.id in self.sudo_users:
      self.live_rank = False
      await message.reply_sticker(self.disable_rank_sticker)
    else:
      await message.reply_sticker(self.fail_sticker)
    
  async def change_title(self, message: Message):
    title = get_payload(message.text)

    if not title: await message.reply_sticker(self.fail_sticker)
    elif message.from_user.id not in self.sudo_users:
      await message.reply_sticker(self.fail_sticker)
    else:
      self.astaroth_live_title = title
      await message.reply_sticker(self.success_sticker)

rainrif_config = RainrifConfig()