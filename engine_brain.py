# 📄 engine_brain.py (彻底抛弃 langchain 主包的终极版)
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# 伪装层：为了完美兼容 app_ultimate.py 里的 brain.memory.clear() 按钮
class MockMemory:
    def __init__(self, parent_engine):
        self.parent = parent_engine
        
    def clear(self):
        self.parent.memory_history = [] # 一键清空历史列表

class BrainEngine:
    def __init__(self, model_name="qwen3:8b"): # 请确保本地 ollama run qwen3:8b 已启动
        # 1. 初始化本地大模型引擎
        self.llm = ChatOllama(model=model_name, streaming=True)
        
        # 2. 抛弃脆弱的第三方记忆库，咱们用最硬核的 List 手工接管最高记忆权限！
        self.memory_history = []
        self.memory = MockMemory(self) # 挂载伪装层
        
        # 3. 设定系统最高指令 (System Prompt)
        self.system_prompt = SystemMessage(content="""你是一位拥有多模态视觉感知能力的安防决策专家。
        你可以通过 YOLO 视觉雷达看到画面，并结合之前的对话记忆进行思考。
        请用简洁、专业的中文给出决策建议。""")

    def think_stream(self, cv_method, yolo_labels, user_query):
        """整合视觉与文本信息，生成流式响应给前端打字机"""
        context = f"""
        [系统状态] 当前使用了 {cv_method} 算法处理图像。
        [视觉结果] YOLO 雷达检测到以下目标: {yolo_labels}。
        [用户指令] {user_query}
        """
        
        # A. 组装本次对话的完整记忆链条 (系统人设 + 历史记忆 + 本次输入)
        messages = [self.system_prompt] + self.memory_history + [HumanMessage(content=context)]
        
        # B. 流式请求大模型，并实时吐给网页前端
        ai_response_text = ""
        for chunk in self.llm.stream(messages):
            text = chunk.content
            ai_response_text += text
            yield text
            
        # C. 极其硬核的记忆更新（将本轮对话永远刻入记忆）
        self.memory_history.append(HumanMessage(content=user_query))
        self.memory_history.append(AIMessage(content=ai_response_text))
        
        # D. 记忆滑动窗口保护：防止聊得太多撑爆 M1 的内存（永远只保留最近的 6 轮对话）
        if len(self.memory_history) > 12: 
            self.memory_history = self.memory_history[-12:]