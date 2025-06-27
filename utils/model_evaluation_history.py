#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型评估历史管理器
用于持久化保存和管理模型的评估历史记录
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import statistics

class ModelEvaluationHistory:
    """模型评估历史管理器"""
    
    def __init__(self, history_file: str = "data/model_evaluation_history.json"):
        self.history_file = history_file
        self.history_data = self._load_history()
    
    def _load_history(self) -> Dict[str, Any]:
        """加载历史数据"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {
                    "model_evaluations": {},
                    "last_updated": None,
                    "version": "1.0"
                }
        except Exception as e:
            return {
                "model_evaluations": {},
                "last_updated": None,
                "version": "1.0"
            }
    
    def _save_history(self):
        """保存历史数据"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
            
            self.history_data["last_updated"] = datetime.now().isoformat()
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            pass
    
    def update_model_evaluation(self, task_data: Dict[str, Any]):
        """更新模型评估记录"""
        try:
            model_name = task_data.get('target_model_name')
            evaluator_model = task_data.get('evaluator_model_name')
            task_id = task_data.get('task_id')
            created_at = task_data.get('created_at')
            results = task_data.get('results', {})
            
            if not model_name or not results:
                return
            
            # 解析评估结果
            evaluation_stats = self._parse_evaluation_results(results)
            if not evaluation_stats:
                return
            
            # 创建评估记录
            evaluation_record = {
                "task_id": task_id,
                "model_name": model_name,
                "evaluator_model": evaluator_model,
                "created_at": created_at,
                "average_score": evaluation_stats['average_score'],
                "total_questions": evaluation_stats['total_questions'],
                "fully_met_requirements": evaluation_stats['fully_met_requirements'],
                "partially_met_requirements": evaluation_stats['partially_met_requirements'],
                "unmet_requirements": evaluation_stats['unmet_requirements'],
                "total_tokens": evaluation_stats['total_tokens'],
                "total_duration_seconds": evaluation_stats['total_duration_seconds'],
                "total_duration_formatted": evaluation_stats['total_duration_formatted'],
                "task_exists": True,  # 任务是否还存在
                "last_updated": datetime.now().isoformat()
            }
            
            # 更新或添加模型记录（只保留最新的）
            current_record = self.history_data["model_evaluations"].get(model_name)
            
            # 如果是新模型或者更新的任务，则更新记录
            if (not current_record or 
                datetime.fromisoformat(created_at) > datetime.fromisoformat(current_record.get('created_at', '1970-01-01'))):
                
                self.history_data["model_evaluations"][model_name] = evaluation_record
                self._save_history()
        
            
        except Exception as e:
            pass
    
    def _parse_evaluation_results(self, results: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """解析评估结果"""
        try:
            results_list = results.get('results', [])
            if not results_list:
                return None
            
            total_questions = len(results_list)
            scores = []
            total_tokens = 0
            fully_met = 0
            partially_met = 0
            unmet = 0
            
            for result in results_list:
                # 获取评估分数
                evaluation = result.get('evaluation', {})
                scores_dict = evaluation.get('scores', {})
                
                if 'overall' in scores_dict:
                    scores.append(scores_dict['overall'])
                
                # 统计token使用
                total_tokens += result.get('tokens_used', 0)
                
                # 分析需求满足情况（基于overall分数）
                overall_score = scores_dict.get('overall', 0)
                if overall_score >= 80:
                    fully_met += 1
                elif overall_score >= 40:
                    partially_met += 1
                else:
                    unmet += 1
            
            # 计算平均分
            average_score = statistics.mean(scores) if scores else 0
            
            return {
                'average_score': round(average_score, 2),
                'total_questions': total_questions,
                'fully_met_requirements': fully_met,
                'partially_met_requirements': partially_met,
                'unmet_requirements': unmet,
                'total_tokens': total_tokens,
                'total_duration_seconds': results.get('total_duration_seconds', 0),
                'total_duration_formatted': results.get('summary', {}).get('total_duration_formatted', '未知')
            }
            
        except Exception as e:
            return None
    
    def mark_task_deleted(self, task_id: str):
        """标记任务已被删除"""
        try:
            for model_name, record in self.history_data["model_evaluations"].items():
                if record.get('task_id') == task_id:
                    record['task_exists'] = False
                    record['last_updated'] = datetime.now().isoformat()
                    self._save_history()

                    break
        except Exception as e:
            pass
    
    def get_all_evaluations(self) -> List[Dict[str, Any]]:
        """获取所有模型的评估记录"""
        try:
            evaluations = []
            for model_name, record in self.history_data["model_evaluations"].items():
                evaluations.append(record)
            
            # 按创建时间倒序排列
            evaluations.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            return evaluations
        except Exception as e:
            return []
    
    def get_model_evaluation(self, model_name: str) -> Optional[Dict[str, Any]]:
        """获取特定模型的评估记录"""
        return self.history_data["model_evaluations"].get(model_name)
    
    def clear_history(self):
        """清空历史记录"""
        self.history_data = {
            "model_evaluations": {},
            "last_updated": None,
            "version": "1.0"
        }
        self._save_history()
    
    def cleanup_old_evaluations(self, max_records: int = 5):
        """清理旧的评估记录，只保留最近的N个"""
        try:
            if len(self.history_data["model_evaluations"]) <= max_records:
                return  # 记录数量未超过限制，无需清理
            
            # 按创建时间排序，获取所有评估记录
            all_evaluations = []
            for model_name, record in self.history_data["model_evaluations"].items():
                all_evaluations.append((model_name, record))
            
            # 按创建时间倒序排序
            all_evaluations.sort(key=lambda x: x[1].get('created_at', ''), reverse=True)
            
            # 保留最近的max_records个记录
            evaluations_to_keep = all_evaluations[:max_records]
            evaluations_to_delete = all_evaluations[max_records:]
            
            # 重建评估历史数据
            new_evaluations = {}
            for model_name, record in evaluations_to_keep:
                new_evaluations[model_name] = record
            
            deleted_count = len(evaluations_to_delete)
            if deleted_count > 0:
                self.history_data["model_evaluations"] = new_evaluations
                self._save_history()
                print(f"自动清理评估历史，删除了 {deleted_count} 个旧记录，保留最近的 {max_records} 个记录")
            
        except Exception as e:
            print(f"清理评估历史失败: {e}")
 