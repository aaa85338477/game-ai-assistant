import streamlit as st
import streamlit.components.v1 as components
import requests
import json

st.set_page_config(page_title="游戏发行会议实时协同助手", page_icon="🎙️", layout="wide")

st.title("🎙️ 海外发行会议实时协同助手")
st.markdown("利用浏览器原生 AI 实时转录会议，一键生成包含**核心数据指标 (CPI/LTV/ROI)**与**行动项**的智能纪要。")

# --- 新增：侧边栏 API Key 配置 ---
with st.sidebar:
    st.header("🔑 授权与设置")
    # type="password" 会将输入的字符显示为圆点，保护隐私
    user_api_key = st.text_input("请输入中转站 API Key", type="password", help="Key 仅在当前网页会话中有效，刷新即销毁，不会被存储。")
    st.markdown("---")
    st.header("📋 业务背景设置")
    meeting_topic = st.text_input("会议议题", "北美区Roguelike新品双层架构测试复盘")
    meeting_context = st.text_input("业务侧重点", "关注第一层吸量表现及 D30 留存预估")

# --- 左侧/右侧 布局设计 ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. 🔴 实时会议转录 (WebRTC)")
    st.info("请使用 Chrome/Edge 浏览器，点击允许麦克风权限。中英夹杂的业务词汇会自动识别。")
    
    # ... （这里保留之前那段完整的 HTML/JS 浏览器录音代码，不做改动） ...
    # components.html(html_code, height=450)

with col2:
    st.subheader("2. 🧠 AI 智能纪要生成")
    meeting_text = st.text_area("粘贴转录文本", height=150, placeholder="请将左侧完成的转录文本粘贴至此...")
    
    if st.button("🚀 生成业务纪要", type="primary"):
        # 拦截 1：检查是否输入了文本
        if not meeting_text.strip():
            st.warning("⚠️ 请先在上方粘贴会议转录文本！")
            st.stop() # 停止向下执行
            
        # 拦截 2：检查是否输入了 API Key
        if not user_api_key:
            st.warning("⚠️ 请先在左侧侧边栏输入您的 API Key！")
            st.stop() # 停止向下执行

        with st.spinner("正在解析业务黑话并生成结构化纪要..."):
            try:
                system_prompt = f"""
                你是一个资深的海外游戏发行制作人兼会议助理。请根据以下会议转写记录，生成结构化的会议纪要。
                当前会议议题：{meeting_topic}
                业务背景提示：{meeting_context}
                
                请严格按照以下格式输出：
                1. 📊 **核心数据盘点**：提取会议中提到的所有关键指标（如 CPI, ROI, LTV, 留存等）。
                2. 📝 **核心结论**：提炼会议讨论的最终共识。
                3. 🎯 **行动项 (Action Items)**：严格按照 [负责人] | [任务描述] | [时间节点] 的格式列出。
                """
                
                url = "https://api.bltcy.ai/v1/chat/completions"
                
                # 将原来的硬编码或 secrets 获取，替换为用户输入的 Key
                headers = {
                    'Accept': 'application/json',
                    'Authorization': f'Bearer {user_api_key}', 
                    'User-Agent': 'DMXAPI/1.0.0',
                    'Content-Type': 'application/json'
                }
                
                payload = json.dumps({
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"会议转写内容：\n{meeting_text}"}
                    ]
                })
                
                # 加入 .encode('utf-8') 防止请求头和数据体中的中文报错
                response = requests.post(url, headers=headers, data=payload.encode('utf-8'))
                
                if response.status_code == 200:
                    response_data = response.json()
                    final_summary = response_data['choices'][0]['message']['content']
                    
                    st.success("✅ 纪要生成完毕！")
                    st.markdown("---")
                    st.markdown(final_summary)
                else:
                    st.error(f"API 请求失败，状态码：{response.status_code}")
                    st.code(response.text)
                    
            except Exception as e:
                st.error(f"网络或处理出错：{e}")
