import sys
import os

if __name__ == "__main__":
    print("🚀 正在啟動英文聽力訓練網頁版...")
    
    # 確保 app.py 存在
    current_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(current_dir, "app.py")
    
    if not os.path.exists(app_path):
        print("❌ 找不到 app.py。請確認 app.py 是否在同一目錄中。")
        sys.exit(1)
        
    try:
        # 導入並啟動 Flask Web 伺服器
        from app import app
        print("🔗 請打開瀏覽器並訪問: http://127.0.0.1:5000")
        app.run(debug=True, host="127.0.0.1", port=5000)
    except ImportError as e:
        print(f"❌ 載入失敗: {e}")
        print("💡 請先安裝必要依賴: pip install Flask edge-tts")
    except Exception as e:
        print(f"❌ 啟動錯誤: {e}")
