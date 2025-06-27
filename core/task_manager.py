#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务管理器
功能：管理评估任务的生命周期，状态跟踪和结果存储
作者：AI助手
创建时间：2024年
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import threading

class TaskManager:
    """评估任务管理器"""
    
    def __init__(self, data_dir: str = "data/tasks"):
        self.data_dir = data_dir
        self.tasks: Dict[str, Dict] = {}
        self.lock = threading.Lock()
        
        # 确保数据目录存在
        os.makedirs(data_dir, exist_ok=True)
        
        # 加载现有任务
        self.load_tasks()
        
        # 启动时自动清理旧任务
        self.cleanup_old_tasks(max_tasks=5)
    
    def create_task(self, task_id: str, task_info: Dict[str, Any]) -> bool:
        """创建新任务"""
        with self.lock:
            if task_id in self.tasks:
                return False
            
            self.tasks[task_id] = task_info.copy()
            self.save_task(task_id)
            
            # 自动清理旧任务，只保留最近的5个
            self.cleanup_old_tasks(max_tasks=5)
            
            return True
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务信息"""
        with self.lock:
            return self.tasks.get(task_id, {}).copy() if task_id in self.tasks else None
    
    def update_task_status(self, task_id: str, status: str) -> bool:
        """更新任务状态"""
        with self.lock:
            if task_id not in self.tasks:
                return False
            
            self.tasks[task_id]["status"] = status
            self.tasks[task_id]["updated_at"] = datetime.now().isoformat()
            self.save_task(task_id)
            
            # 如果任务完成或失败，触发清理
            if status in ['completed', 'failed']:
                self.cleanup_old_tasks(max_tasks=5)
            
            return True
    
    def update_task_progress(self, task_id: str, progress: int, current_question: int = None, total_questions: int = None) -> bool:
        """更新任务进度"""
        with self.lock:
            if task_id not in self.tasks:
                return False
            
            self.tasks[task_id]["progress"] = progress
            if current_question is not None:
                self.tasks[task_id]["current_question"] = current_question
            if total_questions is not None:
                self.tasks[task_id]["total_questions"] = total_questions
            self.tasks[task_id]["updated_at"] = datetime.now().isoformat()
            self.save_task(task_id)
            return True
    
    def update_task_results(self, task_id: str, results: Dict[str, Any]) -> bool:
        """更新任务结果"""
        with self.lock:
            if task_id not in self.tasks:
                return False
            
            self.tasks[task_id]["results"] = results
            self.tasks[task_id]["updated_at"] = datetime.now().isoformat()
            self.save_task(task_id)
            return True
    
    def update_task_error(self, task_id: str, error: str) -> bool:
        """更新任务错误信息"""
        with self.lock:
            if task_id not in self.tasks:
                return False
            
            self.tasks[task_id]["error"] = error
            self.tasks[task_id]["updated_at"] = datetime.now().isoformat()
            self.save_task(task_id)
            return True
    
    def list_tasks(self) -> List[Dict[str, Any]]:
        """获取所有任务列表"""
        with self.lock:
            return [task.copy() for task in self.tasks.values()]
    
    def delete_task(self, task_id: str) -> bool:
        """删除任务"""
        with self.lock:
            if task_id not in self.tasks:
                return False
            
            # 删除任务文件
            task_file = os.path.join(self.data_dir, f"{task_id}.json")
            if os.path.exists(task_file):
                os.remove(task_file)
            
            # 从内存中删除
            del self.tasks[task_id]
            return True
    
    def save_task(self, task_id: str):
        """保存任务到文件"""
        if task_id not in self.tasks:
            return
        
        task_file = os.path.join(self.data_dir, f"{task_id}.json")
        try:
            with open(task_file, 'w', encoding='utf-8') as f:
                json.dump(self.tasks[task_id], f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存任务失败 {task_id}: {e}")
    
    def load_tasks(self):
        """从文件加载任务"""
        if not os.path.exists(self.data_dir):
            return
        
        for filename in os.listdir(self.data_dir):
            if filename.endswith('.json'):
                task_id = filename[:-5]  # 移除.json后缀
                task_file = os.path.join(self.data_dir, filename)
                
                try:
                    with open(task_file, 'r', encoding='utf-8') as f:
                        task_data = json.load(f)
                        self.tasks[task_id] = task_data
                except Exception as e:
                    print(f"加载任务失败 {task_id}: {e}")
    
    def get_task_statistics(self) -> Dict[str, Any]:
        """获取任务统计信息"""
        with self.lock:
            stats = {
                "total_tasks": len(self.tasks),
                "status_count": {},
                "recent_tasks": []
            }
            
            # 统计各状态任务数量
            for task in self.tasks.values():
                status = task.get("status", "unknown")
                stats["status_count"][status] = stats["status_count"].get(status, 0) + 1
            
            # 获取最近的任务
            sorted_tasks = sorted(
                self.tasks.values(),
                key=lambda x: x.get("created_at", ""),
                reverse=True
            )
            stats["recent_tasks"] = sorted_tasks[:5]
            
            return stats
    
    def cleanup_old_tasks(self, max_tasks: int = 5):
        """清理旧任务，只保留最近的N个任务"""
        try:
            if len(self.tasks) <= max_tasks:
                return  # 任务数量未超过限制，无需清理
            
            # 按创建时间排序，获取需要删除的任务
            sorted_tasks = sorted(
                self.tasks.items(),
                key=lambda x: x[1].get("created_at", ""),
                reverse=True
            )
            
            # 保留最近的max_tasks个任务，删除其余的
            tasks_to_keep = sorted_tasks[:max_tasks]
            tasks_to_delete = sorted_tasks[max_tasks:]
            
            deleted_count = 0
            for task_id, task_info in tasks_to_delete:
                try:
                    # 删除任务文件
                    task_file = os.path.join(self.data_dir, f"{task_id}.json")
                    if os.path.exists(task_file):
                        os.remove(task_file)
                    
                    # 从内存中删除
                    if task_id in self.tasks:
                        del self.tasks[task_id]
                    
                    deleted_count += 1
                    print(f"自动清理旧任务: {task_id} (创建于: {task_info.get('created_at', '未知')})")
                    
                except Exception as e:
                    print(f"删除任务失败 {task_id}: {e}")
            
            if deleted_count > 0:
                print(f"自动清理完成，删除了 {deleted_count} 个旧任务，保留最近的 {max_tasks} 个任务")
            
        except Exception as e:
            print(f"自动清理任务失败: {e}") 