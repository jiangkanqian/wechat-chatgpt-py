import re
from gpt3_tokenizer import GPT3Tokenizer
from config import Config
from openai import ChatCompletionRequestMessage

def regexp_encode(str):
    return re.sub(r'[-/\\^$*+?.()|[\]{}]', r'\\$&', str)

GPT3Tokenizer = importlib.import_module('gpt3_tokenizer').GPT3Tokenizer
tokenizer = GPT3Tokenizer(type='gpt3')

def calTokens(chatMessage):
  count = 0
  for msg in chatMessage:
    count += countTokens(msg.content)
    count += countTokens(msg.role)
  return count + 2

def countTokens(str: string) -> int:
  encoded = tokenizer.encode(str)
  return len(encoded.bpe)

def isTokenOverLimit(chatMessage:ChatCompletionRequestMessage) -> boolean:
  limit = 4096
  if config.model=="gpt-3.5-turbo" or config.model=="gpt-3.5-turbo-0301":
    limit = 4096
  return calTokens(chatMessage) > limit

def isTokenOverLimit(chatMessage:ChatCompletionRequestMessage) -> boolean:
  limit = 4096
  if config.model=="gpt-3.5-turbo" or config.model=="gpt-3.5-turbo-0301":
    limit = 4096
  return calTokens(chatMessage) > limit