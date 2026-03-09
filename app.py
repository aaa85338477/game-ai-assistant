import streamlit as st
import requests
import json

st.set_page_config(page_title="游戏发行 AI 会议纪要助手", page_icon="🎮")

st.title("🎮 海外发行会议协同助手")
st.markdown("上传会议录音，自动生成带**业务数据**与**行动项追踪**的结构化纪要。")

# 侧边栏：会议背景信息输入
with st.sidebar:
    st.header("📋 会议前置信息")
    meeting_topic = st.text_input("会议议题", "例如：Q3北美区买量ROI复盘及新版本留存优化")
    meeting_context = st.text_area("业务背景提示", "例如：重点关注 LTV、CPI 数据，以及针对 D30 留存的双层架构优化方案。")

# 主界面：音频上传 (目前前端UI展示，后续可接入真实音频处理)
audio_file = st.file_uploader("上传会议录音 (支持 mp3, m4a, wav)", type=['mp3', 'm4a', 'wav'])

if audio_file is not None and st.button("🚀 开始生成纪要"):
    with st.spinner("正在进行语音识别与行业黑话解析..."):
        try:
            # --- 阶段 1: ASR 语音转文字 ---
            # (这里依然用业务测试文本替代，方便你直接跑通流程，不浪费 API 额度)
            speech_text = """
            大家好，今天过一下北美区上周的数据。目前的 CPI 大概在 2.5 刀，但是由于我们留存层的优化还没上，
            导致现在的 D7 只有 12%，ROI 很难回正，预估 LTV 跑不平。
            程序那边，老李，你需要在周三前把之前说的那个 Roguelike 核心战斗的手感优化合入主干。
            运营这边，小张，周五前产出一份针对土耳其市场的本地化买量素材需求。
            """
            
            st.success("语音识别完成！")
            with st.expander("查看原始转写文本"):
                st.write(speech_text)
                
            # --- 阶段 2: 调用中转 API 进行结构化提炼 ---
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
            
            # API 配置
            url = "https://api.bltcy.ai/v1/chat/completions"
            # 最佳实践：通过 st.secrets 获取密钥，避免明文硬编码在代码中
            api_key = st.secrets.get("API_KEY", "你的默认API_KEY_可以在这里临时硬编码测试") 
            
            headers = {
                'Accept': 'application/json',
                'Authorization': f'Bearer {api_key}', 
                'User-Agent': 'DMXAPI/1.0.0',
                'Content-Type': 'application/json'
            }
            
            payload = json.dumps({
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"会议转写内容：\n{speech_text}"}
                ]
            })
            
            # 发送 POST 请求
            response = requests.post(url, headers=headers, data=payload)
            
            # --- 阶段 3: 解析响应与结果展示 ---
            if response.status_code == 200:
                response_data = response.json()
                # 提取模型回复的文本内容
                final_summary = response_data['choices'][0]['message']['content']
                
                st.markdown("### 📑 会议纪要与行动项")
                st.markdown(final_summary)
            else:
                # 错误处理：如果请求失败，打印状态码和错误信息方便排查
                st.error(f"API 请求失败，状态码：{response.status_code}")
                st.code(response.text)
            
        except Exception as e:
            st.error(f"处理出错：{e}")
