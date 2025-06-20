#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
编程评估器模块
专门处理编程题的评估逻辑
"""

import asyncio
import json
import re
from typing import Dict, Any
from .evaluation_types import EvaluationResult, EvaluationScores, QuestionType
from .score_calculator import ScoreCalculator


class ProgrammingEvaluator:
    """编程评估器"""
    
    def __init__(self, prompt_loader):
        self.prompt_loader = prompt_loader
        self.score_calculator = ScoreCalculator()
    
    def should_use_programming_evaluation(self, question: Dict, reference_answer: Dict) -> bool:
        """判断是否应该使用编程评估"""
        question_category = question.get('category', '').lower()
        question_type = question.get('type', '')
        
        # 判断是否为编程类型问题
        is_programming = (
            question_category == '编程' or 
            question_category == '编程实践' or
            '编程' in question_category
        )
        
        # 如果是编程类型问题，应该优先使用编程评估
        should_use_programming_eval = is_programming
        
        return should_use_programming_eval
    
    async def evaluate_programming_response(self, question_data: dict, model_answer: str,
                                          standard_answer: str, evaluator_model, logger=None) -> Dict[str, Any]:
        """使用评估模型评估编程题"""
        question_type = question_data.get('type', 'standard_answer')
        
        # 创建编程评估提示
        prompt = self.prompt_loader.create_programming_evaluation_prompt(
            question_data, model_answer, standard_answer, question_type
        )
        
        print(f"🎯 使用编程评估模板 - 问题ID: {question_data.get('id')}, 类型: {question_type}")
        
        try:
            await asyncio.sleep(1)  # 避免API限制
            
            # 记录评估模型请求
            if logger:
                logger.log_model_request(evaluator_model.__class__.__name__, prompt, 
                                       {"max_tokens": 500, "temperature": 0.1})
            
            response = await evaluator_model.generate(prompt, max_tokens=5000, temperature=0.1)
            
            if response.get('error'):
                raise Exception(response['error'])
            
            content = response.get('content', '').strip()
            print(f"编程题评估结果: {content}")
            
            # 记录评估模型回答
            if logger:
                logger.log_model_response(evaluator_model.__class__.__name__, response, "编程评估结果")
            
            # 解析JSON格式的评估结果
            try:
                eval_result = self._extract_json_from_text(content)
                if not eval_result:
                    # 如果没有找到JSON，使用默认解析
                    eval_result = self._parse_evaluation_response(content)
                
                # 计算总分
                total_score = self.score_calculator.calculate_programming_score(question_data, eval_result)
                
                return {
                    'scores': {
                        'accuracy': eval_result.get('accuracy', 0),
                        'completeness': eval_result.get('completeness', 0),
                        'clarity': eval_result.get('clarity', 0),
                        'overall': total_score
                    },
                    'requirement_completed': eval_result.get('requirement_completed', False),
                    'sub_question_scores': eval_result.get('sub_question_scores', []),
                    'feedback': eval_result.get('feedback', '无详细反馈'),
                    'tokens_used': response.get('usage', {}).get('total_tokens', 0)
                }
                
            except (json.JSONDecodeError, KeyError) as e:
                print(f"解析评估结果失败: {e}")
                print(f"原始评估内容: {content}")
                # 使用备用解析方法
                return self._parse_evaluation_response(content)
                
        except Exception as e:
            print(f"编程评估失败，回退到通用评估: {e}")
            # 这里不返回错误，而是抛出异常让上层处理
            raise e
    
    def extract_answer_from_response(self, model_answer: str) -> str:
        """从模型回答中提取答案部分"""
        # 首先尝试提取<answer>标签中的内容
        answer_match = re.search(r'<answer>(.*?)</answer>', model_answer, re.DOTALL)
        if answer_match:
            return answer_match.group(1).strip()
        
        # 如果没有answer标签，尝试提取model_answer标签中的内容
        code_match = re.search(r'<model_answer>(.*?)</model_answer>', model_answer, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()
        
        # 如果没有标签，使用全部内容
        return model_answer
    
    def _extract_json_from_text(self, text: str) -> Dict[str, Any]:
        """从文本中提取JSON对象"""
        # 方法1：寻找完整的JSON对象（支持嵌套）
        brace_count = 0
        start_idx = -1
        
        for i, char in enumerate(text):
            if char == '{':
                if brace_count == 0:
                    start_idx = i
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0 and start_idx != -1:
                    try:
                        json_str = text[start_idx:i+1]
                        return json.loads(json_str)
                    except json.JSONDecodeError:
                        continue
        
        # 方法2：使用更宽松的正则表达式
        patterns = [
            r'\{[^{}]*"requirement_completed"[^{}]*\}',  # 简单JSON
            r'\{.*?"requirement_completed".*?\}',       # 包含换行的JSON
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    continue
        
        return None
    
    def _parse_evaluation_response(self, response: str) -> Dict[str, Any]:
        """解析评估响应，提取分数和反馈"""
        # 尝试提取分数（支持多种格式）
        def extract_score(pattern, default=50):
            match = re.search(pattern, response)
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    return default
            return default
        
        accuracy = extract_score(r'准确性[：:]\s*(\d+)')
        completeness = extract_score(r'完整性[：:]\s*(\d+)')
        clarity = extract_score(r'清晰度[：:]\s*(\d+)')
        
        # 检查是否完成需求 - 增加更多关键词
        requirement_keywords = ['完成', 'true', '正确', '成功', '达成', '满足', '符合', '通过']
        not_requirement_keywords = ['未完成', 'false', '错误', '失败', '不符合', '不满足', '不通过']
        
        # 检查否定关键词
        has_negative = any(keyword in response.lower() for keyword in not_requirement_keywords)
        has_positive = any(keyword in response.lower() for keyword in requirement_keywords)
        
        # 如果有明确的否定，则未完成；否则根据积极关键词判断
        requirement_completed = has_positive and not has_negative
        
        # 尝试提取子问题分数
        sub_scores = []
        sub_pattern = r'子问题\s*(\d+)[：:]\s*(\d+)'
        sub_matches = re.findall(sub_pattern, response)
        for match in sub_matches:
            try:
                sub_scores.append(int(match[1]))
            except ValueError:
                continue
        
        return {
            'accuracy': accuracy,
            'completeness': completeness,
            'clarity': clarity,
            'requirement_completed': requirement_completed,
            'feedback': response,
            'sub_question_scores': sub_scores
        } 