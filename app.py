import streamlit as st
from openai import OpenAI
import os

# 1. 初始化客户端 (这里以通用 OpenAI 接口为例，你可以换成 DeepSeek 等)
# 在 Streamlit Cloud 上，我们会通过 Secrets 来配置环境变量，避免密钥泄露
client = OpenAI(
    api_key=st.secrets.get("API_KEY", "your-local-key-here"), 
    base_url=st.secrets.get("BASE_URL", "https://api.openai.com/v1") 
)

st.set_page_config(page_title="游戏发行 AI 会议纪要助手", page_icon="🎮")

st.title("🎮 海外发行会议协同助手")
st.markdown("上传会议录音，自动生成带**业务数据**与**行动项追踪**的结构化纪要。")

# 2. 侧边栏：会议背景信息输入
with st.sidebar:
    st.header("📋 会议前置信息")
    meeting_topic = st.text_input("会议议题", "例如：Q3北美区买量ROI复盘及新版本留存优化")
    meeting_context = st.text_area("业务背景提示", "例如：重点关注 LTV、CPI 数据，以及针对 D30 留存的双层架构优化方案。")

# 3. 主界面：音频上传
audio_file = st.file_uploader("上传会议录音 (支持 mp3, m4a, wav)", type=['mp3', 'm4a', 'wav'])

if audio_file is not None and st.button("🚀 开始生成纪要"):
    with st.spinner("正在进行语音识别与行业黑话解析..."):
        try:
            # --- 阶段 1: ASR 语音转文字 ---
            # 真实场景中这里调用 Whisper API
            # transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
            # speech_text = transcript.text
            
            # 为了你本地测试不耗费额度，这里做个假想的识别结果
            speech_text = """
            大家好，今天过一下北美区上周的数据。目前的 CPI 大概在 2.5 刀，但是由于我们留存层的优化还没上，
            导致现在的 D7 只有 12%，ROI 很难回正，预估 LTV 跑不平。
            程序那边，老李，你需要在周三前把之前说的那个 Roguelike 核心战斗的手感优化合入主干。
            运营这边，小张，周五前产出一份针对土耳其市场的本地化买量素材需求。
            """
            
            st.success("语音识别完成！")
            with st.expander("查看原始转写文本"):
                st.write(speech_text)
                
            # --- 阶段 2: LLM 结构化提炼 ---
            st.info("正在生成结构化业务纪要...")
            
            system_prompt = f"""
            你是一个资深的海外游戏发行制作人兼会议助理。请根据以下会议转写记录，生成结构化的会议纪要。
            当前会议议题：{meeting_topic}
            业务背景提示：{meeting_context}
            
            请严格按照以下格式输出：
            1. 📊 **核心数据盘点**：提取会议中提到的所有关键指标（如 CPI, ROI, LTV, 留存等）。
            2. 📝 **核心结论**：提炼会议讨论的最终共识。
            3. 🎯 **行动项 (Action Items)**：严格按照 [负责人] | [任务描述] | [时间节点] 的格式列出。
            """
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo", # 如果用 DeepSeek，可以换成 deepseek-chat
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"会议转写内容：\n{speech_text}"}
                ]
            )
            
            # --- 阶段 3: 结果展示 ---
            st.markdown("### 📑 会议纪要与行动项")
            st.markdown(response.choices[0].message.content)
            
        except Exception as e:
            st.error(f"处理出错：{e}")
