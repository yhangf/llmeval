#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用评估器模块
处理非编程题的通用评估逻辑
"""

import asyncio
from typing import Dict, Any
from .evaluation_types import EvaluationScores, EvaluationResult
from .score_calculator import ScoreCalculator
from .text_analyzer import TextAnalyzer


class GeneralEvaluator:
    """通用评估器"""
    
    def __init__(self, prompt_loader):
        self.prompt_loader = prompt_loader
        self.score_calculator = ScoreCalculator()
        self.text_analyzer = TextAnalyzer()
    
    async def evaluate_general_response(self, question_text: str, model_answer: str, 
                                      reference: str, evaluator_model, logger=None) -> Dict[str, Any]:
        """使用评估模型评估通用回答"""
        print(f"🎯 使用通用评估模板")
        
        evaluation = {
            "scores": {},
            "feedback": "",
            "details": {},
            "evaluation_tokens": 0
        }
        
        try:
            # 并发评估三个维度
            accuracy_task = self.evaluate_accuracy_with_model(
                question_text, model_answer, reference, evaluator_model, logger
            )
            completeness_task = self.evaluate_completeness_with_model(
                question_text, model_answer, reference, evaluator_model, logger
            )
            clarity_task = self.evaluate_clarity_with_model(
                question_text, model_answer, evaluator_model, logger
            )
            
            # 等待所有评估完成
            accuracy_score, completeness_score, clarity_score = await asyncio.gather(
                accuracy_task, completeness_task, clarity_task
            )
            
            evaluation["scores"]["accuracy"] = accuracy_score["score"]
            evaluation["scores"]["completeness"] = completeness_score["score"]
            evaluation["scores"]["clarity"] = clarity_score["score"]
            
            # 计算总分
            scores = evaluation["scores"]
            evaluation["scores"]["overall"] = self.score_calculator.calculate_overall_score(
                EvaluationScores(
                    accuracy=scores["accuracy"],
                    completeness=scores["completeness"],
                    clarity=scores["clarity"]
                )
            )
            
            # 统计评估模型使用的token
            evaluation["evaluation_tokens"] = (
                accuracy_score["tokens"] + 
                completeness_score["tokens"] + 
                clarity_score["tokens"]
            )
            
            # 生成反馈
            evaluation["feedback"] = self._generate_feedback(evaluation["scores"], model_answer)
            
        except Exception as e:
            print(f"评估模型评估失败: {str(e)}")
            # 如果评估模型失败，回退到程序计算
            evaluation = await self._fallback_evaluation(model_answer, reference, question_text)
        
        return evaluation
    
    async def evaluate_accuracy_with_model(self, question: str, answer: str, 
                                         reference: str, evaluator_model, logger=None) -> Dict[str, Any]:
        """使用评估模型评估准确性"""
        prompt = self.prompt_loader.create_evaluation_prompt(
            question, answer, reference, "accuracy"
        )
        
        try:
            await asyncio.sleep(1)  # 避免API限制
            
            # 记录评估模型请求
            if logger:
                logger.log_model_request(evaluator_model.__class__.__name__, prompt, 
                                       {"max_tokens": 50, "temperature": 0.1})
            
            response = await evaluator_model.generate(prompt, max_tokens=50, temperature=0.1)
            
            if response.get('error'):
                raise Exception(response['error'])
            
            content = response.get('content', '').strip()
            print(f"准确性评估结果: {content}")
            
            # 记录评估模型回答
            if logger:
                logger.log_model_response(evaluator_model.__class__.__name__, response, "准确性评估")
            
            # 从回答中提取分数
            score = self.score_calculator.extract_score_from_response(content)
            
            return {
                "score": score,
                "tokens": response.get('tokens_used', 0),
                "raw_response": content
            }
            
        except Exception as e:
            print(f"准确性评估失败: {str(e)}")
            raise e
    
    async def evaluate_completeness_with_model(self, question: str, answer: str, 
                                             reference: str, evaluator_model, logger=None) -> Dict[str, Any]:
        """使用评估模型评估完整性"""
        prompt = self.prompt_loader.create_evaluation_prompt(
            question, answer, reference, "completeness"
        )
        
        try:
            await asyncio.sleep(1)  # 避免API限制
            
            # 记录评估模型请求
            if logger:
                logger.log_model_request(evaluator_model.__class__.__name__, prompt, 
                                       {"max_tokens": 50, "temperature": 0.1})
            
            response = await evaluator_model.generate(prompt, max_tokens=5000, temperature=0.4)
            
            if response.get('error'):
                raise Exception(response['error'])
            
            content = response.get('content', '').strip()
            print(f"完整性评估结果: {content}")
            
            # 记录评估模型回答
            if logger:
                logger.log_model_response(evaluator_model.__class__.__name__, response, "完整性评估")
            
            # 从回答中提取分数
            score = self.score_calculator.extract_score_from_response(content)
            
            return {
                "score": score,
                "tokens": response.get('tokens_used', 0),
                "raw_response": content
            }
            
        except Exception as e:
            print(f"完整性评估失败: {str(e)}")
            raise e
    
    async def evaluate_clarity_with_model(self, question: str, answer: str, 
                                        evaluator_model, logger=None) -> Dict[str, Any]:
        """使用评估模型评估清晰度"""
        prompt = self.prompt_loader.create_evaluation_prompt(
            question, answer, "", "clarity"
        )
        
        try:
            await asyncio.sleep(1)  # 避免API限制
            
            # 记录评估模型请求
            if logger:
                logger.log_model_request(evaluator_model.__class__.__name__, prompt, 
                                       {"max_tokens": 50, "temperature": 0.1})
            
            response = await evaluator_model.generate(prompt, max_tokens=50, temperature=0.1)
            
            if response.get('error'):
                raise Exception(response['error'])
            
            content = response.get('content', '').strip()
            print(f"清晰度评估结果: {content}")
            
            # 记录评估模型回答
            if logger:
                logger.log_model_response(evaluator_model.__class__.__name__, response, "清晰度评估")
            
            # 从回答中提取分数
            score = self.score_calculator.extract_score_from_response(content)
            
            return {
                "score": score,
                "tokens": response.get('tokens_used', 0),
                "raw_response": content
            }
            
        except Exception as e:
            print(f"清晰度评估失败: {str(e)}")
            raise e
    
    async def _fallback_evaluation(self, model_answer: str, reference: str, question_text: str) -> Dict[str, Any]:
        """备用评估方法"""
        question = {"content": question_text, "category": ""}
        
        accuracy = self._evaluate_accuracy_fallback(model_answer, reference, question)
        completeness = self._evaluate_completeness_fallback(model_answer, reference, question)
        clarity = self._evaluate_clarity_fallback(model_answer, question)
        
        scores = EvaluationScores(accuracy=accuracy, completeness=completeness, clarity=clarity)
        overall = self.score_calculator.calculate_overall_score(scores)
        
        return {
            "scores": {
                "accuracy": accuracy,
                "completeness": completeness,
                "clarity": clarity,
                "overall": overall
            },
            "feedback": "使用备用评估方法进行评估",
            "details": {
                "answer_length": len(model_answer),
                "reference_length": len(reference),
                "keyword_match": self.text_analyzer.calculate_keyword_match(model_answer, reference),
                "structure_score": self.text_analyzer.evaluate_structure(model_answer)
            },
            "evaluation_tokens": 0
        }
    
    def _evaluate_accuracy_fallback(self, model_answer: str, reference: str, question: Dict) -> float:
        """评估答案准确性（备用方法）"""
        if not model_answer or not reference:
            return 0.0
        
        # 关键词匹配
        keyword_score = self.text_analyzer.calculate_keyword_match(model_answer, reference)
        
        # 语义相似度（简化版）
        semantic_score = self.text_analyzer.calculate_semantic_similarity(model_answer, reference)
        
        # 特定领域评估
        domain_score = self.text_analyzer.evaluate_domain_specific(model_answer, question)
        
        return min(100.0, (keyword_score + semantic_score + domain_score) / 3)
    
    def _evaluate_completeness_fallback(self, model_answer: str, reference: str, question: Dict) -> float:
        """评估答案完整性（备用方法）"""
        if not model_answer:
            return 0.0
        
        # 长度比较
        length_ratio = min(1.0, len(model_answer) / max(len(reference), 100))
        length_score = length_ratio * 40
        
        # 要点覆盖
        coverage_score = self.text_analyzer.calculate_coverage(model_answer, reference) * 60
        
        return min(100.0, length_score + coverage_score)
    
    def _evaluate_clarity_fallback(self, model_answer: str, question: Dict) -> float:
        """评估答案清晰度（备用方法）"""
        if not model_answer:
            return 0.0
        
        score = 60.0  # 基础分
        
        # 结构化程度
        structure_score = self.text_analyzer.evaluate_structure(model_answer)
        score += structure_score * 0.4
        
        # 逻辑连贯性
        coherence_score = self.text_analyzer.evaluate_coherence(model_answer)
        score += coherence_score * 0.4
        
        # 专业度
        professionalism_score = self.text_analyzer.evaluate_professionalism(model_answer)
        score += professionalism_score * 0.2
        
        return min(100.0, score)
    
    def _generate_feedback(self, scores: Dict[str, float], answer: str) -> str:
        """生成评估反馈"""
        overall_score = scores.get('overall', 0)
        feedback_parts = []
        
        if overall_score >= 80:
            feedback_parts.append("优秀的回答！")
        elif overall_score >= 60:
            feedback_parts.append("回答质量良好。")
        else:
            feedback_parts.append("回答需要改进。")
        
        # 具体建议
        if scores.get('accuracy', 0) < 60:
            feedback_parts.append("准确性需要提升，建议核实关键信息。")
        
        if scores.get('completeness', 0) < 60:
            feedback_parts.append("回答不够完整，建议补充更多细节。")
        
        if scores.get('clarity', 0) < 60:
            feedback_parts.append("表达不够清晰，建议改进结构和逻辑。")
        
        return " ".join(feedback_parts) 