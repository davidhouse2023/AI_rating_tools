import json
import random
import logging

import streamlit as st
from models import BaseModel
from functools import partial
logging.basicConfig(filename="app.log", filemode="a", level=logging.INFO)

save_file="./result.json"

# TODO 模型池
model_name = ["gpt", "qwen2"]

show=False


def page_base_setting():
    """
    设置页面样式的一些基本配置
    包括logo、标题、按钮等
    """
    img = './LOGO.png'

    # 设置侧边栏
    with st.sidebar:
        st.image(
            img,  # 图片路径或URL
            width=300  # 调整图片宽度，单位为像素
        )
        # st.title("AI Rating")

    # 设置主界面标题
    st.title("Come and rate the anonymous model you think is good😄")
    # 设置按钮样式
    st.markdown("""
                    <style>
                    .stButton > button {
                        width: 100%;  /* 设置按钮宽度为100% */
                    }
                    .footer {
                        position: fixed;
                        left: 0;
                        bottom: 0;
                        width: 100%;
                        background-color: white;
                        padding: 10px 0;
                    }
                    </style>
                    """, unsafe_allow_html=True)
    # 设置左右对话框样式
    st.markdown("""
                 <style>
                 .left-column {
                     height: 400px;  /* 设置左侧列的高度 */
                     border: 1px solid #e0e0e0;
                 }
                 .right-column {
                     height: 400px;  /* 设置右侧列的高度 */
                     border: 1px solid #e0e0e0;
                 }
                 </style>
                 """, unsafe_allow_html=True)

def process_answer(prompt,left,right):
    """
    处理模型的输入，并展示对话框
    :param prompt: 模型的输入
    :param left: 左边对话框
    :param right: 右边对话框
    :return:
    """
    # 匿名模型1
    with left:
        st.session_state.dialog1.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar='🧐'):
            st.write(prompt)
        with st.chat_message("assistant", avatar='🤖'):
            st.write_stream(st.session_state.model_A.response(st.session_state.dialog1))
        st.session_state.dialog1.append({"role": "assistant", "content": st.session_state['cache_assistant']})
        if show:
            st.write(st.session_state.model_A.model_name)
    # 匿名模型2
    with right:
        st.session_state.dialog2.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar='🧐'):
            st.write(prompt)
        with st.chat_message("assistant", avatar='🤖'):
            st.write_stream(st.session_state.model_B.response(st.session_state.dialog2))
        st.session_state.dialog2.append({"role": "assistant", "content": st.session_state['cache_assistant']})
        if show:
            st.write(st.session_state.model_B.model_name)
    # 记录用户打分结果
    record_scores()

def click_button(model_name, result):
    """
    model_name: 模型名称
    result: 打分结果
    """
    with open(save_file, "r", encoding='utf-8') as file:
        content = file.read()
    if content:
        stat_data=json.load(open(save_file,"r"))
    else:
        stat_data={}
    if "total_number" not in stat_data:
        stat_data["total_number"] = 0

    stat_data["total_number"] += 1

    if len(model_name) > 0 and model_name not in stat_data:
        stat_data[model_name]={
            "win_number":0,
            "win_rate":0
        }
    if result == "good":
        stat_data[model_name]["win_number"] += 1
        stat_data[model_name]["win_rate"] = round(stat_data[model_name]["win_number"] / stat_data["total_number"],2)

    with open(save_file, 'w') as f:
        json.dump(stat_data, f, indent=4)


def record_scores():
    """
    用户通过点击事件实现为偏好模型打分
    :return:
    """
    # 为按钮绑定的点击事件
    # 将点击结构写到log文件中

    footer = st.empty()  # 创建一个占位符
    with footer.container():  # 在占位符中创建容器
        # 设置三个按钮，一排水平显示
        col1, col2, col3 = st.columns(3)
        with col1:
            st.button('A is better 👈', on_click=partial(click_button, model_name=st.session_state.model_A.model_name, result="good"))

        with col2:
            st.button('B is better 👉', on_click=partial(click_button, model_name=st.session_state.model_B.model_name, result="good"))

        with col3:
            st.button('Tie 🤝', on_click=partial(click_button, model_name="", result="tie"))
    show = True


def print_history(left,right):
    """
    打印对话历史
    :param left: 左边对话框
    :param right: 右边对话框
    :return:
    """
    with left:
        for dialog in st.session_state.dialog1:
            if dialog["role"] == "user":
                st.chat_message(dialog["role"], avatar='🧐').write(dialog["content"])
            else:
                st.chat_message(dialog["role"], avatar='🤖').write(dialog["content"])

    with right:
        for dialog in st.session_state.dialog2:
            if dialog["role"] == "user":
                st.chat_message(dialog["role"], avatar='🧐').write(dialog["content"])
            else:
                st.chat_message(dialog["role"], avatar='🤖').write(dialog["content"])

# 主函数
def main():

    # 配置页面基础样式
    page_base_setting()

    # 创建页面布局
    col1, col2 = st.columns([1,1],gap='small')

    # 第一个对话窗口
    with col1:
        st.write("匿名模型 A 🐱‍👤")
        left = col1.container(height=500,border=True)

    # 第二个对话窗口
    with col2:
        st.write("匿名模型 B 🐱‍👤")
        right = col2.container(height=500, border=True)

    # 从列表中随机取两个模型，这样设计方便后面有多个模型时可以随机抽样
    random_model = random.sample(model_name, 2)
    model_A = BaseModel(random_model[0])
    model_B = BaseModel(random_model[1])

    # 因为每次按钮操作都会触发所有脚本执行一遍，所以这里需要将选择的模型保存到对话中
    if "model_A" not in st.session_state:
        st.session_state["model_A"] = model_A
    if "model_B" not in st.session_state:
        st.session_state["model_B"] = model_B

    # 初始化不同的会话状态
    if 'dialog1' not in st.session_state:
        st.session_state['dialog1'] = []

    if 'dialog2' not in st.session_state:
        st.session_state['dialog2'] = []

    if 'btn_Regeneration' not in st.session_state:
        st.session_state.btn_Regeneration = False

    # 侧边栏设置
    with st.sidebar:
        # 新一轮对话按钮
        btn_NewRound=st.button("New Round", type="primary")
        # 重新生成对话按钮
        btn_Regeneration=st.button("Regeneration", type="primary")

        if btn_NewRound:
            st.session_state['dialog1'] = []
            st.session_state['dialog2'] = []

        if btn_Regeneration:
            st.session_state.btn_Regeneration = True

    # 用户输入
    prompt = st.chat_input()

    # 当点击重新生成对话按钮时，重新生成当前对话内容
    if st.session_state.btn_Regeneration and len(st.session_state['dialog1'])>0:
        # 取最后一条用户输入
        prompt= st.session_state['dialog1'][-2]["content"]
        # 去掉最后一条对话，以便模型重新生成
        st.session_state['dialog1'] = st.session_state['dialog1'][:-2]
        st.session_state['dialog2'] = st.session_state['dialog2'][:-2]
        st.session_state.btn_Regeneration=False

    # 打印历史内容
    print_history(left, right)

    # 请求并生成对话
    if prompt:
        process_answer(prompt,left,right)


if __name__ == '__main__':
    main()
