import openai
import os
import json
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

configuration = openai.Configuration(
    api_key=config.openai_api_key,
    api_version=config.api,
)
openai = openai.OpenAIApi(configuration)

async def chatgpt(username: str, message: str) -> str:
    # 先将用户输入的消息添加到数据库中
    DBUtils.addUserMessage(username, message)
    messages = DBUtils.getChatMessage(username)
    response = await openai.createChatCompletion(
        model="gpt-3.5-turbo", messages=messages, temperature=config.temperature
    )
    assistantMessage = ""
    try:
        if response.status == 200:
            assistantMessage = response.data.choices[0].message.content.replace(
                r"^\n+|\n+$", ""
            )
        else:
            print(
                f"Something went wrong,Code: {response.status}, {response.statusText}"
            )
    except Exception as e:
        if hasattr(e, "request"):
            print("请求出错")
    return assistantMessage

async def dalle(username, prompt):
    try:
        response = await openai.create_image(
            prompt=prompt,
            n=1,
            size=CreateImageSize._256x256,
            response_format=CreateImageResponseFormat.Url,
            user=username
        )
        if response:
            return response.data[0].url
        else:
            return "Generate image failed"
    except Exception as e:
        return e

async def whisper(username, video_path):
    file = open(video_path, "rb")
    response = await openai.create_transcription(file, "whisper-1")
    if response:
        return response.text
    else:
        return "Speech to text failed"


__all__ = [chatgpt,dalle,whisper];