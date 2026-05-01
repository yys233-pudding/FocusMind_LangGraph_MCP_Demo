import cv2
import threading
import time
import sqlite3
import os
import win32gui
from collections import Counter
from deepface import DeepFace

class RealTimeMonitor:
    def __init__(self, db_path="data/usage_stats.db"):
        self.db_path = db_path
        self._init_db()
        self.current_app = "桌面"
        self.start_time = time.time()
        self.running = True
        
        self.emotions_buffer = []      
        self.stable_emotion = "neutral" 
        self.last_vote_time = time.time()
        
        threading.Thread(target=self._window_listener, daemon=True).start()
        threading.Thread(target=self._emotion_capture_loop, daemon=True).start()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.execute('''CREATE TABLE IF NOT EXISTS usage (date TEXT, app TEXT, duration REAL)''')
        conn.commit()
        conn.close()

    def _window_listener(self):
        while self.running:
            try:
                hwnd = win32gui.GetForegroundWindow()
                app_name = win32gui.GetWindowText(hwnd)
                if app_name and app_name != self.current_app:
                    duration = time.time() - self.start_time
                    self._save_usage(self.current_app, duration)
                    self.current_app = app_name
                    self.start_time = time.time()
            except: pass
            time.sleep(1)

    def _emotion_capture_loop(self):
        cap = cv2.VideoCapture(0)
        while self.running:
            ret, frame = cap.read()
            if ret:
                try:
                    # 使用 DeepFace 识别[cite: 4]
                    result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
                    raw_emotion = result[0]['dominant_emotion']
                    self.emotions_buffer.append(raw_emotion) 
                except: pass
            
            # 5秒结算一次[cite: 4]
            now = time.time()
            if now - self.last_vote_time >= 5:
                if self.emotions_buffer:
                    most_common = Counter(self.emotions_buffer).most_common(1)[0][0]
                    self.stable_emotion = most_common
                    self.emotions_buffer = [] 
                self.last_vote_time = now
            time.sleep(0.5)
        cap.release()

    def _save_usage(self, app, duration):
        date = time.strftime("%Y-%m-%d")
        conn = sqlite3.connect(self.db_path)
        conn.execute("INSERT INTO usage VALUES (?, ?, ?)", (date, app, duration))
        conn.commit()
        conn.close()

    def get_today_total(self, app_name):
        date = time.strftime("%Y-%m-%d")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("SELECT SUM(duration) FROM usage WHERE date=? AND app=?", (date, app_name))
        row = cursor.fetchone()
        stored = row[0] if row[0] else 0
        conn.close()
        return stored + (time.time() - self.start_time)

    def get_fused_state(self):
        # 统一 key 名为 today_usage_seconds[cite: 4]
        return {
            "emotion": self.stable_emotion,
            "current_app": self.current_app,
            "today_usage_seconds": int(self.get_today_total(self.current_app)),
            "timestamp": time.strftime("%H:%M:%S")
        }

    def stop(self):
        self.running = False