class IConfig:
    def __init__(self, api, openai_api_key, model, chatTriggerRule, disableGroupMessage, temperature, blockWords, chatgptBlockWords, chatPrivateTriggerKeyword):
        self.api = api
        self.openai_api_key = openai_api_key
        self.model = model
        self.chatTriggerRule = chatTriggerRule
        self.disableGroupMessage = disableGroupMessage
        self.temperature = temperature
        self.blockWords = blockWords
        self.chatgptBlockWords = chatgptBlockWords
        self.chatPrivateTriggerKeyword = chatPrivateTriggerKeyword

class User:
    def __init__(self, username, chatMessage):
        self.username = username
        self.chatMessage = chatMessage