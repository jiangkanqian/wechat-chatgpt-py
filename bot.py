from wechaty import Contact,  Room
from wechaty import Message
from typing import Union
import asyncio
import re
import config
import openai
from data import DBUtils
from openai import chatgpt, dalle, whisper
from utils import regexp_encode
from typing import TypeVar

class MessageType:
    Unknown = 0,
    Attachment = 1
    Audio = 2
    Contact = 3
    ChatHistory = 4
    Emoticon = 5
    Image = 6
    Text = 7
    Location = 8
    MiniProgram = 9
    GroupNote = 10
    Transfer = 11
    RedEnvelope = 12
    Recalled = 13
    Url = 14
    Video = 15
    Post = 16

SINGLE_MESSAGE_MAX_SIZE = 500
Speaker = TypeVar("Speaker", Room, Contact)

class ICommand:
    def __init__(self, name, description, exec_fn):
        self.name = name
        self.description = description
        self.exec_fn = exec_fn

class CommandManager:
    def __init__(self):
        self.commands = []

    def add_command(self, command):
        self.commands.append(command)

    def get_commands(self):
        return self.commands

    async def exec_command(self, talker, command, *args):
        for cmd in self.commands:
            if cmd.name == command:
                await cmd.exec_fn(talker, *args)
                return
        await talker.say("未知命令：{}".format(command))
        await talker.say("输入 /cmd help 查看帮助")

