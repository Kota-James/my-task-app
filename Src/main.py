"""
美しいGUIタスク管理アプリケーション
CustomTkinterを使用したモダンなデザイン
"""
import customtkinter as ctk
from tkinter import messagebox, filedialog
import tkinter as tk
from datetime import datetime, timedelta
import os
import sys
import json

# モジュールのパスを追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from modules.task import Task, TaskManager
from modules.pomodoro import PomodoroTimer
from modules.notifications import NotificationManager
from modules.statistics import TaskStatistics


class TaskApp:
    def __init__(self):
        # CustomTkinterの設定
        ctk.set_appearance_mode("dark")  # ダークモード
        ctk.set_default_color_theme("blue")  # テーマカラー
        
        # メインウィンドウの作成
        self.root = ctk.CTk()
        self.root.title("🎯 タスクマスター Pro - Advanced Task Management")
        self.root.geometry("1400x900")
        self.root.minsize(1000, 700)
        
        # タスクマネージャーの初期化
        self.task_manager = TaskManager()
        self.task_manager.load_tasks()
        
        # 新機能の初期化
        self.pomodoro_timer = PomodoroTimer()
        self.notification_manager = NotificationManager()
        self.statistics = TaskStatistics(self.task_manager)
        
        # ポモドーロタイマーのコールバック設定
        self.pomodoro_timer.on_tick = self.update_timer_display
        self.pomodoro_timer.on_session_complete = self.on_pomodoro_session_complete
        
        # カラーパレット
        self.colors = {
            'primary': "#1f538d",
            'secondary': "#2980b9",
            'success': "#27ae60",
            'warning': "#f39c12",
            'danger': "#e74c3c",
            'dark': "#2c3e50",
            'light': "#ecf0f1"
        }
        
        # 現在選択されているタスク
        self.selected_task = None
        
        # テーマ設定
        self.current_theme = "dark"
        
        # UI要素の初期化
        self.setup_ui()
        self.update_task_list()
        self.update_statistics()
        
        # ウィンドウを閉じる際の処理
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_ui(self):
        """UIレイアウトをセットアップ"""
        # メインフレームの作成
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # タブビューの作成
        self.tabview = ctk.CTkTabview(self.main_frame)
        self.tabview.pack(fill="both", expand=True)
        
        # タブの追加
        self.tabview.add("📋 タスク管理")
        self.tabview.add("🍅 ポモドーロ")
        self.tabview.add("📊 統計")
        self.tabview.add("⚙️ 設定")
        
        # 各タブのセットアップ
        self.setup_task_tab()
        self.setup_pomodoro_tab()
        self.setup_statistics_tab()
        self.setup_settings_tab()
    
    def setup_task_tab(self):
        """タスク管理タブのセットアップ"""
        task_frame = self.tabview.tab("📋 タスク管理")
        
        # 左側パネル（統計とコントロール）
        self.left_panel = ctk.CTkFrame(task_frame, width=350)
        self.left_panel.pack(side="left", fill="y", padx=(0, 10))
        self.left_panel.pack_propagate(False)
        
        # 右側パネル（タスクリストと詳細）
        self.right_panel = ctk.CTkFrame(task_frame)
        self.right_panel.pack(side="right", fill="both", expand=True)
        
        self.setup_left_panel()
        self.setup_right_panel()
    
    def setup_left_panel(self):
        """左側パネルのセットアップ"""
        # タイトル
        title_label = ctk.CTkLabel(
            self.left_panel, 
            text="🎯 タスクマスター Pro",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(15, 25))
        
        # 統計情報フレーム
        self.stats_frame = ctk.CTkFrame(self.left_panel)
        self.stats_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        stats_title = ctk.CTkLabel(
            self.stats_frame,
            text="📊 統計情報",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        stats_title.pack(pady=(12, 8))
        
        # 統計ラベル
        self.total_label = ctk.CTkLabel(self.stats_frame, text="総タスク数: 0")
        self.total_label.pack(pady=1)
        
        self.incomplete_label = ctk.CTkLabel(self.stats_frame, text="未完了: 0")
        self.incomplete_label.pack(pady=1)
        
        self.completed_label = ctk.CTkLabel(self.stats_frame, text="完了済み: 0")
        self.completed_label.pack(pady=1)
        
        self.overdue_label = ctk.CTkLabel(self.stats_frame, text="期限切れ: 0", text_color="red")
        self.overdue_label.pack(pady=(1, 12))
        
        # ボタンフレーム
        self.button_frame = ctk.CTkFrame(self.left_panel)
        self.button_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        button_title = ctk.CTkLabel(
            self.button_frame,
            text="🛠️ 操作",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        button_title.pack(pady=(15, 10))
        
        # 新規タスク追加ボタン
        self.add_button = ctk.CTkButton(
            self.button_frame,
            text="➕ 新しいタスク",
            command=self.show_add_task_dialog,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.add_button.pack(fill="x", padx=15, pady=5)
        
        # タスク編集ボタン
        self.edit_button = ctk.CTkButton(
            self.button_frame,
            text="✏️ 編集",
            command=self.show_edit_task_dialog,
            height=35,
            state="disabled"
        )
        self.edit_button.pack(fill="x", padx=15, pady=5)
        
        # タスク削除ボタン
        self.delete_button = ctk.CTkButton(
            self.button_frame,
            text="🗑️ 削除",
            command=self.delete_task,
            height=35,
            fg_color="red",
            hover_color="darkred",
            state="disabled"
        )
        self.delete_button.pack(fill="x", padx=15, pady=5)
        
        # 完了切り替えボタン
        self.toggle_button = ctk.CTkButton(
            self.button_frame,
            text="✅ 完了切替",
            command=self.toggle_task_completion,
            height=35,
            state="disabled"
        )
        self.toggle_button.pack(fill="x", padx=15, pady=(5, 15))
        
        # フィルターフレーム
        self.filter_frame = ctk.CTkFrame(self.left_panel)
        self.filter_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        filter_title = ctk.CTkLabel(
            self.filter_frame,
            text="🔍 フィルター",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        filter_title.pack(pady=(15, 10))
        
        # フィルターオプション
        self.filter_var = tk.StringVar(value="すべて")
        filter_options = ["すべて", "未完了", "完了済み", "期限切れ"]
        
        self.filter_menu = ctk.CTkOptionMenu(
            self.filter_frame,
            variable=self.filter_var,
            values=filter_options,
            command=self.apply_filter
        )
        self.filter_menu.pack(fill="x", padx=15, pady=(0, 15))
    
    def setup_pomodoro_tab(self):
        """ポモドーロタブのセットアップ"""
        pomodoro_frame = self.tabview.tab("🍅 ポモドーロ")
        
        # ポモドーロタイマーメインフレーム
        timer_main_frame = ctk.CTkFrame(pomodoro_frame)
        timer_main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # タイトル
        timer_title = ctk.CTkLabel(
            timer_main_frame,
            text="🍅 ポモドーロタイマー",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        timer_title.pack(pady=(20, 30))
        
        # タイマー表示エリア
        self.timer_display_frame = ctk.CTkFrame(timer_main_frame)
        self.timer_display_frame.pack(fill="x", padx=40, pady=20)
        
        # セッション情報
        self.session_label = ctk.CTkLabel(
            self.timer_display_frame,
            text="🍅 作業中",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.session_label.pack(pady=(20, 10))
        
        # タイマー表示
        self.timer_label = ctk.CTkLabel(
            self.timer_display_frame,
            text="25:00",
            font=ctk.CTkFont(size=48, weight="bold")
        )
        self.timer_label.pack(pady=10)
        
        # プログレスバー
        self.timer_progress = ctk.CTkProgressBar(self.timer_display_frame, width=300)
        self.timer_progress.pack(pady=(10, 20))
        self.timer_progress.set(0)
        
        # ポモドーロ回数表示
        self.pomodoro_count_label = ctk.CTkLabel(
            self.timer_display_frame,
            text="完了ポモドーロ: 0回",
            font=ctk.CTkFont(size=14)
        )
        self.pomodoro_count_label.pack(pady=(0, 20))
        
        # コントロールボタン
        control_frame = ctk.CTkFrame(timer_main_frame)
        control_frame.pack(fill="x", padx=40, pady=20)
        
        button_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        button_frame.pack(expand=True)
        
        self.start_button = ctk.CTkButton(
            button_frame,
            text="▶️ 開始",
            command=self.start_pomodoro,
            width=100,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.start_button.pack(side="left", padx=5)
        
        self.pause_button = ctk.CTkButton(
            button_frame,
            text="⏸️ 一時停止",
            command=self.pause_pomodoro,
            width=100,
            height=40,
            state="disabled"
        )
        self.pause_button.pack(side="left", padx=5)
        
        self.stop_button = ctk.CTkButton(
            button_frame,
            text="⏹️ 停止",
            command=self.stop_pomodoro,
            width=100,
            height=40,
            fg_color="red",
            hover_color="darkred",
            state="disabled"
        )
        self.stop_button.pack(side="left", padx=5)
        
        # タスク選択フレーム
        task_selection_frame = ctk.CTkFrame(timer_main_frame)
        task_selection_frame.pack(fill="x", padx=40, pady=20)
        
        ctk.CTkLabel(
            task_selection_frame,
            text="📝 作業中のタスク",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(15, 10))
        
        # タスク選択コンボボックス
        self.current_task_var = tk.StringVar()
        self.task_combobox = ctk.CTkComboBox(
            task_selection_frame,
            variable=self.current_task_var,
            values=self.get_incomplete_task_titles(),
            state="readonly"
        )
        self.task_combobox.pack(fill="x", padx=20, pady=(0, 15))
        
        # 設定フレーム
        settings_frame = ctk.CTkFrame(timer_main_frame)
        settings_frame.pack(fill="x", padx=40, pady=20)
        
        ctk.CTkLabel(
            settings_frame,
            text="⚙️ タイマー設定",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(15, 10))
        
        # 時間設定
        time_setting_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        time_setting_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        ctk.CTkLabel(time_setting_frame, text="作業時間（分）:").pack(side="left")
        self.work_time_var = tk.StringVar(value="25")
        work_time_entry = ctk.CTkEntry(time_setting_frame, textvariable=self.work_time_var, width=60)
        work_time_entry.pack(side="left", padx=(10, 20))
        
        ctk.CTkLabel(time_setting_frame, text="休憩時間（分）:").pack(side="left")
        self.break_time_var = tk.StringVar(value="5")
        break_time_entry = ctk.CTkEntry(time_setting_frame, textvariable=self.break_time_var, width=60)
        break_time_entry.pack(side="left", padx=(10, 0))
    
    def setup_statistics_tab(self):
        """統計タブのセットアップ"""
        stats_frame = self.tabview.tab("📊 統計")
        
        # スクロール可能なフレーム
        scrollable_stats = ctk.CTkScrollableFrame(stats_frame)
        scrollable_stats.pack(fill="both", expand=True, padx=20, pady=20)
        
        # タイトル
        stats_title = ctk.CTkLabel(
            scrollable_stats,
            text="📊 詳細統計分析",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        stats_title.pack(pady=(20, 30))
        
        # 生産性統計
        productivity_frame = ctk.CTkFrame(scrollable_stats)
        productivity_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            productivity_frame,
            text="🚀 生産性統計",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(15, 10))
        
        self.productivity_stats_frame = ctk.CTkFrame(productivity_frame, fg_color="transparent")
        self.productivity_stats_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        # カテゴリ統計
        category_frame = ctk.CTkFrame(scrollable_stats)
        category_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            category_frame,
            text="📁 カテゴリ別分析",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(15, 10))
        
        self.category_stats_frame = ctk.CTkFrame(category_frame, fg_color="transparent")
        self.category_stats_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        # エクスポートボタン
        export_frame = ctk.CTkFrame(scrollable_stats)
        export_frame.pack(fill="x", padx=20, pady=20)
        
        export_button = ctk.CTkButton(
            export_frame,
            text="📥 統計データをエクスポート",
            command=self.export_statistics,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        export_button.pack(pady=15)
    
    def setup_settings_tab(self):
        """設定タブのセットアップ"""
        settings_frame = self.tabview.tab("⚙️ 設定")
        
        # 設定メインフレーム
        settings_main = ctk.CTkFrame(settings_frame)
        settings_main.pack(fill="both", expand=True, padx=20, pady=20)
        
        # タイトル
        settings_title = ctk.CTkLabel(
            settings_main,
            text="⚙️ アプリケーション設定",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        settings_title.pack(pady=(20, 30))
        
        # テーマ設定
        theme_frame = ctk.CTkFrame(settings_main)
        theme_frame.pack(fill="x", padx=40, pady=20)
        
        ctk.CTkLabel(
            theme_frame,
            text="🎨 テーマ設定",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(15, 10))
        
        theme_control_frame = ctk.CTkFrame(theme_frame, fg_color="transparent")
        theme_control_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        ctk.CTkLabel(theme_control_frame, text="外観モード:").pack(side="left")
        
        self.theme_var = tk.StringVar(value="dark")
        theme_menu = ctk.CTkOptionMenu(
            theme_control_frame,
            variable=self.theme_var,
            values=["dark", "light", "system"],
            command=self.change_theme
        )
        theme_menu.pack(side="left", padx=(10, 0))
        
        # 通知設定
        notification_frame = ctk.CTkFrame(settings_main)
        notification_frame.pack(fill="x", padx=40, pady=20)
        
        ctk.CTkLabel(
            notification_frame,
            text="🔔 通知設定",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(15, 10))
        
        notification_control_frame = ctk.CTkFrame(notification_frame, fg_color="transparent")
        notification_control_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        self.sound_enabled_var = tk.BooleanVar(value=True)
        sound_checkbox = ctk.CTkCheckBox(
            notification_control_frame,
            text="サウンド通知を有効にする",
            variable=self.sound_enabled_var,
            command=self.toggle_sound
        )
        sound_checkbox.pack(side="left")
        
        # データ管理
        data_frame = ctk.CTkFrame(settings_main)
        data_frame.pack(fill="x", padx=40, pady=20)
        
        ctk.CTkLabel(
            data_frame,
            text="💾 データ管理",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(15, 10))
        
        data_button_frame = ctk.CTkFrame(data_frame, fg_color="transparent")
        data_button_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        export_tasks_button = ctk.CTkButton(
            data_button_frame,
            text="📤 タスクをエクスポート",
            command=self.export_tasks,
            width=150
        )
        export_tasks_button.pack(side="left", padx=(0, 10))
        
        import_tasks_button = ctk.CTkButton(
            data_button_frame,
            text="📥 タスクをインポート",
            command=self.import_tasks,
            width=150
        )
        import_tasks_button.pack(side="left")
    
    def setup_right_panel(self):
        """右側パネルのセットアップ"""
        # タスクリストフレーム
        self.task_list_frame = ctk.CTkFrame(self.right_panel)
        self.task_list_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # タスクリストタイトル
        list_title = ctk.CTkLabel(
            self.task_list_frame,
            text="📋 タスク一覧",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        list_title.pack(pady=(20, 10))
        
        # スクロール可能なタスクリスト
        self.scrollable_frame = ctk.CTkScrollableFrame(self.task_list_frame)
        self.scrollable_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # タスクアイテムを格納するリスト
        self.task_items = []
    
    def create_task_item(self, task):
        """個別のタスクアイテムを作成"""
        # タスクアイテムフレーム
        item_frame = ctk.CTkFrame(self.scrollable_frame)
        item_frame.pack(fill="x", padx=5, pady=5)
        
        # タスクが選択された時の処理
        def on_task_select():
            self.selected_task = task
            self.update_button_states()
            # 他のタスクの選択を解除
            for item in self.task_items:
                if item != item_frame:
                    item.configure(border_width=0)
            # このタスクを選択状態にする
            item_frame.configure(border_width=2, border_color="blue")
        
        # クリックイベントを追加
        item_frame.bind("<Button-1>", lambda e: on_task_select())
        
        # タスク情報のレイアウト
        info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        info_frame.pack(fill="x", padx=15, pady=10)
        
        # タイトル行
        title_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        title_frame.pack(fill="x")
        
        # 完了状態のアイコン
        status_icon = "✅" if task.completed else "⭕"
        status_label = ctk.CTkLabel(
            title_frame,
            text=status_icon,
            font=ctk.CTkFont(size=16)
        )
        status_label.pack(side="left")
        
        # タイトル
        title_text = task.title
        if task.completed:
            title_text = f"~~{title_text}~~"
        
        title_label = ctk.CTkLabel(
            title_frame,
            text=title_text,
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        title_label.pack(side="left", padx=(10, 0), fill="x", expand=True)
        
        # 優先度バッジ
        priority_color = task.get_priority_color()
        priority_label = ctk.CTkLabel(
            title_frame,
            text=f"[{task.priority}]",
            text_color=priority_color,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        priority_label.pack(side="right")
        
        # 詳細情報行
        if task.description or task.due_date or task.category or task.progress > 0:
            details_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
            details_frame.pack(fill="x", pady=(5, 0))
            
            details_text = ""
            if task.category:
                details_text += f"📁 {task.category}  "
            if task.due_date:
                details_text += f"📅 {task.due_date}  "
                if task.is_overdue():
                    details_text += "⚠️ 期限切れ"
            if task.pomodoro_count > 0:
                details_text += f"  🍅 {task.pomodoro_count}ポモドーロ"
            
            if details_text:
                details_label = ctk.CTkLabel(
                    details_frame,
                    text=details_text,
                    font=ctk.CTkFont(size=11),
                    text_color="gray",
                    anchor="w"
                )
                details_label.pack(side="left")
            
            # プログレスバー
            if task.progress > 0:
                progress_frame = ctk.CTkFrame(details_frame, fg_color="transparent")
                progress_frame.pack(fill="x", pady=(5, 0))
                
                progress_label = ctk.CTkLabel(
                    progress_frame,
                    text=f"進捗: {task.progress}%",
                    font=ctk.CTkFont(size=10),
                    text_color=task.get_progress_color()
                )
                progress_label.pack(side="left")
                
                progress_bar = ctk.CTkProgressBar(
                    progress_frame,
                    width=150,
                    height=8,
                    progress_color=task.get_progress_color()
                )
                progress_bar.pack(side="left", padx=(10, 0))
                progress_bar.set(task.progress / 100)
            
            if task.description:
                desc_label = ctk.CTkLabel(
                    details_frame,
                    text=f"💭 {task.description[:50]}..." if len(task.description) > 50 else f"💭 {task.description}",
                    font=ctk.CTkFont(size=11),
                    text_color="lightgray",
                    anchor="w"
                )
                desc_label.pack(fill="x", pady=(2, 0))
        
        # すべての子ウィジェットにクリックイベントを追加
        def bind_click_recursive(widget):
            widget.bind("<Button-1>", lambda e: on_task_select())
            for child in widget.winfo_children():
                bind_click_recursive(child)
        
        bind_click_recursive(item_frame)
        
        self.task_items.append(item_frame)
        return item_frame
    
    def update_task_list(self):
        """タスクリストを更新"""
        # 既存のタスクアイテムを削除
        for item in self.task_items:
            item.destroy()
        self.task_items.clear()
        
        # フィルター適用
        tasks = self.get_filtered_tasks()
        
        if not tasks:
            # タスクがない場合のメッセージ
            no_tasks_label = ctk.CTkLabel(
                self.scrollable_frame,
                text="📝 タスクがありません\n\n「新しいタスク」ボタンから\nタスクを追加してください",
                font=ctk.CTkFont(size=16),
                text_color="gray"
            )
            no_tasks_label.pack(expand=True)
            self.task_items.append(no_tasks_label)
        else:
            # タスクアイテムを作成
            for task in tasks:
                self.create_task_item(task)
        
        # 選択状態をリセット
        self.selected_task = None
        self.update_button_states()
    
    def get_filtered_tasks(self):
        """フィルターに基づいてタスクを取得"""
        filter_value = self.filter_var.get()
        
        if filter_value == "未完了":
            return self.task_manager.get_incomplete_tasks()
        elif filter_value == "完了済み":
            return self.task_manager.get_completed_tasks()
        elif filter_value == "期限切れ":
            return self.task_manager.get_overdue_tasks()
        else:
            return self.task_manager.tasks
    
    def update_statistics(self):
        """統計情報を更新"""
        stats = self.task_manager.get_task_count_by_status()
        
        self.total_label.configure(text=f"総タスク数: {stats['total']}")
        self.incomplete_label.configure(text=f"未完了: {stats['incomplete']}")
        self.completed_label.configure(text=f"完了済み: {stats['completed']}")
        self.overdue_label.configure(text=f"期限切れ: {stats['overdue']}")
        
        # 詳細統計も更新（統計タブが存在する場合）
        try:
            self.update_detailed_statistics()
        except AttributeError:
            # まだ統計タブが作成されていない場合は無視
            pass
        
        # ポモドーロタブのタスクリストも更新
        try:
            self.task_combobox.configure(values=self.get_incomplete_task_titles())
        except AttributeError:
            # まだポモドーロタブが作成されていない場合は無視
            pass
    
    def update_button_states(self):
        """ボタンの有効/無効状態を更新"""
        has_selection = self.selected_task is not None
        
        state = "normal" if has_selection else "disabled"
        self.edit_button.configure(state=state)
        self.delete_button.configure(state=state)
        self.toggle_button.configure(state=state)
    
    def apply_filter(self, value):
        """フィルターを適用"""
        self.update_task_list()
    
    def show_add_task_dialog(self):
        """新規タスク追加ダイアログを表示"""
        dialog = TaskDialog(self.root, "新しいタスクを追加")
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            task = Task(
                title=dialog.result['title'],
                description=dialog.result['description'],
                priority=dialog.result['priority'],
                due_date=dialog.result['due_date'],
                category=dialog.result['category'],
                tags=dialog.result['tags'],
                estimated_time=dialog.result['estimated_time'],
                progress=dialog.result['progress']
            )
            self.task_manager.add_task(task)
            self.update_task_list()
            self.update_statistics()
            
            # 通知音
            self.notification_manager.play_sound('task_complete')
    
    def show_edit_task_dialog(self):
        """タスク編集ダイアログを表示"""
        if not self.selected_task:
            return
        
        dialog = TaskDialog(self.root, "タスクを編集", self.selected_task)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            self.selected_task.update(
                title=dialog.result['title'],
                description=dialog.result['description'],
                priority=dialog.result['priority'],
                due_date=dialog.result['due_date'],
                category=dialog.result['category'],
                tags=dialog.result['tags'],
                estimated_time=dialog.result['estimated_time'],
                progress=dialog.result['progress']
            )
            self.task_manager.save_tasks()
            self.update_task_list()
            self.update_statistics()
    
    def delete_task(self):
        """選択されたタスクを削除"""
        if not self.selected_task:
            return
        
        result = messagebox.askyesno(
            "確認",
            f"タスク「{self.selected_task.title}」を削除しますか？"
        )
        
        if result:
            self.task_manager.remove_task(self.selected_task.id)
            self.update_task_list()
            self.update_statistics()
    
    def toggle_task_completion(self):
        """選択されたタスクの完了状態を切り替え"""
        if not self.selected_task:
            return
        
        self.selected_task.toggle_completion()
        self.task_manager.save_tasks()
        self.update_task_list()
        self.update_statistics()
    
    def on_closing(self):
        """アプリケーション終了時の処理"""
        self.pomodoro_timer.stop()
        self.task_manager.save_tasks()
        self.root.destroy()
    
    # ポモドーロタイマー関連メソッド
    def start_pomodoro(self):
        """ポモドーロタイマーを開始"""
        # 設定から作業時間と休憩時間を取得
        try:
            work_time = int(self.work_time_var.get())
            break_time = int(self.break_time_var.get())
            self.pomodoro_timer.work_duration = work_time * 60
            self.pomodoro_timer.short_break = break_time * 60
        except ValueError:
            messagebox.showerror("エラー", "時間設定が正しくありません。")
            return
        
        self.pomodoro_timer.start()
        self.start_button.configure(state="disabled")
        self.pause_button.configure(state="normal")
        self.stop_button.configure(state="normal")
        
        # 通知
        self.notification_manager.play_sound('timer_alert')
    
    def pause_pomodoro(self):
        """ポモドーロタイマーを一時停止/再開"""
        if self.pomodoro_timer.is_paused:
            self.pomodoro_timer.resume()
            self.pause_button.configure(text="⏸️ 一時停止")
        else:
            self.pomodoro_timer.pause()
            self.pause_button.configure(text="▶️ 再開")
    
    def stop_pomodoro(self):
        """ポモドーロタイマーを停止"""
        self.pomodoro_timer.stop()
        self.start_button.configure(state="normal")
        self.pause_button.configure(state="disabled", text="⏸️ 一時停止")
        self.stop_button.configure(state="disabled")
        self.timer_label.configure(text="25:00")
        self.timer_progress.set(0)
    
    def update_timer_display(self, remaining_time):
        """タイマー表示を更新"""
        session_info = self.pomodoro_timer.get_session_info()
        
        # 表示を更新
        self.session_label.configure(text=session_info['session_name'])
        self.timer_label.configure(text=session_info['formatted_time'])
        self.timer_progress.set(session_info['progress'])
        self.pomodoro_count_label.configure(text=f"完了ポモドーロ: {session_info['session_count']}回")
    
    def on_pomodoro_session_complete(self, session_type):
        """ポモドーロセッション完了時の処理"""
        if session_type == "work":
            # 作業セッション完了
            task_title = self.current_task_var.get()
            if task_title and task_title != "タスクを選択してください":
                # 選択されたタスクのポモドーロ回数を増加
                for task in self.task_manager.tasks:
                    if task.title == task_title:
                        task.increment_pomodoro()
                        break
                self.task_manager.save_tasks()
                self.update_task_list()
            
            self.notification_manager.show_notification(
                "ポモドーロ完了！",
                "お疲れ様でした！休憩時間です。",
                'session_complete'
            )
        else:
            # 休憩セッション完了
            self.notification_manager.show_notification(
                "休憩終了",
                "次の作業セッションを始めましょう！",
                'session_complete'
            )
    
    def get_incomplete_task_titles(self):
        """未完了タスクのタイトル一覧を取得"""
        incomplete_tasks = self.task_manager.get_incomplete_tasks()
        titles = [task.title for task in incomplete_tasks]
        return ["タスクを選択してください"] + titles if titles else ["タスクを選択してください"]
    
    # 統計関連メソッド
    def update_detailed_statistics(self):
        """詳細統計を更新"""
        # 生産性統計の更新
        productivity_stats = self.statistics.get_productivity_stats()
        
        # 既存のウィジェットを削除
        for widget in self.productivity_stats_frame.winfo_children():
            widget.destroy()
        
        # 生産性統計の表示
        stats_text = f"""
        📈 完了率: {productivity_stats['completion_rate']}%
        ⏱️ 総作業時間: {productivity_stats['total_actual_time']}分
        🍅 総ポモドーロ: {productivity_stats['total_pomodoros']}回
        📊 効率性: {productivity_stats['efficiency']}%
        ⌚ 平均タスク時間: {productivity_stats['average_task_time']}分
        """
        
        ctk.CTkLabel(
            self.productivity_stats_frame,
            text=stats_text,
            font=ctk.CTkFont(size=12),
            justify="left"
        ).pack(anchor="w")
        
        # カテゴリ統計の更新
        category_stats = self.statistics.get_category_stats()
        
        # 既存のウィジェットを削除
        for widget in self.category_stats_frame.winfo_children():
            widget.destroy()
        
        # カテゴリ統計の表示
        for category, stats in category_stats.items():
            category_text = f"📁 {category}: 総数{stats['total']} | 完了{stats['completed']} | 進行中{stats['in_progress']} | 期限切れ{stats['overdue']}"
            ctk.CTkLabel(
                self.category_stats_frame,
                text=category_text,
                font=ctk.CTkFont(size=11),
                justify="left"
            ).pack(anchor="w", pady=2)
    
    def export_statistics(self):
        """統計データをエクスポート"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="統計データを保存"
            )
            
            if filename:
                self.statistics.export_statistics(filename)
                messagebox.showinfo("成功", f"統計データを {filename} にエクスポートしました。")
        except Exception as e:
            messagebox.showerror("エラー", f"エクスポートに失敗しました: {e}")
    
    # 設定関連メソッド
    def change_theme(self, new_theme):
        """テーマを変更"""
        ctk.set_appearance_mode(new_theme)
        self.current_theme = new_theme
    
    def toggle_sound(self):
        """サウンドの有効/無効を切り替え"""
        self.notification_manager.set_sound_enabled(self.sound_enabled_var.get())
    
    def export_tasks(self):
        """タスクをJSONファイルにエクスポート"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="タスクデータを保存"
            )
            
            if filename:
                tasks_data = [task.to_dict() for task in self.task_manager.tasks]
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(tasks_data, f, ensure_ascii=False, indent=2)
                messagebox.showinfo("成功", f"タスクデータを {filename} にエクスポートしました。")
        except Exception as e:
            messagebox.showerror("エラー", f"エクスポートに失敗しました: {e}")
    
    def import_tasks(self):
        """JSONファイルからタスクをインポート"""
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="タスクデータを読み込み"
            )
            
            if filename:
                with open(filename, 'r', encoding='utf-8') as f:
                    tasks_data = json.load(f)
                
                imported_count = 0
                for task_data in tasks_data:
                    try:
                        task = Task.from_dict(task_data)
                        self.task_manager.add_task(task)
                        imported_count += 1
                    except Exception:
                        continue  # 無効なタスクデータはスキップ
                
                self.update_task_list()
                self.update_statistics()
                messagebox.showinfo("成功", f"{imported_count}件のタスクをインポートしました。")
        except Exception as e:
            messagebox.showerror("エラー", f"インポートに失敗しました: {e}")
    
    def run(self):
        """アプリケーションを実行"""
        self.root.mainloop()


class TaskDialog:
    """タスク追加/編集用のダイアログ"""
    
    def __init__(self, parent, title, task=None):
        self.result = None
        
        # ダイアログウィンドウの作成
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("550x750")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # ウィンドウを中央に配置
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (550 // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (750 // 2)
        self.dialog.geometry(f"550x750+{x}+{y}")
        
        self.setup_dialog(task)
    
    def setup_dialog(self, task):
        """ダイアログのUIをセットアップ"""
        # メインフレーム
        main_frame = ctk.CTkFrame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # タイトル
        title_label = ctk.CTkLabel(
            main_frame,
            text="📝 タスク情報",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(20, 30))
        
        # タスクタイトル
        ctk.CTkLabel(main_frame, text="タスク名 *", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20)
        self.title_entry = ctk.CTkEntry(main_frame, height=35)
        self.title_entry.pack(fill="x", padx=20, pady=(5, 15))
        
        # 説明
        ctk.CTkLabel(main_frame, text="説明", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20)
        self.description_text = ctk.CTkTextbox(main_frame, height=100)
        self.description_text.pack(fill="x", padx=20, pady=(5, 15))
        
        # 優先度
        ctk.CTkLabel(main_frame, text="優先度", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20)
        self.priority_var = tk.StringVar(value="中")
        self.priority_menu = ctk.CTkOptionMenu(
            main_frame,
            variable=self.priority_var,
            values=["高", "中", "低"]
        )
        self.priority_menu.pack(fill="x", padx=20, pady=(5, 15))
        
        # カテゴリ
        ctk.CTkLabel(main_frame, text="カテゴリ", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20)
        self.category_entry = ctk.CTkEntry(main_frame, height=35)
        self.category_entry.pack(fill="x", padx=20, pady=(5, 15))
        
        # 期限日
        ctk.CTkLabel(main_frame, text="期限日 (YYYY-MM-DD形式)", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20)
        self.due_date_entry = ctk.CTkEntry(main_frame, height=35, placeholder_text="例: 2024-12-31")
        self.due_date_entry.pack(fill="x", padx=20, pady=(5, 15))
        
        # タグ
        ctk.CTkLabel(main_frame, text="タグ (カンマ区切り)", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20)
        self.tags_entry = ctk.CTkEntry(main_frame, height=35, placeholder_text="例: 重要, 緊急, プロジェクトA")
        self.tags_entry.pack(fill="x", padx=20, pady=(5, 15))
        
        # 予想作業時間
        ctk.CTkLabel(main_frame, text="予想作業時間 (分)", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20)
        self.estimated_time_entry = ctk.CTkEntry(main_frame, height=35, placeholder_text="例: 120")
        self.estimated_time_entry.pack(fill="x", padx=20, pady=(5, 15))
        
        # 進捗率
        ctk.CTkLabel(main_frame, text="進捗率 (%)", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20)
        progress_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        progress_frame.pack(fill="x", padx=20, pady=(5, 15))
        
        self.progress_var = tk.IntVar(value=0)
        self.progress_slider = ctk.CTkSlider(
            progress_frame,
            from_=0,
            to=100,
            variable=self.progress_var,
            number_of_steps=100
        )
        self.progress_slider.pack(side="left", fill="x", expand=True)
        
        self.progress_label = ctk.CTkLabel(progress_frame, text="0%", width=40)
        self.progress_label.pack(side="right", padx=(10, 0))
        
        # スライダーの値が変更されたときにラベルを更新
        self.progress_slider.configure(command=self.update_progress_label)
        
        # 便利な日付ボタン
        date_button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        date_button_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        today_btn = ctk.CTkButton(
            date_button_frame,
            text="今日",
            command=lambda: self.set_date(0),
            width=80,
            height=30
        )
        today_btn.pack(side="left", padx=(0, 5))
        
        tomorrow_btn = ctk.CTkButton(
            date_button_frame,
            text="明日",
            command=lambda: self.set_date(1),
            width=80,
            height=30
        )
        tomorrow_btn.pack(side="left", padx=5)
        
        week_btn = ctk.CTkButton(
            date_button_frame,
            text="1週間後",
            command=lambda: self.set_date(7),
            width=80,
            height=30
        )
        week_btn.pack(side="left", padx=5)
        
        # ボタンフレーム
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(20, 20))
        
        # キャンセルボタン
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="キャンセル",
            command=self.cancel,
            fg_color="gray",
            hover_color="darkgray"
        )
        cancel_btn.pack(side="right", padx=(10, 0))
        
        # 保存ボタン
        save_btn = ctk.CTkButton(
            button_frame,
            text="保存",
            command=self.save,
            height=35
        )
        save_btn.pack(side="right")
        
        # 既存タスクの情報を設定
        if task:
            self.title_entry.insert(0, task.title)
            self.description_text.insert("1.0", task.description)
            self.priority_var.set(task.priority)
            self.category_entry.insert(0, task.category)
            if task.due_date:
                self.due_date_entry.insert(0, task.due_date)
            if task.tags:
                self.tags_entry.insert(0, ", ".join(task.tags))
            self.estimated_time_entry.insert(0, str(task.estimated_time))
            self.progress_var.set(task.progress)
            self.update_progress_label(task.progress)
        else:
            # デフォルト値
            self.category_entry.insert(0, "一般")
            self.estimated_time_entry.insert(0, "25")
        
        # フォーカスをタイトルに設定
        self.title_entry.focus()
    
    def update_progress_label(self, value):
        """進捗ラベルを更新"""
        self.progress_label.configure(text=f"{int(value)}%")
    
    def set_date(self, days_offset):
        """日付を設定"""
        target_date = datetime.now() + timedelta(days=days_offset)
        date_str = target_date.strftime("%Y-%m-%d")
        self.due_date_entry.delete(0, tk.END)
        self.due_date_entry.insert(0, date_str)
    
    def save(self):
        """入力内容を保存"""
        title = self.title_entry.get().strip()
        if not title:
            messagebox.showerror("エラー", "タスク名を入力してください。")
            return
        
        description = self.description_text.get("1.0", tk.END).strip()
        priority = self.priority_var.get()
        category = self.category_entry.get().strip() or "一般"
        due_date = self.due_date_entry.get().strip() or None
        
        # タグの処理
        tags_text = self.tags_entry.get().strip()
        tags = [tag.strip() for tag in tags_text.split(",") if tag.strip()] if tags_text else []
        
        # 予想時間の処理
        try:
            estimated_time = int(self.estimated_time_entry.get().strip()) if self.estimated_time_entry.get().strip() else 25
        except ValueError:
            messagebox.showerror("エラー", "予想作業時間は数値で入力してください。")
            return
        
        # 進捗率
        progress = self.progress_var.get()
        
        # 日付の形式チェック
        if due_date:
            try:
                datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("エラー", "期限日の形式が正しくありません。\nYYYY-MM-DD形式で入力してください。")
                return
        
        self.result = {
            'title': title,
            'description': description,
            'priority': priority,
            'category': category,
            'due_date': due_date,
            'tags': tags,
            'estimated_time': estimated_time,
            'progress': progress
        }
        
        self.dialog.destroy()
    
    def cancel(self):
        """キャンセル"""
        self.dialog.destroy()


def main():
    """メイン関数"""
    app = TaskApp()
    app.run()


if __name__ == "__main__":
    main()