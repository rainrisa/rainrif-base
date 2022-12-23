from typing import Dict
from datetime import datetime, timedelta
from pyrogram import Client
from pyrogram.types import Message
from pyrogram.enums import MessageEntityType
from functions.get_inner_text import get_inner_text
from rainrif_config import rainrif_config
import re

class Player():
  def __init__(self, name, id):
    self.name = name
    self.id = id
    self.total_bulls = 0
    self.afk = False

class AstarothGame():
  def __init__(self, app: Client, live_channel_id, discussion_id, chat_id):
    self.app = app
    self.played_numbers = []
    self.unplayed_numbers = []
    self.live_channel_id = live_channel_id
    self.live_message_id = None
    self.discussion_id = discussion_id
    self.discussion_message_id = None
    self.init_numbers_played = False
    self.players: Dict[int, Player] = {}
    self.live_rank_message_id = None
    self.round = 1
    self.chat_id = chat_id
    self.display_chat_id = True

  def get_rank(self):
    return sorted(self.players, key = lambda id: self.players[id].total_bulls)

  def set_players(self, message: Message):
    entities = message.entities

    for entity in entities:
      if entity.type == MessageEntityType.TEXT_MENTION:
        player = Player(entity.user.first_name, entity.user.id)
        self.players[player.id] = player
    
    return

  def update_total_bulls(self, message: Message):
    numbers = re.findall(r'\d+', message.text)
    number_of_bulls = int(numbers[-1]) or 0
    entity = message.entities[0]

    if entity.type == MessageEntityType.TEXT_LINK or entity.type == MessageEntityType.BOLD:
      message_text = message.text
      user_name = get_inner_text(message_text, entity)

      for player_id in self.players:
        if self.players[player_id].name == user_name:
          self.players[player_id].total_bulls += number_of_bulls

    return

  def update_init_numbers(self, numbers):
    next_number_index = 1

    while True: 
      try:
        self.played_numbers.append(int(
          numbers[next_number_index]))
        next_number_index += 3
      except Exception: break

    for i in range(len(self.played_numbers)):
      self.unplayed_numbers[int(self.played_numbers[i]) - 1] = "-"

  def update_numbers(self, numbers):
    for i in range(len(numbers)):
      self.played_numbers.append(int(numbers[i]))
      self.unplayed_numbers[int(numbers[i]) - 1] = "-"

  def update_round(self, number):
    self.round = number

  async def send_live_rank_message(self):
    if self.live_rank_message_id:
      if rainrif_config.live_rank: 
        try: await self.app.edit_message_text(
          self.discussion_id, 
          self.live_rank_message_id,
          self.get_live_rank_text())
        except: pass
      else:
        await self.app.delete_messages(self.discussion_id, self.live_rank_message_id)
        self.live_rank_message_id = None
    else:
      if not rainrif_config.live_rank: return

      m = await self.app.send_message(
        chat_id = self.discussion_id, 
        text = self.get_live_rank_text(), 
        reply_to_message_id = self.discussion_message_id)

      self.live_rank_message_id = m.id

  async def send_live_message(self):
    m = await self.app.send_message(self.live_channel_id, self.get_live_text())
    self.live_message_id = m.id

  async def update_live_message(self, finish = False):
    if finish:
      await self.app.edit_message_text(
        self.live_channel_id,
        self.live_message_id,
        "Permainan berakhir!")
    else:
      await self.app.edit_message_text(
        self.live_channel_id,
        self.live_message_id,
        self.get_live_text())

  async def delete_live_message(self):
    await self.app.delete_messages(
      self.live_channel_id,
      self.live_message_id)

  def get_live_rank_text(self):
    rank_ids = self.get_rank()
    text = f"**{rainrif_config.astaroth_live_title} Podium Sementara**\n"
    next_rank = 1
    last_player_bulls = 0
    text += f"\n**{next_rank}.** "
    row_count = 0

    for player_id in rank_ids:
      player = self.players[player_id]
      done = False

      while not done:
        if player.total_bulls != last_player_bulls:
          past_player_bulls = last_player_bulls
          last_player_bulls = player.total_bulls

          if row_count:
            text += f"**{past_player_bulls} sapi**\n"
            next_rank += 1
            text += f"\n**{next_rank}.** "
            text += f"`{player.name}` | "
            row_count = 1
            done = True
        else:
          text += f"`{player.name}` | "
          row_count += 1
          done = True

    text += f"**{last_player_bulls} sapi**"

    return text

  def get_live_text(self):
    self.played_numbers.sort()
    date_now = datetime.utcnow() + timedelta(hours=7)  # GMT7 Timezone
    date_after_format = date_now.strftime("%H:%M")
    text = f"**{rainrif_config.astaroth_live_title}**"
    if self.display_chat_id: text += f" `{self.chat_id}`"
    text += "\n\n"
    text += f"**Round {self.round}** | **List Kartu Yang Tersisa:**\n\n"
    text += "`"
    text += " ".join(map(str, self.unplayed_numbers))
    text += "`"
    text += "\n\n"
    text += f"**Jumlah Pemain:** `{len(self.players)}` | **Update:** `{date_after_format}`"

    return text
