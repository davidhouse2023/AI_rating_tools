# LLM_Demos
## 项目结构
webUI.py：入口文件

models.py：模型调用的相关配置

result.json：模型的评估结果，会随着评估次数的增加而累加

## 添加你自己的模型

1. 在webUI的第13行动态添加你的模型名称

`model_name = ["你的模型名称","..."]`

2. 在models.py文件的response函数中，动态加入你的模型调用

## 运行
输入下述命令即可运行：

`streamlit run .\webUI.py`

