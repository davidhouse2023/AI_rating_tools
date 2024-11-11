import streamlit as st
import openai
from typing import Generator



class BaseModel:
    def __init__(self,model_name:str):

        self.model_name = model_name

    def response(self, messages:list)->Generator:
        """
        messages:[{"role": "user", "content": ""},{"role": "assistant", "content": ""}]
        返回值：这里是流式返回，所以返回类型定义为Generator
        """

        # TODO 你想添加任何模型，只需要在这里加上if判断，然后调用你的方法，方法的具体实现在后面加入即可
        if self.model_name == 'gpt':
            return self.http_gpt(messages)

        elif self.model_name == 'qwen2':
            return self.http_qwen2(messages)

    def http_gpt(self, messages:list)->Generator:
        """
        调用对话模型API
        :param messages: 用户输入
        :return: 流式输出
        """
        openai.api_type = ""
        openai.api_version = ""
        openai.api_base = ""
        openai.api_key = ""
        # ① 模型调用
        stream = openai.ChatCompletion.create(
            engine="gpt35-16k-jp",
            messages=messages,
            stream=True

        )
        # ② 初始化对话缓存
        st.session_state['cache_assistant'] = ""
        #  ③ 返回模型调用结果
        for chunk in stream:
            if chunk.choices and chunk.choices[0] and getattr(chunk.choices[0], "delta") and "content" in chunk.choices[0].delta.keys():
                # ④ 将结果加入对话缓存，用以web页面显示对话历史
                st.session_state['cache_assistant'] += chunk.choices[0].delta['content']
                yield chunk.choices[0].delta['content']

    def http_qwen2(self, messages:list)->Generator:
        """
        这里只是简单给出一个例子
        如果你需要把你自己的模型调用放进来，请仿照上述调用gpt给出的四个步骤就可以了
        """
        st.session_state['cache_assistant'] = "思考ing"
        yield "思考ing"
