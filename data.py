import json
from typing import List, Optional
from pydantic import BaseModel
from enum import Enum


class ChatCompletionRequestMessageRoleEnum(str, Enum):
    User = "User"
    Assistant = "Assistant"
    System = "System"


class ChatCompletionRequestMessage(BaseModel):
    role: ChatCompletionRequestMessageRoleEnum
    content: str


class User(BaseModel):
    username: str
    chatMessage: List[ChatCompletionRequestMessage]


def isTokenOverLimit(user: User) -> bool:
    return False


class DB:
    data: List[User] = []

    def addUser(self, username: str) -> User:
        existUser = self.getUserByUsername(username)
        if existUser:
            return existUser
        newUser = User(username=username, chatMessage=[
            ChatCompletionRequestMessage(role=ChatCompletionRequestMessageRoleEnum.System,
                                         content="You are a helpful assistant.")
        ])
        self.data.append(newUser)
        return newUser

    def getUserByUsername(self, username: str) -> Optional[User]:
        for user in self.data:
            if user.username == username:
                return user
        return None

    def getChatMessage(self, username: str) -> List[ChatCompletionRequestMessage]:
        return self.getUserByUsername(username).chatMessage

    def setPrompt(self, username: str, prompt: str) -> None:
        user = self.getUserByUsername(username)
        if user:
            for msg in user.chatMessage:
                if msg.role == ChatCompletionRequestMessageRoleEnum.System:
                    msg.content = prompt

    def addUserMessage(self, username: str, message: str) -> None:
        user = self.getUserByUsername(username)
        if user:
            while isTokenOverLimit(user):
                user.chatMessage.pop(1)
            user.chatMessage.append(
                ChatCompletionRequestMessage(role=ChatCompletionRequestMessageRoleEnum.User, content=message))

    def addAssistantMessage(self, username: str, message: str) -> None:
        user = self.getUserByUsername(username)
        if user:
            while isTokenOverLimit(user):
                user.chatMessage.pop(1)
            user.chatMessage.append(
                ChatCompletionRequestMessage(role=ChatCompletionRequestMessageRoleEnum.Assistant, content=message))

    def clearHistory(username):
        user = getUserByUsername(username)
        if user:
            user.chatMessage = [
                {
                    "role": ChatCompletionRequestMessageRoleEnum.System,
                    "content": "You are a helpful assistant."
                }
            ]
 
    def getAllData():
        return DB.data
 
DBUtils = DB()