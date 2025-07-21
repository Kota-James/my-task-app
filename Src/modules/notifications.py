"""
通知システム
"""
import winsound
import threading
from typing import Optional


class NotificationManager:
    """通知管理クラス"""
    
    def __init__(self):
        self.sound_enabled = True
        self.custom_sounds = {
            'task_complete': self._create_completion_sound,
            'session_complete': self._create_session_sound,
            'timer_alert': self._create_alert_sound,
            'reminder': self._create_reminder_sound
        }
    
    def play_sound(self, sound_type: str = 'timer_alert'):
        """サウンドを再生"""
        if not self.sound_enabled:
            return
        
        def play():
            try:
                if sound_type in self.custom_sounds:
                    self.custom_sounds[sound_type]()
                else:
                    winsound.Beep(800, 300)
            except Exception:
                # サウンド再生失敗時は無視
                pass
        
        # 別スレッドで再生して UIをブロックしない
        sound_thread = threading.Thread(target=play)
        sound_thread.daemon = True
        sound_thread.start()
    
    def _create_completion_sound(self):
        """タスク完了音"""
        # 上昇音階
        frequencies = [523, 659, 784, 1047]  # C, E, G, C
        for freq in frequencies:
            winsound.Beep(freq, 200)
    
    def _create_session_sound(self):
        """セッション完了音"""
        # 短い通知音
        winsound.Beep(800, 300)
        winsound.Beep(1000, 300)
    
    def _create_alert_sound(self):
        """アラート音"""
        # 注意喚起音
        for _ in range(3):
            winsound.Beep(1000, 200)
            winsound.Beep(800, 200)
    
    def _create_reminder_sound(self):
        """リマインダー音"""
        # 優しい通知音
        winsound.Beep(600, 400)
    
    def show_notification(self, title: str, message: str, sound_type: str = 'timer_alert'):
        """通知を表示（Windows標準の通知システムを使用）"""
        try:
            import plyer
            plyer.notification.notify(
                title=title,
                message=message,
                app_name="タスクマスター",
                timeout=5
            )
        except ImportError:
            # plyer がない場合はサウンドのみ
            pass
        
        self.play_sound(sound_type)
    
    def set_sound_enabled(self, enabled: bool):
        """サウンドの有効/無効を設定"""
        self.sound_enabled = enabled
