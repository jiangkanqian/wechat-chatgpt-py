from wechaty import Wechaty
from wechaty_puppet import MessageType
from wechaty_puppet import get_logger
from chatGPTBot import ChatGPTBot
from config import config
logger = get_logger('ChatGPTBot')
bot = Wechaty()
chatGPTBot = ChatGPTBot()

bot = WechatyBuilder.build(
    name="wechat-assistant", # generate xxxx.memory-card.json and save login data for the next login
    puppet="wechaty-puppet-wechat",
    puppet_options={
        "uos": True
    }
)

async def main():
    initializedAt = Date.now()
    bot.on("scan", lambda qrcode, status: asyncio.ensure_future(qrcode_handler(qrcode, status)))
    bot.on("login", lambda user: asyncio.ensure_future(login_handler(user)))
    bot.on("message", lambda message: asyncio.ensure_future(message_handler(message)))
    try:
        await bot.start()
    except Exception as e:
        print(f"⚠️ Bot start failed, can you log in through wechat on the web?: {e}")
