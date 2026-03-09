import streamlit as st
import streamlit.components.v1 as components
import requests
import json

st.set_page_config(page_title="游戏发行会议实时协同助手", page_icon="🎙️", layout="wide")

st.title("🎙️ 海外发行会议实时协同助手")
st.markdown("利用浏览器原生 AI 实时转录会议，一键生成包含**核心数据指标 (CPI/LTV/ROI)**与**行动项**的智能纪要。")

# --- 左侧/右侧 布局设计 ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. 🔴 实时会议转录 (WebRTC)")
    st.info("请使用 Chrome/Edge 浏览器，点击允许麦克风权限。中英夹杂的业务词汇会自动识别。")
    
    # 嵌入前端 HTML 和 JS 代码，调用浏览器的实时语音识别
    html_code = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { font-family: sans-serif; margin: 0; padding: 10px; }
            #status { margin-bottom: 10px; font-weight: bold; color: #555; }
            .btn { padding: 8px 15px; margin-right: 10px; border: none; border-radius: 4px; cursor: pointer; color: white; }
            .btn-start { background-color: #ff4b4b; }
            .btn-stop { background-color: #4CAF50; }
            textarea { width: 100%; height: 300px; padding: 10px; box-sizing: border-box; border: 1px solid #ccc; border-radius: 4px; font-size: 14px; line-height: 1.5; }
        </style>
    </head>
    <body>
        <div id="status">等待开始...</div>
        <button class="btn btn-start" onclick="startDictation()">🎤 开始实时转录</button>
        <button class="btn btn-stop" onclick="stopDictation()">⏹️ 结束会议</button>
        <br><br>
        <textarea id="transcript" placeholder="会议实时产生的文字将显示在这里...&#10;结束后，请复制此处的文本，粘贴到右侧进行 AI 总结。"></textarea>

        <script>
            var final_transcript = '';
            var recognition;

            function startDictation() {
                if ('webkitSpeechRecognition' in window) {
                    recognition = new webkitSpeechRecognition();
                    recognition.continuous = true;
                    recognition.interimResults = true;
                    // 设置为中文，如果是纯英文会议可改为 'en-US'
                    recognition.lang = "cmn-Hans-CN"; 
                    
                    recognition.onstart = function() {
                        document.getElementById('status').innerHTML = "🔴 正在聆听中... (实时出字)";
                        document.getElementById('status').style.color = "#ff4b4b";
                    };

                    recognition.onresult = function(e) {
                        var interim_transcript = '';
                        for (var i = e.resultIndex; i < e.results.length; ++i) {
                            if (e.results[i].isFinal) {
                                final_transcript += e.results[i][0].transcript;
                            } else {
                                interim_transcript += e.results[i][0].transcript;
                            }
                        }
                        // 实时更新文本框内容
                        document.getElementById('transcript').value = final_transcript + interim_transcript;
                    };

                    recognition.onerror = function(e) {
                        document.getElementById('status').innerHTML = "❌ 识别出错，请检查麦克风权限。";
                    };
                    
                    recognition.start();
                } else {
                    document.getElementById('status').innerHTML = "⚠️ 你的浏览器不支持原生语音识别，请使用最新版 Chrome。";
                }
            }

            function stopDictation() {
                if(recognition) recognition.stop();
                document.getElementById('status').innerHTML = "✅ 会议结束。请全选复制下方文本。";
                document.getElementById('status').style.color = "#4CAF50";
            }
        </script>
    </body>
    </html>
    """
    # 在 Streamlit 中渲染这块 HTML
    components.html(html_code, height=450)

with col2:
    st.subheader("2. 🧠 AI 智能纪要生成")
    
    # 背景信息输入
    meeting_topic = st.text_input("会议议题", "北美区Roguelike新品双层架构测试复盘")
    meeting_context = st.text_input("业务侧重点", "关注第一层吸量表现及 D30 留存预估")
    
    # 接收来自左侧复制的文本
    meeting_text = st.text_area("粘贴转录文本", height=150, placeholder="请将左侧完成的转录文本粘贴至此...")
    
    if st.button("🚀 生成业务纪要", type="primary"):
        if not meeting_text.strip():
            st.warning("请先在上方粘贴会议转录文本！")
        else:
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
                    
                    # 使用你提供的中转站 API 配置
                    url = "https://api.bltcy.ai/v1/chat/completions"
                    api_key = st.secrets.get("API_KEY", "你的默认API_KEY") 
                    
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
                            {"role": "user", "content": f"会议转写内容：\n{meeting_text}"}
                        ]
                    })
                    
                    response = requests.post(url, headers=headers, data=payload)
                    
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
                    st.error(f"处理出错：{e}")
