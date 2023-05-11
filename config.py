from typing import TypedDict
import os

class IConfig(TypedDict):
  api: str
  openai_api_key: str
  model: str
  chatPrivateTriggerKeyword: str
  chatTriggerRule: str
  disableGroupMessage: bool
  temperature: float
  blockWords: list[str]
  chatgptBlockWords: list[str]

config: IConfig = {
  "api": os.getenv("API"),
  "openai_api_key": os.getenv("OPENAI_API_KEY") or "123456789",
  "model": os.getenv("MODEL") or "gpt-3.5-turbo",
  "chatPrivateTriggerKeyword": os.getenv("CHAT_PRIVATE_TRIGGER_KEYWORD") or "",
  "chatTriggerRule": os.getenv("CHAT_TRIGGER_RULE") or "",
  "disableGroupMessage": os.getenv("DISABLE_GROUP_MESSAGE") == "true",
  "temperature": float(os.getenv("TEMPERATURE")) if os.getenv("TEMPERATURE") else 0.6,
  "blockWords": os.getenv("BLOCK_WORDS").split(",") if os.getenv("BLOCK_WORDS") else [],
  "chatgptBlockWords": os.getenv("CHATGPT_BLOCK_WORDS").split(",") if os.getenv("CHATGPT_BLOCK_WORDS") else [],
}