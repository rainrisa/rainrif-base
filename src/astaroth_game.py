from typing import Dict
from datetime import datetime, timedelta
from pyrogram import Client
from pyrogram.types import Message
from pyrogram.enums import MessageEntityType
from functions.get_inner_text import get_inner_text
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
    self.last_live_rank_message_id = None
    self.round = 1
    self.chat_id = chat_id

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
    if self.last_live_rank_message_id:
      await self.app.delete_messages(self.discussion_id, self.last_live_rank_message_id)
    
    m = await self.app.send_message(
      chat_id = self.discussion_id, 
      text = self.get_live_rank_text(), 
      reply_to_message_id = self.discussion_message_id)
    
    self.last_live_rank_message_id = m.id

  async def send_live_message(self):
    m = await self.app.send_message(self.live_channel_id, self.get_live_text())
    self.live_message_id = m.id

  async def update_live_message(self):
     await self.app.edit_message_text(self.live_channel_id,
                                  self.live_message_id,
                                  self.get_live_text())

  async def delete_live_message(self):
    await self.app.delete_messages(self.live_channel_id,
                                self.live_message_id)

  def get_live_rank_text(self):
    rank_ids = self.get_rank()
    total_players = len(self.players)
    total_pro = 0
    total_nub = 0
    text = "**Dark Fearst Podium Sementara**\n"
    
    if total_players > 10:
      total_pro = 5
      total_nub = 5
    else:
      total_pro = int(total_players / 2)
      total_nub = total_players - total_pro
    
    pro_rank = rank_ids[:total_pro]
    nub_rank = rank_ids[-total_nub:]
    pro_number = 0
    nub_number = total_players - total_nub

    text += "\nPro\n"

    for player_id in pro_rank:
      pro_number += 1
      player = self.players[player_id]
      text += f"\n**{pro_number}.** `{player.name}` | `{player.total_bulls} sapi`\n"

    text += "\n"
    text += "\nTidak Pro\n"

    for player_id in nub_rank:
      nub_number += 1
      player = self.players[player_id]
      if player.total_bulls == 0: continue
      text += f"\n**{nub_number}.** `{player.name}` | `{player.total_bulls} sapi`\n"

    return text

  def get_live_text(self):
    self.played_numbers.sort()
    date_now = datetime.utcnow() + timedelta(hours=7)  # GMT7 Timezone
    date_after_format = date_now.strftime("%H:%M")
    text = f"**Dark Fearst Live** `{self.chat_id}`\n\n"
    text += f"**Round {self.round}** | **List Kartu Yang Tersisa:**\n\n"
    text += "`"
    text += " ".join(map(str, self.unplayed_numbers))
    text += "`"
    text += "\n\n"
    text += f"**Jumlah Pemain:** `{len(self.players)}` | **Update:** `{date_after_format}`"

    return text
