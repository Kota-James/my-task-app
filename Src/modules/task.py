"""
タスク管理アプリケーション用のタスククラス
"""
from datetime import datetime
from typing import Optional
import json


class Task:
    """個々のタスクを表現するクラス"""
    
    def __init__(self, title: str, description: str = "", priority: str = "中", 
                 due_date: Optional[str] = None, category: str = "一般", tags: list = None,
                 estimated_time: int = 25, progress: int = 0):
        """
        タスクを初期化
        
        Args:
            title (str): タスクのタイトル
            description (str): タスクの詳細説明
            priority (str): 優先度 ("高", "中", "低")
            due_date (Optional[str]): 期限日 (YYYY-MM-DD形式)
            category (str): カテゴリ
            tags (list): タグのリスト
            estimated_time (int): 予想作業時間（分）
            progress (int): 進捗率（0-100）
        """
        self.id = self._generate_id()
        self.title = title
        self.description = description
        self.priority = priority
        self.due_date = due_date
        self.category = category
        self.tags = tags or []
        self.estimated_time = estimated_time  # 分単位
        self.progress = progress  # 0-100%
        self.pomodoro_count = 0  # 完了したポモドーロ数
        self.actual_time = 0  # 実際にかかった時間（分）
        self.completed = False
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def _generate_id(self) -> str:
        """ユニークなIDを生成"""
        return f"task_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    
    def toggle_completion(self):
        """タスクの完了状態を切り替え"""
        self.completed = not self.completed
        self.updated_at = datetime.now().isoformat()
    
    def update(self, title: str = None, description: str = None, 
               priority: str = None, due_date: str = None, category: str = None,
               tags: list = None, estimated_time: int = None, progress: int = None):
        """タスク情報を更新"""
        if title is not None:
            self.title = title
        if description is not None:
            self.description = description
        if priority is not None:
            self.priority = priority
        if due_date is not None:
            self.due_date = due_date
        if category is not None:
            self.category = category
        if tags is not None:
            self.tags = tags
        if estimated_time is not None:
            self.estimated_time = estimated_time
        if progress is not None:
            self.progress = max(0, min(100, progress))  # 0-100の範囲に制限
        
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> dict:
        """タスクを辞書形式で返す"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'due_date': self.due_date,
            'category': self.category,
            'tags': self.tags,
            'estimated_time': self.estimated_time,
            'progress': self.progress,
            'pomodoro_count': self.pomodoro_count,
            'actual_time': self.actual_time,
            'completed': self.completed,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Task':
        """辞書からタスクオブジェクトを作成"""
        task = cls(
            title=data['title'],
            description=data.get('description', ''),
            priority=data.get('priority', '中'),
            due_date=data.get('due_date'),
            category=data.get('category', '一般'),
            tags=data.get('tags', []),
            estimated_time=data.get('estimated_time', 25),
            progress=data.get('progress', 0)
        )
        task.id = data['id']
        task.pomodoro_count = data.get('pomodoro_count', 0)
        task.actual_time = data.get('actual_time', 0)
        task.completed = data.get('completed', False)
        task.created_at = data.get('created_at', datetime.now().isoformat())
        task.updated_at = data.get('updated_at', datetime.now().isoformat())
        return task
    
    def get_priority_color(self) -> str:
        """優先度に応じた色を返す"""
        colors = {
            "高": "#ff4757",  # 赤
            "中": "#ffa502",  # オレンジ
            "低": "#2ed573"   # 緑
        }
        return colors.get(self.priority, "#747d8c")
    
    def is_overdue(self) -> bool:
        """期限切れかどうかを判定"""
        if not self.due_date or self.completed:
            return False
        
        try:
            due = datetime.strptime(self.due_date, '%Y-%m-%d')
            return due.date() < datetime.now().date()
        except ValueError:
            return False
    
    def __str__(self) -> str:
        status = "✓" if self.completed else "○"
        return f"{status} [{self.priority}] {self.title}"
    
    def add_tag(self, tag: str):
        """タグを追加"""
        if tag and tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.now().isoformat()
    
    def remove_tag(self, tag: str):
        """タグを削除"""
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.now().isoformat()
    
    def increment_pomodoro(self):
        """ポモドーロ回数を増加"""
        self.pomodoro_count += 1
        self.actual_time += 25  # 1ポモドーロ = 25分
        self.updated_at = datetime.now().isoformat()
    
    def get_progress_color(self) -> str:
        """進捗に応じた色を返す"""
        if self.progress >= 75:
            return "#2ed573"  # 緑
        elif self.progress >= 50:
            return "#ffa502"  # オレンジ
        elif self.progress >= 25:
            return "#ff6b35"  # 薄い赤
        else:
            return "#747d8c"  # グレー
    
    def get_estimated_pomodoros(self) -> int:
        """予想ポモドーロ数を計算"""
        return max(1, (self.estimated_time + 24) // 25)  # 25分単位で切り上げ


class TaskManager:
    """タスクの管理を行うクラス"""
    
    def __init__(self):
        self.tasks = []
        self.data_file = "tasks.json"
    
    def add_task(self, task: Task):
        """タスクを追加"""
        self.tasks.append(task)
        self.save_tasks()
    
    def remove_task(self, task_id: str):
        """タスクを削除"""
        self.tasks = [task for task in self.tasks if task.id != task_id]
        self.save_tasks()
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """IDでタスクを取得"""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None
    
    def get_tasks_by_category(self, category: str) -> list:
        """カテゴリ別にタスクを取得"""
        return [task for task in self.tasks if task.category == category]
    
    def get_incomplete_tasks(self) -> list:
        """未完了のタスクを取得"""
        return [task for task in self.tasks if not task.completed]
    
    def get_completed_tasks(self) -> list:
        """完了済みのタスクを取得"""
        return [task for task in self.tasks if task.completed]
    
    def get_overdue_tasks(self) -> list:
        """期限切れのタスクを取得"""
        return [task for task in self.tasks if task.is_overdue()]
    
    def save_tasks(self):
        """タスクをJSONファイルに保存"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                tasks_data = [task.to_dict() for task in self.tasks]
                json.dump(tasks_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"タスクの保存中にエラーが発生しました: {e}")
    
    def load_tasks(self):
        """JSONファイルからタスクを読み込み"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                tasks_data = json.load(f)
                self.tasks = [Task.from_dict(data) for data in tasks_data]
        except FileNotFoundError:
            self.tasks = []
        except Exception as e:
            print(f"タスクの読み込み中にエラーが発生しました: {e}")
            self.tasks = []
    
    def get_categories(self) -> list:
        """利用可能なカテゴリのリストを取得"""
        categories = set(task.category for task in self.tasks)
        return sorted(list(categories))
    
    def get_task_count_by_status(self) -> dict:
        """ステータス別のタスク数を取得"""
        return {
            'total': len(self.tasks),
            'completed': len(self.get_completed_tasks()),
            'incomplete': len(self.get_incomplete_tasks()),
            'overdue': len(self.get_overdue_tasks())
        }