# 📄 ai_translator.py (本地大模型全自动翻译机)
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage
import os

print("🚀 正在启动本地 Qwen 大模型翻译引擎...")

# 1. 唤醒咱们之前配置好的本地大模型 (确保你后台跑着 ollama run qwen3:8b)
llm = ChatOllama(model="qwen3:8b") 

# 2. 给大模型设定极其严格的“人设”
system_prompt = SystemMessage(content="""
你是一个顶级的计算机视觉（CV）算法专家。
请将下面提供的 OpenCV 底层 C++ 英文官方注释，翻译成通俗易懂的中文。
要求：
1. 保持专业术语的准确性（如 kernel 翻译为 卷积核，tensor 翻译为 张量）。
2. 如果英文注释太生硬，请用大白话解释它的实际作用和参数含义。
3. 不要输出多余的废话，直接给出中文翻译。
""")

# 3. 读取咱们刚才生成的超级大字典
input_file = "OpenCV_Ultimate_Dictionary.txt"
output_file = "OpenCV_Ultimate_Dictionary_CN.txt"

if not os.path.exists(input_file):
    print("❌ 找不到英文原版字典！请先运行上一步的提取脚本！")
    exit()

print("📚 正在分块读取并喂给大模型（这可能需要一些时间，请让 M1 风扇转起来！）...")

# ...... 前面的加载大模型代码保持不变 ......

with open(input_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

total_lines = len(lines)
batch_size = 150 # 💥 军师绝招：每次只切 150 行喂给大模型，既不会撑爆内存，又能保证翻译质量！

print(f"📦 字典总计 {total_lines} 行，已开启大厂批处理流水线，每次吞吐 {batch_size} 行！")

# 打开文件准备“追加”写入 (注意这里是 "a" 模式，append)
with open(output_file, "a", encoding="utf-8") as out_f:
    for i in range(0, total_lines, batch_size):
        # 1. 极其精准的切片
        chunk = "".join(lines[i : i + batch_size])
        
        print(f"\n🔄 正在翻译第 {i} 到 {i + batch_size} 行 (进度: {i}/{total_lines})...")
        
        # 2. 组装弹药
        messages = [system_prompt, HumanMessage(content=chunk)]
        
        # 3. 疯狂输出并实时写入硬盘（断电也不怕！）
        for response_chunk in llm.stream(messages):
            print(response_chunk.content, end="", flush=True)
            out_f.write(response_chunk.content)
            
        out_f.write("\n\n") # 每批次翻译完加个空行隔开

print("\n\n🎉 报告老板！十几万字的天书，已经被咱们用工业流水线彻底翻译成中文啦！")