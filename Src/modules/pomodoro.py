"""
ポモドーロタイマー機能
"""
import time
import threading
from typing import Callable, Optional
from datetime import datetime, timedelta


class PomodoroTimer:
    """ポモドーロタイマークラス"""
    
    def __init__(self, work_duration: int = 25, short_break: int = 5, long_break: int = 15):
        """
        Args:
            work_duration (int): 作業時間（分）
            short_break (int): 短い休憩時間（分）
            long_break (int): 長い休憩時間（分）
        """
        self.work_duration = work_duration * 60  # 秒に変換
        self.short_break = short_break * 60
        self.long_break = long_break * 60
        
        self.is_running = False
        self.is_paused = False
        self.current_session = "work"  # "work", "short_break", "long_break"
        self.session_count = 0
        self.remaining_time = self.work_duration
        self.timer_thread = None
        
        # コールバック関数
        self.on_tick: Optional[Callable[[int], None]] = None
        self.on_session_complete: Optional[Callable[[str], None]] = None
        self.on_timer_complete: Optional[Callable[[], None]] = None
    
    def start(self):
        """タイマーを開始"""
        if not self.is_running:
            self.is_running = True
            self.is_paused = False
            self.timer_thread = threading.Thread(target=self._run_timer)
            self.timer_thread.daemon = True
            self.timer_thread.start()
    
    def pause(self):
        """タイマーを一時停止"""
        self.is_paused = True
    
    def resume(self):
        """タイマーを再開"""
        self.is_paused = False
    
    def stop(self):
        """タイマーを停止"""
        self.is_running = False
        self.is_paused = False
        self.reset()
    
    def reset(self):
        """タイマーをリセット"""
        self.current_session = "work"
        self.session_count = 0
        self.remaining_time = self.work_duration
        self.is_running = False
        self.is_paused = False
    
    def _run_timer(self):
        """タイマーのメインループ"""
        while self.is_running and self.remaining_time > 0:
            if not self.is_paused:
                self.remaining_time -= 1
                
                # 毎秒コールバックを呼び出し
                if self.on_tick:
                    self.on_tick(self.remaining_time)
                
                # セッション完了チェック
                if self.remaining_time <= 0:
                    self._complete_session()
            
            time.sleep(1)
        
        self.is_running = False
    
    def _complete_session(self):
        """セッション完了時の処理"""
        if self.on_session_complete:
            self.on_session_complete(self.current_session)
        
        if self.current_session == "work":
            self.session_count += 1
            # 4回目の作業セッション後は長い休憩
            if self.session_count % 4 == 0:
                self.current_session = "long_break"
                self.remaining_time = self.long_break
            else:
                self.current_session = "short_break"
                self.remaining_time = self.short_break
        else:
            # 休憩後は作業に戻る
            self.current_session = "work"
            self.remaining_time = self.work_duration
        
        # タイマー完了の場合
        if self.on_timer_complete:
            self.on_timer_complete()
    
    def get_formatted_time(self) -> str:
        """残り時間を MM:SS 形式で取得"""
        minutes = self.remaining_time // 60
        seconds = self.remaining_time % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def get_session_info(self) -> dict:
        """現在のセッション情報を取得"""
        session_names = {
            "work": "🍅 作業中",
            "short_break": "☕ 短い休憩",
            "long_break": "🛋️ 長い休憩"
        }
        
        return {
            "session_type": self.current_session,
            "session_name": session_names[self.current_session],
            "session_count": self.session_count,
            "remaining_time": self.remaining_time,
            "formatted_time": self.get_formatted_time(),
            "is_running": self.is_running,
            "is_paused": self.is_paused,
            "progress": self._get_progress()
        }
    
    def _get_progress(self) -> float:
        """現在のセッションの進捗を取得（0.0-1.0）"""
        if self.current_session == "work":
            total_time = self.work_duration
        elif self.current_session == "short_break":
            total_time = self.short_break
        else:
            total_time = self.long_break
        
        return (total_time - self.remaining_time) / total_time if total_time > 0 else 0.0
