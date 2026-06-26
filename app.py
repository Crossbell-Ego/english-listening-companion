import asyncio
import base64
import edge_tts
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# 支援的微軟 Edge 英文語音清單
SUPPORTED_VOICES = {
    "Emma (en-US, 女)": "en-US-EmmaNeural",
    "Ava (en-US, 女)": "en-US-AvaNeural",
    "Andrew (en-US, 男)": "en-US-AndrewNeural",
    "Brian (en-US, 男)": "en-US-BrianNeural",
    "Sonia (en-GB, 女)": "en-GB-SoniaNeural",
    "Ryan (en-GB, 男)": "en-GB-RyanNeural"
}

async def get_tts_data(text, voice, rate):
    """呼叫 edge-tts 並同步收集音訊資料與單字時間戳記"""
    communicate = edge_tts.Communicate(text, voice, rate=rate, boundary="WordBoundary")
    audio_bytes = b""
    words = []
    
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_bytes += chunk["data"]
        elif chunk["type"] == "WordBoundary":
            # offset (時間偏移) 與 duration 單位均是 100ns (Ticks)
            # 轉換為秒數：除以 10,000,000
            start_time = chunk["offset"] / 10000000.0
            duration = chunk["duration"] / 10000000.0
            words.append({
                "text": chunk["text"],
                "start": start_time,
                "end": start_time + duration
            })
            
    return audio_bytes, words

@app.route("/")
def index():
    """首頁路由"""
    return render_template("index.html", voices=SUPPORTED_VOICES)

@app.route("/api/tts")
def tts_api():
    """文字轉語音 API (回傳 Base64 音訊與 Word Boundary 資訊)"""
    text = request.args.get("text", "").strip()
    voice = request.args.get("voice", "en-US-AvaNeural")
    rate = request.args.get("rate", "+0%")

    if not text:
        return jsonify({"error": "請輸入英文文字"}), 400

    try:
        # 使用 asyncio.run 執行非同步 tts 任務
        audio_data, words = asyncio.run(get_tts_data(text, voice, rate))
        
        if not audio_data:
            return jsonify({"error": "生成音訊失敗，請稍後再試"}), 500

        # 將音訊二進位資料轉為 Base64 字串
        audio_base64 = base64.b64encode(audio_data).decode("utf-8")
        audio_url = f"data:audio/mp3;base64,{audio_base64}"

        return jsonify({
            "audio": audio_url,
            "words": words
        })
    except Exception as e:
        return jsonify({"error": f"語音生成出錯: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
