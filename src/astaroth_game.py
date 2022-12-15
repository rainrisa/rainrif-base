from datetime import datetime, timedelta

class AstarothGame():
  def __init__(self, app, played_numbers, unplayed_numbers, live_chat_id):
    self.app = app
    self.played_numbers = played_numbers
    self.unplayed_numbers = unplayed_numbers
    self.live_chat_id = live_chat_id
    self.live_message_id = None
    self.init_numbers_played = False

  def update_init_numbers(self, numbers):
    next_number_index = 1

    while True: 
      try:
        self.played_numbers.append(int(
          numbers[next_number_index]))
        next_number_index += 3
      except Exception: break

    for i in range(len(self.played_numbers)):
      self.unplayed_numbers[int(self.played_numbers[i]) - 1] = "_"

  def update_numbers(self, numbers):
    for i in range(len(numbers)):
      self.played_numbers.append(int(numbers[i]))
      self.unplayed_numbers[int(numbers[i]) - 1] = "_"

  async def send_live_message(self):
    m = await self.app.send_message(self.live_chat_id, self.get_live_text())
    self.live_message_id = m.id

  async def update_live_message(self):
     await self.app.edit_message_text(self.live_chat_id,
                                  self.live_message_id,
                                  self.get_live_text())

  async def delete_live_message(self):
    await self.app.delete_messages(self.live_chat_id,
                                self.live_message_id)

  def get_live_text(self):
    self.played_numbers.sort()
    date_now = datetime.utcnow() + timedelta(hours=7)  # GMT7 Timezone
    date_after_format = date_now.strftime("%d-%m-%Y %H:%M:%S")
    text = "🤡 Dark Fearst Live 🤡\n\n"
    text += "List Angka Yang Tersisa\n\n"
    text += ", ".join(map(str, self.unplayed_numbers)) or "-"
    text += "\n\n"
    text += f"Last Updated: {date_after_format}"

    return text