class ChatGPTBot:
    chatPrivateTriggerKeyword = config.chatPrivateTriggerKeyword
    chatTriggerRule = re.compile(config.chatTriggerRule) if config.chatTriggerRule else None
    disableGroupMessage = config.disableGroupMessage or False
    botName = ""
    ready = False

    def setBotName(botName):
      return botName

    def chatGroupTriggerRegEx(botName):
        return re.compile('^@{0}\\s'.format(regexp_encode(botName)))

    def chatPrivateTriggerRule(chatPrivateTriggerKeyword, chatTriggerRule):
        regEx = chatTriggerRule
        if not regEx and chatPrivateTriggerKeyword:
            regEx = re.compile(regexp_encode(chatPrivateTriggerKeyword))
        return regEx
    
    cmdmgr = CommandManager()
    cmdmgr.add_command(
        ICommand(
            "help",
            "显示帮助信息",
            lambda talker: talker.say(
                "========\n"
                "/cmd help\n"
                "# 显示帮助信息\n"
                "/cmd prompt <PROMPT>\n"
                "# 设置当前会话的 prompt \n"
                "/img <PROMPT>\n"
                "# 根据 prompt 生成图片\n"
                "/cmd clear\n"
                "# 清除自上次启动以来的所有会话\n"
                "========",
            ),
        )
    )
    cmdmgr.add_command(
        ICommand(
            "prompt",
            "设置当前会话的prompt",
            lambda talker, prompt: (
                DBUtils.set_prompt(await talker.topic(), prompt)
                if isinstance(talker, Room)
                else DBUtils.set_prompt(talker.name(), prompt)
            ),
        )
    )
    cmdmgr.add_command(
        ICommand(
            "clear",
            "清除自上次启动以来的所有会话",
            lambda talker: (
                DBUtils.clear_history(await talker.topic())
                if isinstance(talker, Room)
                else DBUtils.clear_history(talker.name())
            ),
        )
    )

    async def command(self, contact, rawText: str) -> None:
      commandName, *args = rawText.split()
      command = next((command for command in self.commands if command.name == commandName), None)
      if command:
          await command.exec(contact, " ".join(args))

    def cleanMessage(rawText: str, privateChat: bool = False) -> str:
      text = rawText
      item = rawText.split("- - - - - - - - - - - - - - -")
      if len(item) > 1:
        text = item[len(item) - 1]

      chatTriggerRule = re.compile(r'')
      chatPrivateTriggerRule = re.compile(r'')

      if privateChat and chatPrivateTriggerRule:
        text = re.sub(chatPrivateTriggerRule, "", text)
      elif not privateChat:
        text = re.sub(r'^.*?{}.*?$'.format(ChatGPTBot.chatGroupTriggerRegEx), "", text)
        text = re.sub(chatTriggerRule, "", text)
      # remove more text via - - - - - - - - - - - - - - -
      return text
    
    async def getGPTMessage(talkerName: str, text: str) -> str:
      gptMessage: str = await chatgpt(talkerName, text)
      if gptMessage != "":
          DBUtils.addAssistantMessage(talkerName, gptMessage)
          return gptMessage
      return "Sorry, please try again later. 😔"
    
    def checkChatGPTBlockWords(message: str) -> bool:
      if len(config.chatgptBlockWords) == 0:
        return False
      return any(word in message for word in config.chatgptBlockWords)
    
    async def trySay(talker: (Room | Contact), message: str) -> None:
      messages = []
      if ChatGPTBot.checkChatGPTBlockWords(message):
          print(f'🚫 Blocked ChatGPT: {message}')
          return
      while len(message) > SINGLE_MESSAGE_MAX_SIZE:
          messages.append(message[:SINGLE_MESSAGE_MAX_SIZE])
          message = message[SINGLE_MESSAGE_MAX_SIZE:]
      messages.append(message)
      for msg in messages:
          await talker.say(msg)
    
    def triggerGPTMessage(text, privateChat = False):
      chatGroupTriggerRegEx = re.compile( r'^\[\d{2}:\d{2}\]\s' )
      triggered = False
      if privateChat:
          regEx = ChatGPTBot.chatPrivateTriggerRule
          triggered = regEx.search(text) if regEx else True
      else:
          triggered = chatGroupTriggerRegEx.search(text)
          # group message support `chatTriggerRule`
          if triggered and ChatGPTBot.chatTriggerRule:
              triggered = ChatGPTBot.chatTriggerRule.search(text.replace(chatGroupTriggerRegEx, ""))
      if triggered:
          print(f"🎯 Triggered ChatGPT: {text}")
      return triggered
    
    def checkBlockWords(message: str) -> bool:
      if len(config.blockWords) == 0:
          return False
      return any(word in message for word in config.blockWords)
    
    def is_nonsense(self, talker: Contact, messageType: MessageType, text: str) -> bool:
        if talker.is_self():
            return True
        if not (messageType == MessageType.Text or messageType == MessageType.Audio):
            return True
        if talker.name() == "微信团队":
            return True
        if text.find("收到一条视频/语音聊天消息，请在手机上查看"):
            return True
        if text.find("收到红包，请在手机上查看"):
            return True
        if text.find("收到转账，请在手机上查看"):
            return True
        if text.find("/cgi-bin/mmwebwx-bin/webwxgetpubliclinkimg"):
            return True
        if self.checkBlockWords(text):
            return True
        return False
    
    async def onPrivateMessage(self, talker: Contact, text: str):
      gptMessage = await self.getGPTMessage(talker.name(), text)
      await self.trySay(talker, gptMessage)
    
    async def onGroupMessage(self, contact, room, content):
      gptMessage = await self.getGPTMessage(await room.topic(), content);
      result = f"@{contact.name()} {content}\n\n------\n {gptMessage}"
      await self.trySay(room, result);
    
    async def on_message(self, message: Message):
      talker = message.talker()
      raw_text = message.text()
      room = message.room()
      message_type = message.type()
      private_chat = not room
      if private_chat:
          print(f'🤵 Contact: {talker.name()} 💬 Text: {raw_text}')
      else:
          topic = await room.topic()
          print(f'🚪 Room: {topic} 🤵 Contact: {talker.name()} 💬 Text: {raw_text}')
      if self.is_nonsense(talker, message_type, raw_text):
          return
      if message_type == MessageType.Audio:
          # 保存语音文件
          file_box = await message.to_file_box()
          file_name = "./public/" + file_box.name
          await file_box.to_file(file_name, True).catch(lambda e: print("保存语音失败", e))
          # Whisper
          whisper("", file_name).then(lambda text: message.say(text))
          return
      if raw_text.startswith("/cmd "):
          print(f'🤖 Command: {raw_text}')
          cmd_content = raw_text[5:]  # 「/cmd 」一共5个字符(注意空格)
          if private_chat:
              await self.command(talker, cmd_content)
          else:
              await self.command(room, cmd_content)
          return
      # 使用DallE生成图片
      if raw_text.startswith("/img"):
          print(f'🤖 Image: {raw_text}')
          img_content = raw_text[4:]
          if private_chat:
              url = await dalle(talker.name(), img_content)
          else:
              url = await dalle(await room.topic(), img_content)
          file_box = FileBox.from_url(url)
          await message.say(file_box)
          return
      if self.trigger_gpt_message(raw_text, private_chat):
          text = self.clean_message(raw_text, private_chat)
          if private_chat:
              return await self.on_private_message(talker, text)
          else:
              if self.disable_group_message:
                  return
              else:
                  return await self.on_group_message(talker, text, room)
      else:
          return
