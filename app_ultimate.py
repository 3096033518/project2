# 📄 app_ultimate.py
import streamlit as st
import numpy as np
import cv2
import tempfile
from engine_cv import CVToolbox
from engine_yolo import YOLOEngine
from engine_brain import BrainEngine
from engine_auth import AuthEngine # 💥 引入咱们的安全中枢

st.set_page_config(page_title="VLA-Ultimate 工业决策系统", layout="wide", page_icon="👁️")

# --- 0. 全局会话状态初始化 (Session State) ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = ""

auth = AuthEngine() # 启动门禁引擎

# ==========================================
# 🛑 门禁系统：未登录状态下的 UI (防弹自动跳转版)
# ==========================================
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>🔐 VLA-Ultimate 内部系统</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>请先验证您的身份权限</p>", unsafe_allow_html=True)
    
    # 1. 初始化纯净的状态机（不再绑定给任何组件的 key）
    if 'page_mode' not in st.session_state:
        st.session_state.page_mode = "login"

    # 使用纯净的居中分栏
    _, col, _ = st.columns([1, 2, 1])
    
    with col:
        # 2. 💥 用按钮做导航器，彻底避开状态死锁陷阱！
        nav1, nav2 = st.columns(2)
        with nav1:
            if st.button("🔑 身份登录", use_container_width=True):
                st.session_state.page_mode = "login"
                st.rerun()
        with nav2:
            if st.button("📝 新兵注册", use_container_width=True):
                st.session_state.page_mode = "register"
                st.rerun()
                
        st.divider() # 加一条极简分割线，美化 UI
        
        # 3. 登录面板
        if st.session_state.page_mode == "login":
            login_user = st.text_input("账号", key="log_user")
            login_pwd = st.text_input("密码", type="password", key="log_pwd")
            if st.button("🚀 登入系统", use_container_width=True):
                success, msg = auth.login(login_user, login_pwd)
                if success:
                    st.success(msg)
                    st.session_state.logged_in = True
                    st.session_state.current_user = login_user
                    st.rerun() 
                else:
                    st.error(msg)
                    
        # 4. 注册面板
        elif st.session_state.page_mode == "register":
            reg_user = st.text_input("设置新账号", key="reg_user")
            reg_pwd = st.text_input("设置新密码", type="password", key="reg_pwd")
            reg_pwd_confirm = st.text_input("确认密码", type="password", key="reg_pwd_2")
            if st.button("💾 提交注册", use_container_width=True):
                if reg_pwd != reg_pwd_confirm:
                    st.error("两次输入的密码不一致！")
                else:
                    success, msg = auth.register(reg_user, reg_pwd)
                    if success:
                        st.success(msg)
                        # 💥 军师绝杀：现在的修改绝对安全！它会瞬间把页面踢回登录页！
                        st.session_state.page_mode = "login"
                        st.rerun()
                    else:
                        st.error(msg)

