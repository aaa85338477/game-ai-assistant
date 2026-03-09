# ---------------------------------------------------------
                # 阶段一：调用 Whisper 模型进行高精度语音转文本
                # ---------------------------------------------------------
                st.write("⏳ 正在通过 Whisper 模型提取语音特征...")
                
                whisper_url = "https://api.bltcy.ai/v1/audio/transcriptions"
                whisper_headers = {'Authorization': f'Bearer {user_api_key}'}
                files = {'file': ('audio.wav', audio_bytes, 'audio/wav')}
                
                # 💡 核心改动 1：增加 response_format 参数
                data = {
                    'model': 'whisper-1',
                    'response_format': 'verbose_json'  # 魔法指令：要求返回带时间戳的分段数据
                }
                
                whisper_response = requests.post(whisper_url, headers=whisper_headers, files=files, data=data)
                
                if whisper_response.status_code == 200:
                    response_data = whisper_response.json()
                    
                    # 依然提取出一段完整的纯文本，留给后面的 LLM 做总结用
                    transcript_text = response_data.get('text', '') 
                    
                    # 💡 核心改动 2：解析时间戳分段，拼接成优美的对话记录格式
                    segments = response_data.get('segments', [])
                    display_text = ""
                    
                    if segments: # 如果接口成功返回了分段
                        for seg in segments:
                            # 将秒数转换为分:秒 (mm:ss) 的格式
                            start_m, start_s = divmod(int(seg['start']), 60)
                            end_m, end_s = divmod(int(seg['end']), 60)
                            time_stamp = f"[{start_m:02d}:{start_s:02d} - {end_m:02d}:{end_s:02d}]"
                            
                            # 拼接格式：加粗时间戳 + 具体文本 + 双换行
                            display_text += f"**{time_stamp}** {seg['text']}\n\n"
                    else:
                        # 降级保底：如果中转站不支持详细模式，就按空格和句号强行换行
                        display_text = transcript_text.replace(" ", "\n\n").replace("。", "。\n\n")
                        
                    st.write("✅ Whisper 语音转录完成！")
                    
                    # 在界面上展示精美的带时间戳记录，并默认展开 (expanded=True)
                    with st.expander("👀 查看结构化原始转写记录", expanded=True):
                        st.markdown(display_text)
                else:
                    st.error(f"Whisper API 请求失败，状态码：{whisper_response.status_code}")
                    st.code(whisper_response.text)
                    st.stop()
