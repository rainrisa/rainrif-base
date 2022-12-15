from asyncio import sleep

class UserConstruct():
  def __init__(self, name, id):
    self.name = name
    self.id = id

class Tag():
  def __init__(self, app, message, chat_id):
    self.app = app
    self.message = message
    self.chat_id = chat_id
    self.users = []
    self.waiting_list = []
    self.pseudonym = 0
    self.sleep_time = 5
    self.mention_at_a_time = 30
    self.tag_message_ids = []

  async def tag_all_users(self):
    for x in range(len(self.users)):
      self.waiting_list.append(self.users[x])

      if (len(self.waiting_list) >= self.mention_at_a_time):
        await self.send_mention_message()
        self.waiting_list.clear()
        await sleep(self.sleep_time)

    await self.send_mention_message()
    self.waiting_list.clear()

  async def get_all_users(self):
    async for m in self.app.get_chat_members(self.chat_id):
      self.pseudonym += 1
      self.users.append(UserConstruct(self.pseudonym, m.user.id))

  def generate_text_mention(self):
    text_mention = f"#all {self.message}"
    text_mention += "\n\n"

    for x in range(len(self.waiting_list)):
      user_name = self.waiting_list[x].name
      user_id = self.waiting_list[x].id

      text_mention += f"[{user_name}](tg://user?id={user_id})"
      text_mention += " "

    return text_mention

  async def send_mention_message(self):
    m = await self.app.send_message(self.chat_id, self.generate_text_mention())
    self.tag_message_ids.append(m.id)

  async def delete_all_tag_messages(self):
    try: await self.app.delete_messages(self.chat_id, self.tag_message_ids)
    except Exception: pass
