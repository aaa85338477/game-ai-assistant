import streamlit as st
import requests
import json

st.set_page_config(page_title="游戏发行会议 AI 协同助手", page_icon="🎙️", layout="wide")

st.title("🎙️ 海外发行会议 AI 协同助手 (Whisper Pro版)")
st.markdown("集成 OpenAI Whisper 语音大模型与 LLM，精准识别**游戏发行黑话 (CPI/LTV/ROI)**，一键沉淀会议纪要。")

# --- 侧边栏 API Key 与 业务背景配置 ---
with st.sidebar:
    st.header("🔑 授权与设置")
    user_api_key = st.text_input("请输入中转站 API Key", type="password", help="需支持 whisper-1 和 gpt-4o-mini 模型调用")
    
    st.markdown("---")
    st.header("📋 业务背景设置")
    meeting_topic = st.text_input("会议议题", "北美区Roguelike新品双层架构测试复盘")
    meeting_context = st.text_input("业务侧重点", "关注第一层吸量表现及 D30 留存预估")

# --- 左右布局设计 ---
col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("1. 🎧 会议音频输入")
    st.info("Whisper 大模型支持极高精度的中英夹杂识别，请提供会议音频。")
    
    # 提供两种输入方式：麦克风录音 或 文件上传
    input_method = st.radio("选择输入方式", ["🎤 现场麦克风录制", "📁 上传会议录音文件"])
    
    audio_bytes = None
    
    if input_method == "🎤 现场麦克风录制":
        # 使用 Streamlit 原生录音组件
        audio_data = st.audio_input("点击麦克风开始录音 (说两句包含 CPI/LTV 的黑话试试)")
        if audio_data:
            audio_bytes = audio_data.getvalue()
            st.success("录音已捕获！")
            
    else:
        uploaded_file = st.file_uploader("上传录音 (支持 mp3, wav, m4a)", type=['mp3', 'wav', 'm4a'])
        if uploaded_file:
            audio_bytes = uploaded_file.getvalue()
            st.audio(audio_bytes, format="audio/wav")

with col2:
    st.subheader("2. 🧠 AI 高精度解析与纪要")
    
    if st.button("🚀 开始 AI 智能处理", type="primary", use_container_width=True):
        if not audio_bytes:
            st.warning("⚠️ 请先在左侧录制或上传会议音频！")
            st.stop()
            
        if not user_api_key:
            st.warning("⚠️ 请先在左侧侧边栏输入您的 API Key！")
            st.stop()

        # ---------------------------------------------------------
        # 阶段一：调用 Whisper 模型进行高精度语音转文本
        # ---------------------------------------------------------
        with st.status("正在执行多模态 AI 任务...", expanded=True) as status:
            try:
                st.write("⏳ 正在通过 Whisper 模型提取语音特征...")
                
                # 中转站的 Whisper API 端点 (通常与官方一致)
                whisper_url = "https://api.bltcy.ai/v1/audio/transcriptions"
                
                # 发送文件时，不需要手动设置 Content-Type，requests 会自动处理 boundary
                whisper_headers = {
                    'Authorization': f'Bearer {user_api_key}'
                }
                
                # 包装音频文件用于 POST 上传
                files = {
                    'file': ('audio.wav', audio_bytes, 'audio/wav')
                }
                data = {
                    'model': 'whisper-1'
                }
                
                whisper_response = requests.post(whisper_url, headers=whisper_headers, files=files, data=data)
                
                if whisper_response.status_code == 200:
                    transcript_text = whisper_response.json().get('text', '')
                    st.write("✅ Whisper 语音转录完成！")
                    
                    # 在界面上展示一下极高精度的转录结果，惊艳面试官
                    with st.expander("👀 查看 Whisper 原始转写文本", expanded=False):
                        st.info(transcript_text)
                else:
                    st.error(f"Whisper API 请求失败，状态码：{whisper_response.status_code}")
                    st.code(whisper_response.text)
                    st.stop()
                    
                # ---------------------------------------------------------
                # 阶段二：调用 LLM 模型生成业务纪要
                # ---------------------------------------------------------
                st.write("⏳ 正在结合游戏发行业务逻辑生成结构化纪要...")
                
                system_prompt = f"""
                你是一个资深的海外游戏发行制作人兼会议助理。请根据以下极高精度的会议转写记录，生成结构化的会议纪要。
                当前会议议题：{meeting_topic}
                业务背景提示：{meeting_context}
                
                请严格按照以下格式输出：
                1. 📊 **核心数据盘点**：提取会议中提到的所有关键指标（如 CPI, ROI, LTV, 留存等）。
                2. 📝 **核心结论**：提炼会议讨论的最终共识。
                3. 🎯 **行动项 (Action Items)**：严格按照 [负责人] | [任务描述] | [时间节点] 的格式列出。
                """
                
                llm_url = "https://api.bltcy.ai/v1/chat/completions"
                llm_headers = {
                    'Accept': 'application/json',
                    'Authorization': f'Bearer {user_api_key}', 
                    'Content-Type': 'application/json'
                }
                
                llm_payload = json.dumps({
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"会议转写内容：\n{transcript_text}"}
                    ]
                })
                
                llm_response = requests.post(llm_url, headers=llm_headers, data=llm_payload.encode('utf-8'))
                
                if llm_response.status_code == 200:
                    final_summary = llm_response.json()['choices'][0]['message']['content']
                    st.write("✅ 智能纪要生成完毕！")
                    status.update(label="🎉 AI 处理全流程完成！", state="complete", expanded=False)
                else:
                    st.error(f"LLM API 请求失败，状态码：{llm_response.status_code}")
                    st.code(llm_response.text)
                    st.stop()

            except Exception as e:
                status.update(label="❌ 处理出错", state="error")
                st.error(f"错误详情：{e}")
                st.stop()
        
        # 在外部干净地展示最终结果
        st.markdown("### 📑 最终业务纪要")
        st.markdown(final_summary)
