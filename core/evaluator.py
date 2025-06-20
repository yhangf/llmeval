#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
评估引擎 - 重构版本
功能：执行模型评估，计算各种指标和分数
作者：AI助手
创建时间：2024年
"""

import asyncio
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime

from .evaluation.evaluation_types import QuestionData, ModelResponse, ReferenceAnswer
from .evaluation.programming_evaluator import ProgrammingEvaluator
from .evaluation.general_evaluator import GeneralEvaluator
from .evaluation.score_calculator import ScoreCalculator
from .evaluation.logger import EvaluationLogger


class Evaluator:
    """模型评估引擎 - 重构版本"""
    
    def __init__(self, model_manager, prompt_loader):
        self.model_manager = model_manager
        self.prompt_loader = prompt_loader
        self.programming_evaluator = ProgrammingEvaluator(prompt_loader)
        self.general_evaluator = GeneralEvaluator(prompt_loader)
        self.score_calculator = ScoreCalculator()
        self.logger = EvaluationLogger()
        
    async def evaluate_model(self, target_model_name: str, evaluator_model_name: str, 
                           questions: List[Dict], answers: List[Dict], 
                           config: Dict[str, Any] = None,
                           progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """评估单个模型"""
        # 获取待评估模型和评估模型
        target_model = self.model_manager.get_model(target_model_name)
        evaluator_model = self.model_manager.get_model(evaluator_model_name)
        
        if not target_model:
            raise ValueError(f"待评估模型 {target_model_name} 不存在")
        if not evaluator_model:
            raise ValueError(f"评估模型 {evaluator_model_name} 不存在")
        
        config = config or {}
        results = self._initialize_results(target_model_name, evaluator_model_name, len(questions))
        
        # 启动日志会话
        dataset_name = getattr(self.prompt_loader, '_current_dataset_file', 'unknown')
        if dataset_name and dataset_name != 'unknown':
            # 提取数据集文件名
            dataset_name = dataset_name.split('/')[-1].replace('.json', '')
        log_file = self.logger.start_evaluation_session(target_model_name, evaluator_model_name, dataset_name)
        results["log_file"] = log_file
        
        # 创建答案映射
        answer_map = self._create_answer_mapping(answers)
        
        # 逐一评估问题
        for i, question in enumerate(questions):
            # 获取问题ID和参考答案
            question_id = question.get('id') or question.get('question_id') or (i+1)
            reference_answer = self._get_reference_answer(question_id, question, answer_map)
            
            # 记录问题开始
            question_text = question.get('content') or question.get('question', '')
            self.logger.log_question_start(question_id, question_text, question)
            
            # 计算当前问题的基础进度（每个问题占总进度的一部分）
            question_base_progress = int((i / len(questions)) * 100)  # 30%-90%
            question_progress_range = 100 / len(questions)  # 每个问题占的进度范围
            
            # 更新进度 - 生成回答阶段（当前问题的前50%）
            generation_progress = int(question_base_progress + question_progress_range * 0.5)
            if progress_callback:
                progress_callback(generation_progress, i + 1, len(questions))
            self.logger.log_progress(i + 1, len(questions), "生成回答")
            
            # 生成模型回答
            model_response = await self._generate_model_response(
                question, target_model, config, i
            )
            
            # 更新进度 - 评估回答阶段（当前问题的后50%）
            evaluation_progress = int(question_base_progress + question_progress_range)
            if progress_callback:
                progress_callback(evaluation_progress, i + 1, len(questions))
            self.logger.log_progress(i + 1, len(questions), "评估回答")
            
            # 评估回答
            evaluation = await self.evaluate_response(
                question, model_response, reference_answer, evaluator_model
            )
            
            # 记录评估结果
            self.logger.log_evaluation_result(question_id, evaluation)
            
            # 构建结果项
            result_item = self._build_result_item(
                question_id, question, model_response, reference_answer, evaluation
            )
            
            results["results"].append(result_item)
            results["total_tokens"] += result_item["tokens_used"]
            
            # 更新进度 - 完成当前问题
            final_progress = 30 + int((i + 1) / len(questions) * 60)  # 30%-90%
            if progress_callback:
                progress_callback(final_progress)
        
        # 完成评估
        results["summary"] = self.score_calculator.calculate_summary_statistics(results["results"])
        results["total_cost"] = self.score_calculator.estimate_cost(results["total_tokens"], target_model_name)
        results["end_time"] = datetime.now().isoformat()
        
        # 记录会话总结并结束
        self.logger.log_session_summary(results["summary"])
        self.logger.log_session_end()
        
        return results
    
    async def evaluate_response(self, question: Dict, model_response: Dict, 
                              reference_answer: Dict, evaluator_model) -> Dict[str, Any]:
        """评估单个回答"""
        # 如果模型生成失败，返回零分
        if model_response.get('error'):
            return self._create_error_evaluation(model_response['error'])
        
        model_answer = model_response.get('content', '')
        reference = self._extract_reference_content(reference_answer)
        question_text = question.get('content') or question.get('question', '')
        
        # 判断是否使用编程评估
        if self.programming_evaluator.should_use_programming_evaluation(question, reference_answer):
            return await self._evaluate_programming_response(
                question, model_answer, reference, reference_answer, evaluator_model
            )
        else:
            return await self._evaluate_general_response(
                question_text, model_answer, reference, evaluator_model
            )
    
    async def _evaluate_programming_response(self, question: Dict, model_answer: str,
                                           reference: str, reference_answer: Dict, 
                                           evaluator_model) -> Dict[str, Any]:
        """评估编程类型的回答"""
        print(f"检测到编程类型问题，使用专门的编程评估...")
        print(f"问题类型: {question.get('type')}")
        print(f"是否有标准答案: {reference_answer.get('standard_answer') is not None}")
        print(f"子问题数量: {len(question.get('sub_questions', []))}")
        
        try:
            # 提取答案部分
            extracted_answer = self.programming_evaluator.extract_answer_from_response(model_answer)
            
            # 获取标准答案
            standard_answer = reference_answer.get('standard_answer', reference)
            
            # 使用编程评估方法
            programming_eval = await self.programming_evaluator.evaluate_programming_response(
                question, extracted_answer, standard_answer, evaluator_model, self.logger
            )
            
            # 添加编程评估特有的字段
            evaluation = {
                "scores": programming_eval["scores"],
                "feedback": programming_eval["feedback"],
                "evaluation_tokens": programming_eval["tokens_used"],
                "requirement_completed": programming_eval.get("requirement_completed", False),
                "sub_question_scores": programming_eval.get("sub_question_scores", []),
                "details": {
                    "answer_length": len(model_answer),
                    "reference_length": len(reference),
                    "evaluation_type": "programming"
                }
            }
            
            return evaluation
            
        except Exception as e:
            print(f"编程评估失败，回退到通用评估: {str(e)}")
            # 回退到通用评估
            return await self._evaluate_general_response(
                question.get('content', ''), model_answer, reference, evaluator_model
            )
    
    async def _evaluate_general_response(self, question_text: str, model_answer: str,
                                       reference: str, evaluator_model) -> Dict[str, Any]:
        """评估通用类型的回答"""
        print(f"使用通用评估模型评估回答...")
        
        evaluation = await self.general_evaluator.evaluate_general_response(
            question_text, model_answer, reference, evaluator_model, self.logger
        )
        
        # 添加详细分析
        evaluation["details"].update({
            "answer_length": len(model_answer),
            "reference_length": len(reference),
            "evaluation_type": "general"
        })
        
        return evaluation
    
    def _initialize_results(self, target_model_name: str, evaluator_model_name: str, 
                          questions_count: int) -> Dict[str, Any]:
        """初始化结果结构"""
        return {
            "target_model_name": target_model_name,
            "evaluator_model_name": evaluator_model_name,
            "start_time": datetime.now().isoformat(),
            "questions_count": questions_count,
            "results": [],
            "summary": {},
            "total_tokens": 0,
            "total_cost": 0.0
        }
    
    def _create_answer_mapping(self, answers: List[Dict]) -> Dict[Any, Dict]:
        """创建答案映射"""
        answer_map = {}
        for i, ans in enumerate(answers):
            # 尝试多种ID字段
            question_id = ans.get('question_id') or ans.get('id') or str(i+1)
            answer_map[question_id] = ans
            # 同时添加字符串和数字版本的ID
            if isinstance(question_id, int):
                answer_map[str(question_id)] = ans
            elif isinstance(question_id, str) and question_id.isdigit():
                answer_map[int(question_id)] = ans
        return answer_map
    
    def _get_reference_answer(self, question_id: Any, question: Dict, 
                            answer_map: Dict[Any, Dict]) -> Dict:
        """获取参考答案"""
        reference_answer = answer_map.get(question_id)
        
        # 如果没找到，尝试其他格式
        if not reference_answer:
            if isinstance(question_id, int):
                reference_answer = answer_map.get(str(question_id))
            elif isinstance(question_id, str) and question_id.isdigit():
                reference_answer = answer_map.get(int(question_id))
        
        # 对于没有标准答案的编程题，创建虚拟答案对象
        if not reference_answer:
            question_type = question.get('type', '')
            if question_type == 'no_standard_answer':
                print(f"问题 {question_id} 是无标准答案类型，创建虚拟答案对象")
                reference_answer = {
                    'question_id': question_id,
                    'type': 'no_standard_answer',
                    'content': ''
                }
            else:
                print(f"警告: 问题 {question_id} 没有对应的参考答案")
                reference_answer = {
                    'question_id': question_id,
                    'type': 'missing',
                    'content': ''
                }
        
        return reference_answer
    
    async def _generate_model_response(self, question: Dict, target_model, 
                                     config: Dict, question_index: int) -> Dict:
        """生成模型回答"""
        question_id = question.get('id', question_index + 1)
        question_text = question.get('content') or question.get('question', '')
        
        print(f"正在为问题 {question_id} 生成回答")
        print(f"问题内容: {question_text[:100]}...")
        
        # 检查是否使用结构化提示
        use_structured_prompt = (hasattr(self.prompt_loader, '_current_dataset_file') and 
                               self.prompt_loader._current_dataset_file and 
                               'mixed' in self.prompt_loader._current_dataset_file.lower())
        
        if use_structured_prompt:
            structured_prompt = self.prompt_loader.create_model_prompt_with_answer_format(question)
            print(f"使用结构化提示格式")
        else:
            structured_prompt = question_text
        
        # 添加请求间隔，避免API限制
        if question_index > 0:
            print(f"等待2秒后继续下一个请求...")
            await asyncio.sleep(2)
        
        try:
            # 记录模型请求
            self.logger.log_model_request(target_model.__class__.__name__, structured_prompt, config)
            
            model_response = await target_model.generate(structured_prompt, **config)
            
            # 记录模型回答
            self.logger.log_model_response(target_model.__class__.__name__, model_response, "待评估模型回答")
            
            print(f"待评估模型回答: {model_response}")
        except Exception as e:
            print(f"待评估模型生成失败: {str(e)}")
            model_response = {
                'content': f'生成失败: {str(e)}',
                'tokens_used': 0,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            
            # 记录错误
            self.logger.log_error(f"待评估模型生成失败", e)
        
        return model_response
    
    def _extract_reference_content(self, reference_answer: Dict) -> str:
        """提取参考答案内容"""
        return (reference_answer.get('standard_answer') or 
                reference_answer.get('answer') or 
                reference_answer.get('content', ''))
    
    def _create_error_evaluation(self, error_message: str) -> Dict[str, Any]:
        """创建错误评估结果"""
        return {
            "scores": {
                "accuracy": 0,
                "completeness": 0,
                "clarity": 0,
                "overall": 0
            },
            "feedback": f"模型回答生成失败: {error_message}",
            "details": {},
            "evaluation_tokens": 0
        }
    
    def _build_result_item(self, question_id: Any, question: Dict, 
                         model_response: Dict, reference_answer: Dict, 
                         evaluation: Dict) -> Dict[str, Any]:
        """构建结果项"""
        # 获取显示用的参考答案
        display_reference = ""
        if reference_answer.get('type') == 'no_standard_answer':
            display_reference = "无标准答案"
        elif reference_answer.get('type') == 'missing':
            display_reference = "未找到参考答案"
        else:
            display_reference = self._extract_reference_content(reference_answer)
            if not display_reference:
                display_reference = "未找到参考答案内容"
        
        return {
            "question_id": question_id,
            "question": question.get('content') or question.get('question', ''),
            "model_response": model_response['content'],
            "reference_answer": display_reference,
            "evaluation": evaluation,
            "tokens_used": model_response.get('tokens_used', 0) + evaluation.get('evaluation_tokens', 0),
            "timestamp": model_response.get('timestamp')
        } 