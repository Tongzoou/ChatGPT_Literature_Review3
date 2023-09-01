# Author:Tongzou
# QQ:90000303
# CreatTime:2023/7/1
# FilesNmae:ChatGPT_conversation
"""
只能使用我给的转发key
"""
# coding:utf-8
import openai
import os
class ChatGPT_conversation_3:
    def __init__(self,API_KEY,PROMPT_LIST,REQUEST_PORT):
        self.API_KEY = API_KEY#API_KEY
        self.PROMPT_LIST= PROMPT_LIST#请求对话
        self.REQUEST_PORT = REQUEST_PORT#端口
    def creat_conversation(self,gpt_version):
        try:
            openai.api_base = self.REQUEST_PORT
            openai.api_key = self.API_KEY
            completion = openai.ChatCompletion.create(
                model=gpt_version,
                messages=self.PROMPT_LIST
            )

            chat_response = completion
            # 答案
            answer = chat_response.choices[0].message.content
            # token消耗数据
            usage = chat_response.usage
            #回复请求的模型是
            model=chat_response.model
            print(model)
            # 保持上下文联想
            self.PROMPT_LIST.append({"role": "assistant", "content": answer})
            # 返回接收答案数据、更新后的对话数据、token消耗数据
            return answer, self.PROMPT_LIST, usage, model, None
        except Exception as e:
            print(str(e))
            return None, None, None, None, str(e)

