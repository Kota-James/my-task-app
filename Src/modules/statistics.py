"""
統計分析モジュール
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json
from modules.task import Task, TaskManager


class TaskStatistics:
    """タスク統計クラス"""
    
    def __init__(self, task_manager: TaskManager):
        self.task_manager = task_manager
    
    def get_productivity_stats(self) -> Dict[str, Any]:
        """生産性統計を取得"""
        tasks = self.task_manager.tasks
        completed_tasks = self.task_manager.get_completed_tasks()
        
        total_estimated_time = sum(task.estimated_time for task in tasks)
        total_actual_time = sum(task.actual_time for task in completed_tasks)
        total_pomodoros = sum(task.pomodoro_count for task in completed_tasks)
        
        # 完了率
        completion_rate = (len(completed_tasks) / len(tasks)) * 100 if tasks else 0
        
        # 時間効率性（実際時間 vs 予想時間）
        efficiency = 0
        if total_actual_time > 0 and total_estimated_time > 0:
            efficiency = (total_estimated_time / total_actual_time) * 100
        
        return {
            'total_tasks': len(tasks),
            'completed_tasks': len(completed_tasks),
            'completion_rate': round(completion_rate, 1),
            'total_estimated_time': total_estimated_time,
            'total_actual_time': total_actual_time,
            'total_pomodoros': total_pomodoros,
            'efficiency': round(efficiency, 1),
            'average_task_time': round(total_actual_time / len(completed_tasks), 1) if completed_tasks else 0
        }
    
    def get_category_stats(self) -> Dict[str, Dict[str, int]]:
        """カテゴリ別統計を取得"""
        category_stats = {}
        
        for task in self.task_manager.tasks:
            category = task.category
            if category not in category_stats:
                category_stats[category] = {
                    'total': 0,
                    'completed': 0,
                    'in_progress': 0,
                    'overdue': 0
                }
            
            category_stats[category]['total'] += 1
            
            if task.completed:
                category_stats[category]['completed'] += 1
            elif task.is_overdue():
                category_stats[category]['overdue'] += 1
            else:
                category_stats[category]['in_progress'] += 1
        
        return category_stats
    
    def get_priority_stats(self) -> Dict[str, Dict[str, int]]:
        """優先度別統計を取得"""
        priority_stats = {'高': {'total': 0, 'completed': 0},
                         '中': {'total': 0, 'completed': 0},
                         '低': {'total': 0, 'completed': 0}}
        
        for task in self.task_manager.tasks:
            priority = task.priority
            priority_stats[priority]['total'] += 1
            if task.completed:
                priority_stats[priority]['completed'] += 1
        
        return priority_stats
    
    def get_weekly_progress(self) -> List[Dict[str, Any]]:
        """週別進捗を取得"""
        weekly_data = []
        today = datetime.now().date()
        
        for i in range(7):
            date = today - timedelta(days=6-i)
            day_tasks = [task for task in self.task_manager.tasks 
                        if datetime.fromisoformat(task.created_at).date() == date]
            completed_tasks = [task for task in day_tasks if task.completed]
            
            weekly_data.append({
                'date': date.strftime('%m/%d'),
                'day': date.strftime('%a'),
                'total_tasks': len(day_tasks),
                'completed_tasks': len(completed_tasks),
                'completion_rate': (len(completed_tasks) / len(day_tasks)) * 100 if day_tasks else 0
            })
        
        return weekly_data
    
    def get_tag_usage(self) -> Dict[str, int]:
        """タグ使用統計を取得"""
        tag_count = {}
        
        for task in self.task_manager.tasks:
            for tag in task.tags:
                tag_count[tag] = tag_count.get(tag, 0) + 1
        
        # 使用頻度順にソート
        return dict(sorted(tag_count.items(), key=lambda x: x[1], reverse=True))
    
    def export_statistics(self, filename: str = None) -> str:
        """統計データをJSONファイルにエクスポート"""
        if filename is None:
            filename = f"task_statistics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        stats_data = {
            'generated_at': datetime.now().isoformat(),
            'productivity': self.get_productivity_stats(),
            'categories': self.get_category_stats(),
            'priorities': self.get_priority_stats(),
            'weekly_progress': self.get_weekly_progress(),
            'tag_usage': self.get_tag_usage()
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(stats_data, f, ensure_ascii=False, indent=2)
            return filename
        except Exception as e:
            raise Exception(f"統計データのエクスポートに失敗しました: {e}")
    
    def get_task_trends(self) -> Dict[str, Any]:
        """タスクトレンド分析"""
        if not self.task_manager.tasks:
            return {}
        
        # 最近の完了傾向
        recent_completed = len([task for task in self.task_manager.get_completed_tasks() 
                               if (datetime.now() - datetime.fromisoformat(task.updated_at)).days <= 7])
        
        # 平均完了時間
        completed_tasks = self.task_manager.get_completed_tasks()
        if completed_tasks:
            avg_completion_time = sum(
                (datetime.fromisoformat(task.updated_at) - datetime.fromisoformat(task.created_at)).days
                for task in completed_tasks
            ) / len(completed_tasks)
        else:
            avg_completion_time = 0
        
        return {
            'recent_completions': recent_completed,
            'average_completion_days': round(avg_completion_time, 1),
            'most_productive_day': self._get_most_productive_day(),
            'preferred_categories': list(self.get_category_stats().keys())[:3]
        }
    
    def _get_most_productive_day(self) -> str:
        """最も生産性の高い曜日を取得"""
        day_completions = {}
        
        for task in self.task_manager.get_completed_tasks():
            day = datetime.fromisoformat(task.updated_at).strftime('%A')
            day_completions[day] = day_completions.get(day, 0) + 1
        
        if day_completions:
            return max(day_completions, key=day_completions.get)
        return "データ不足"