# ==========================================
# 🟢 内部系统：已登录状态下的核心 UI (原来的代码全在这)
# ==========================================
else:
    # --- 1. 资源预加载 (Singleton) ---
    @st.cache_resource
    def load_system():
        return CVToolbox(), YOLOEngine(), BrainEngine()

    cv_box, yolo, brain = load_system()

    # --- 2. 侧边栏：控制中心 ---
    with st.sidebar:
        # 显示当前长官名字和退出按钮
        st.success(f"💂‍♂️ 长官：{st.session_state.current_user}")
        if st.button("🚪 安全退出", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.current_user = ""
            st.rerun()
            
        st.divider()
        st.title("🛡️ 算法控制台")
        
        cv_mode = st.selectbox("核心 OpenCV 算子", [
            "原图", "灰度化", "反色", "怀旧风", "高斯模糊", "中值滤波", "双边滤波",
            "Canny边缘", "Sobel算子", "Laplacian算子", "直方图均衡", "CLAHE增强",
            "二值化", "OTSU阈值", "膨胀", "腐蚀", "水平翻转", "垂直翻转"
        ])
        
        p1, p2 = 127, 255
        if cv_mode in ["高斯模糊", "中值滤波", "双边滤波"]:
            p1 = st.slider("核大小/半径", 1, 51, 9, step=2)
        elif cv_mode == "Canny边缘":
            p1 = st.slider("低阈值", 0, 255, 100)
            p2 = st.slider("高阈值", 0, 255, 200)
        elif cv_mode == "二值化":
            p1 = st.slider("分割阈值", 0, 255, 127)
        elif cv_mode in ["膨胀", "腐蚀"]:
            p1 = st.slider("迭代次数", 1, 10, 1)

        st.divider()
        use_yolo = st.toggle("开启 YOLOv8 智能感知", value=True)
        yolo_conf = st.slider("YOLO 置信度", 0.1, 1.0, 0.25)
        
        if st.button("🧹 清空 AI 记忆", use_container_width=True):
            brain.memory.clear()
            st.toast("记忆已重置")

# --- 3. 主界面布局 (图片/视频 双引擎版) ---
    st.header("👁️🧠 多模态视觉决策中台")

    # 💥 军师升级：上传组件现在支持 mp4 视频了！
    uploaded = st.file_uploader("请上传待检测图像 或 视频", type=["jpg", "png", "jpeg", "mp4", "avi", "mov"])

    if uploaded:
        file_ext = uploaded.name.split('.')[-1].lower()
        
        # ==========================================
        # 🟢 分支 A：静态图片处理逻辑 (原汁原味保留)
        # ==========================================
        if file_ext in ['jpg', 'png', 'jpeg']:
            file_bytes = np.asarray(bytearray(uploaded.read()), dtype=np.uint8)
            raw_img = cv2.imdecode(file_bytes, 1)
            processed_img = cv_box.process(raw_img, cv_mode, p1, p2)

            yolo_labels = "未开启"
            display_img = processed_img.copy()
            if use_yolo:
                display_img, labels = yolo.detect(processed_img, conf=yolo_conf)
                yolo_labels = ", ".join(labels) if labels else "无目标"

            c1, c2 = st.columns(2)
            c1.image(cv2.cvtColor(raw_img, cv2.COLOR_BGR2RGB), caption="1. 原始采集信号", use_container_width=True)
            
            if len(display_img.shape) == 2:
                c2.image(display_img, caption=f"2. {cv_mode} + YOLO 感知结果", use_container_width=True)
            else:
                c2.image(cv2.cvtColor(display_img, cv2.COLOR_BGR2RGB), caption=f"2. {cv_mode} + YOLO 感知结果", use_container_width=True)

            st.divider()
            st.subheader("🤖 AI 专家深度分析 (带有记忆感知)")
            user_query = st.chat_input("基于当前视觉场景，下达决策指令...")
            if user_query:
                with st.chat_message("assistant", avatar="🧠"):
                    st.write_stream(brain.think_stream(cv_mode, yolo_labels, user_query))

        # ==========================================
        # 🔴 分支 B：动态视频流处理逻辑 (全新涡轮引擎)
        # ==========================================
        elif file_ext in ['mp4', 'avi', 'mov']:
            st.warning("🎥 视频流已接入！正在通过 M1 Pro 算力进行逐帧渲染...")
            
            # 1. 缓存视频到临时文件（OpenCV 必须通过物理路径读取视频）
            tfile = tempfile.NamedTemporaryFile(delete=False)
            tfile.write(uploaded.read())
            cap = cv2.VideoCapture(tfile.name)
            
            # 2. 网页上的两个“相框”占位符
            c1, c2 = st.columns(2)
            frame_placeholder1 = c1.empty()
            frame_placeholder2 = c2.empty()
            
            # 3. 设置物理刹车
            stop_btn = st.button("⏹️ 强制停止视频监控", type="primary")
            
            yolo_labels_set = set() # 记录视频中出现过的所有物体
            
            # 4. 开启无限抽帧循环！
            while cap.isOpened() and not stop_btn:
                ret, frame = cap.read()
                if not ret:
                    st.success("✅ 视频流监控完毕！")
                    break
                    
                # 💥 军师防卡顿绝招：压缩帧画面，保障 M1 渲染流畅度！
                frame = cv2.resize(frame, (640, 360))
                
                # 扔进咱们的 CV 引擎
                processed_img = cv_box.process(frame, cv_mode, p1, p2)
                display_img = processed_img.copy()
                
                # 扔进 YOLO 引擎
                if use_yolo:
                    display_img, labels = yolo.detect(processed_img, conf=yolo_conf)
                    for lbl in labels: yolo_labels_set.add(lbl) # 收集罪证
                
                # 疯狂刷新网页上的相框
                frame_placeholder1.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), channels="RGB", caption="🟢 实时监控源")
                if len(display_img.shape) == 2:
                    frame_placeholder2.image(display_img, channels="GRAY", caption="🔴 VLA 雷达锁定")
                else:
                    frame_placeholder2.image(cv2.cvtColor(display_img, cv2.COLOR_BGR2RGB), channels="RGB", caption="🔴 VLA 雷达锁定")
            
            cap.release()
            
            # 5. 视频放完后，AI 专家介入进行“战后总结”
            if stop_btn or not ret:
                st.divider()
                st.subheader("🤖 AI 专家视频全案分析")
                summary_labels = ", ".join(list(yolo_labels_set)) if yolo_labels_set else "无任何目标"
                st.info(f"📋 监控汇总：系统在刚刚的视频段内，累计发现了以下目标群体：**{summary_labels}**")
                
                user_query = st.chat_input("基于刚才的视频监控结果，下达决策指令...")
                if user_query:
                    with st.chat_message("assistant", avatar="🧠"):
                        st.write_stream(brain.think_stream(cv_mode, summary_labels, user_query))

    else:
        st.info("👋 长官，请上传一张图片 或 一段 MP4 视频，开启全链路 AI 级联分析。")