#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分数计算器模块
负责各种评估指标的计算
"""

import re
import statistics
from typing import Dict, List, Any, Optional
from .evaluation_types import EvaluationScores


class ScoreCalculator:
    """分数计算器"""
    
    def __init__(self):
        self.weights = {
            'accuracy': 0.4,
            'completeness': 0.3,
            'clarity': 0.3
        }
    
    def calculate_overall_score(self, scores: EvaluationScores) -> float:
        """计算总分"""
        return (
            scores.accuracy * self.weights['accuracy'] +
            scores.completeness * self.weights['completeness'] +
            scores.clarity * self.weights['clarity']
        )
    
    def calculate_programming_score(self, question_data: dict, eval_result: dict) -> float:
        """计算编程题总分"""
        question_type = question_data.get('type', 'standard_answer')
        
        if question_type == "standard_answer":
            # 有标准答案：根据子问题完成情况计算
            sub_scores = eval_result.get('sub_question_scores', [])
            weights = [sq['weight'] for sq in question_data.get('sub_questions', [])]
            
            if len(sub_scores) == len(weights):
                # 确保子问题分数在0-1范围内（如果是0-100范围，则除以100）
                normalized_scores = []
                for score in sub_scores:
                    if score > 1:  # 如果分数大于1，说明是0-100范围，需要归一化
                        normalized_scores.append(score / 100)
                    else:  # 如果分数在0-1范围，直接使用
                        normalized_scores.append(score)
                
                # 计算加权总分
                weighted_score = sum(score * weight for score, weight in zip(normalized_scores, weights))
                return weighted_score * 100  # 转换为0-100范围
            else:
                # 子问题数量不匹配，使用三维度分数计算
                accuracy = eval_result.get('accuracy', 0)
                completeness = eval_result.get('completeness', 0)
                clarity = eval_result.get('clarity', 0)
                return (accuracy + completeness + clarity) / 3
        else:
            # 无标准答案：无论是否完成需求，都基于三维度分数计算总分
            accuracy = eval_result.get('accuracy', 0)
            completeness = eval_result.get('completeness', 0)
            clarity = eval_result.get('clarity', 0)
            return (accuracy + completeness + clarity) / 3
    
    def extract_score_from_response(self, response: str) -> float:
        """从评估模型的回答中提取分数"""
        # 尝试多种模式提取分数
        patterns = [
            r'(\d+)分',  # "85分"
            r'(\d+)\.(\d+)分',  # "85.5分"
            r'分数[：:]\s*(\d+)',  # "分数：85"
            r'评分[：:]\s*(\d+)',  # "评分：85"
            r'(\d+)/100',  # "85/100"
            r'^(\d+)$',  # 纯数字
            r'(\d+)\.(\d+)',  # 小数
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, response)
            if matches:
                if isinstance(matches[0], tuple):  # 小数情况
                    score = float(f"{matches[0][0]}.{matches[0][1]}")
                else:
                    score = float(matches[0])
                
                # 确保分数在0-100范围内
                return max(0.0, min(100.0, score))
        
        # 如果没有找到数字，尝试从文本中推断
        response_lower = response.lower()
        if any(word in response_lower for word in ['优秀', 'excellent', '很好']):
            return 90.0
        elif any(word in response_lower for word in ['良好', 'good', '不错']):
            return 75.0
        elif any(word in response_lower for word in ['一般', 'average', '普通']):
            return 60.0
        elif any(word in response_lower for word in ['较差', 'poor', '不好']):
            return 40.0
        elif any(word in response_lower for word in ['很差', 'very poor', '糟糕']):
            return 20.0
        
        # 默认返回中等分数
        print(f"无法从回答中提取分数，使用默认值: {response}")
        return 50.0
    
    def calculate_summary_statistics(self, results: List[Dict]) -> Dict[str, Any]:
        """计算汇总统计"""
        if not results:
            return {}
        
        # 收集所有分数
        all_scores = {
            'accuracy': [],
            'completeness': [],
            'clarity': [],
            'overall': []
        }
        
        total_tokens = 0
        
        for result in results:
            eval_data = result.get('evaluation', {})
            scores = eval_data.get('scores', {})
            
            for metric in all_scores:
                if metric in scores:
                    all_scores[metric].append(scores[metric])
            
            total_tokens += result.get('tokens_used', 0)
        
        # 计算统计信息
        summary = {
            'total_questions': len(results),
            'total_tokens': total_tokens,
            'average_tokens_per_question': total_tokens / len(results) if results else 0,
            'score_statistics': {}
        }
        
        for metric, scores in all_scores.items():
            if scores:
                summary['score_statistics'][metric] = {
                    'mean': statistics.mean(scores),
                    'median': statistics.median(scores),
                    'std_dev': statistics.stdev(scores) if len(scores) > 1 else 0,
                    'min': min(scores),
                    'max': max(scores)
                }
        
        return summary
    
    def estimate_cost(self, total_tokens: int, model_name: str) -> float:
        """估算使用成本"""
        cost_per_token = {
            'gpt-4': 0.00003,
            'gpt-3.5-turbo': 0.000002,
            'claude': 0.000015,
            'default': 0.00001
        }
        
        # 根据模型名称匹配费率
        rate = cost_per_token['default']
        for model_key, model_rate in cost_per_token.items():
            if model_key in model_name.lower():
                rate = model_rate
                break
        
        return total_tokens * rate 