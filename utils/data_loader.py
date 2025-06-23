"""
数据加载器模块
负责加载和管理测试问题、标准答案等数据
支持多种数据格式和动态数据更新
作者: AI助手
创建时间: 2024
"""

import asyncio
import json
import os
from typing import Dict, List, Optional
import logging
from datetime import datetime
import glob


class DataLoader:
    """数据加载器主类"""
    
    def __init__(self, questions_dir: str = "data/questions", answers_dir: str = "data/answers"):
        self.questions_dir = questions_dir
        self.answers_dir = answers_dir
        self.questions: List[Dict] = []
        self.answers: Dict[str, Dict] = {}
        self.logger = logging.getLogger(__name__)
        
        # 确保数据目录存在
        os.makedirs(questions_dir, exist_ok=True)
        os.makedirs(answers_dir, exist_ok=True)
    
    async def load_questions(self, filename: str = None) -> List[Dict]:
        """加载问题，可以指定文件名或加载所有问题"""
        try:
            questions = []
            
            if filename:
                # 加载指定文件
                file_path = os.path.join(self.questions_dir, filename)
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"问题文件不存在: {filename}")
                question_files = [file_path]
            else:
                # 加载所有文件
                pattern = os.path.join(self.questions_dir, "*.json")
                question_files = glob.glob(pattern)
            
            for file_path in question_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                        # 如果是单个问题
                        if isinstance(data, dict) and "id" in data:
                            questions.append(self._validate_question(data))
                        
                        # 如果是问题列表
                        elif isinstance(data, list):
                            for question in data:
                                if isinstance(question, dict) and "id" in question:
                                    questions.append(self._validate_question(question))
                        
                        # 如果是包含questions字段的对象
                        elif isinstance(data, dict) and "questions" in data:
                            for question in data["questions"]:
                                if isinstance(question, dict) and "id" in question:
                                    questions.append(self._validate_question(question))
                
                except Exception as e:
                    self.logger.error(f"加载问题文件失败 {file_path}: {str(e)}")
            
            if not filename:
                # 只有在加载所有问题时才更新实例变量
                self.questions = questions
            
            self.logger.info(f"成功加载 {len(questions)} 个问题")
            return questions
            
        except Exception as e:
            self.logger.error(f"加载问题时发生错误: {str(e)}")
            return []
    
    def load_questions_sync(self, filename: str = None) -> List[Dict]:
        """同步版本的加载问题方法"""
        try:
            questions = []
            
            if filename:
                # 加载指定文件
                file_path = os.path.join(self.questions_dir, filename)
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"问题文件不存在: {filename}")
                question_files = [file_path]
            else:
                # 加载所有文件
                pattern = os.path.join(self.questions_dir, "*.json")
                question_files = glob.glob(pattern)
            
            for file_path in question_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                        # 处理不同的数据格式
                        if isinstance(data, dict) and "id" in data:
                            questions.append(data)
                        elif isinstance(data, list):
                            for question in data:
                                if isinstance(question, dict):
                                    questions.append(question)
                        elif isinstance(data, dict) and "questions" in data:
                            for question in data["questions"]:
                                if isinstance(question, dict):
                                    questions.append(question)
                
                except Exception as e:
                    self.logger.error(f"加载问题文件失败 {file_path}: {str(e)}")
            
            return questions
            
        except Exception as e:
            self.logger.error(f"加载问题时发生错误: {str(e)}")
            return []
    
    def _validate_question(self, question: Dict) -> Dict:
        """验证和标准化问题格式"""
        # 检查必需字段 - 支持多种字段名
        if "id" not in question:
            raise ValueError(f"问题缺少必需字段: id")
        
        # 支持多种问题内容字段名
        content = question.get("content") or question.get("question") or ""
        if not content:
            raise ValueError(f"问题缺少内容字段 (content 或 question)")
        
        # 标准化问题格式
        standardized = {
            "id": str(question["id"]),
            "content": content,
            "question": content,  # 保持兼容性
            "category": question.get("category", "general"),
            "difficulty": question.get("difficulty", "medium"),
            "type": question.get("type", "open_ended"),
            "context": question.get("context", ""),
            "metadata": question.get("metadata", {}),
            "created_at": question.get("created_at", datetime.now().isoformat()),
            "tags": question.get("tags", [])
        }
        
        return standardized
    
    async def load_answers(self, filename: str = None) -> List[Dict]:
        """加载标准答案，可以指定文件名或加载所有答案"""
        try:
            answers = []
            
            if filename:
                # 加载指定文件
                file_path = os.path.join(self.answers_dir, filename)
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"答案文件不存在: {filename}")
                answer_files = [file_path]
            else:
                # 加载所有文件
                pattern = os.path.join(self.answers_dir, "*.json")
                answer_files = glob.glob(pattern)
            
            for file_path in answer_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                        # 如果是单个答案
                        if isinstance(data, dict) and "question_id" in data:
                            answers.append(data)
                        
                        # 如果是答案列表
                        elif isinstance(data, list):
                            for answer in data:
                                if isinstance(answer, dict):
                                    answers.append(answer)
                        
                        # 如果是包含answers字段的对象
                        elif isinstance(data, dict) and "answers" in data:
                            for answer in data["answers"]:
                                if isinstance(answer, dict):
                                    answers.append(answer)
                
                except Exception as e:
                    self.logger.error(f"加载答案文件失败 {file_path}: {str(e)}")
            
            if not filename:
                # 只有在加载所有答案时才更新实例变量
                self.answers = {str(a.get("question_id", "")): a for a in answers if a.get("question_id")}
            
            self.logger.info(f"成功加载 {len(answers)} 个标准答案")
            return answers
            
        except Exception as e:
            self.logger.error(f"加载答案时发生错误: {str(e)}")
            return []
    
    def load_answers_sync(self, filename: str = None) -> List[Dict]:
        """同步版本的加载答案方法"""
        try:
            answers = []
            
            if filename:
                # 加载指定文件
                file_path = os.path.join(self.answers_dir, filename)
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"答案文件不存在: {filename}")
                answer_files = [file_path]
            else:
                # 加载所有文件
                pattern = os.path.join(self.answers_dir, "*.json")
                answer_files = glob.glob(pattern)
            
            for file_path in answer_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                        # 处理不同的数据格式
                        if isinstance(data, dict) and "question_id" in data:
                            answers.append(data)
                        elif isinstance(data, list):
                            for answer in data:
                                if isinstance(answer, dict):
                                    answers.append(answer)
                        elif isinstance(data, dict) and "answers" in data:
                            for answer in data["answers"]:
                                if isinstance(answer, dict):
                                    answers.append(answer)
                
                except Exception as e:
                    self.logger.error(f"加载答案文件失败 {file_path}: {str(e)}")
            
            return answers
            
        except Exception as e:
            self.logger.error(f"加载答案时发生错误: {str(e)}")
            return []
    
    def _validate_answer(self, answer: Dict) -> Dict:
        """验证和标准化答案格式"""
        # 检查必需字段
        if "question_id" not in answer:
            raise ValueError(f"答案缺少必需字段: question_id")
        
        # 支持多种答案内容字段名
        content = answer.get("content") or answer.get("answer") or ""
        if not content:
            raise ValueError(f"答案缺少内容字段 (content 或 answer)")
        
        # 标准化答案格式
        standardized = {
            "question_id": str(answer["question_id"]),
            "content": content,
            "answer": content,  # 保持兼容性
            "explanation": answer.get("explanation", ""),
            "key_points": answer.get("key_points", []),
            "scoring_criteria": answer.get("scoring_criteria", {}),
            "alternative_answers": answer.get("alternative_answers", []),
            "metadata": answer.get("metadata", {}),
            "created_at": answer.get("created_at", datetime.now().isoformat())
        }
        
        return standardized
    
    async def get_questions(self, category: str = None, difficulty: str = None, limit: int = None) -> List[Dict]:
        """获取问题列表，支持筛选"""
        filtered_questions = self.questions.copy()
        
        # 按分类筛选
        if category:
            filtered_questions = [q for q in filtered_questions if q.get("category") == category]
        
        # 按难度筛选
        if difficulty:
            filtered_questions = [q for q in filtered_questions if q.get("difficulty") == difficulty]
        
        # 限制数量
        if limit and limit > 0:
            filtered_questions = filtered_questions[:limit]
        
        return filtered_questions
    
    async def get_question_by_id(self, question_id: str) -> Optional[Dict]:
        """根据ID获取特定问题"""
        for question in self.questions:
            if question["id"] == question_id:
                return question
        return None
    
    async def get_answer_by_question_id(self, question_id: str) -> Optional[Dict]:
        """根据问题ID获取标准答案"""
        return self.answers.get(question_id)
    
    async def add_question(self, question: Dict) -> bool:
        """添加新问题"""
        try:
            validated_question = self._validate_question(question)
            
            # 检查ID是否已存在
            if any(q["id"] == validated_question["id"] for q in self.questions):
                raise ValueError(f"问题ID {validated_question['id']} 已存在")
            
            self.questions.append(validated_question)
            
            # 保存到文件
            await self._save_question(validated_question)
            
            self.logger.info(f"成功添加问题: {validated_question['id']}")
            return True
            
        except Exception as e:
            self.logger.error(f"添加问题失败: {str(e)}")
            return False
    
    async def _save_question(self, question: Dict):
        """保存问题到文件"""
        filename = f"question_{question['id']}.json"
        filepath = os.path.join(self.questions_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(question, f, indent=2, ensure_ascii=False)
    
    async def add_answer(self, answer: Dict) -> bool:
        """添加新答案"""
        try:
            validated_answer = self._validate_answer(answer)
            
            self.answers[validated_answer["question_id"]] = validated_answer
            
            # 保存到文件
            await self._save_answer(validated_answer)
            
            self.logger.info(f"成功添加答案: {validated_answer['question_id']}")
            return True
            
        except Exception as e:
            self.logger.error(f"添加答案失败: {str(e)}")
            return False
    
    async def _save_answer(self, answer: Dict):
        """保存答案到文件"""
        filename = f"answer_{answer['question_id']}.json"
        filepath = os.path.join(self.answers_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(answer, f, indent=2, ensure_ascii=False)
    
    async def get_categories(self) -> List[str]:
        """获取所有问题分类"""
        categories = set()
        for question in self.questions:
            categories.add(question.get("category", "general"))
        return sorted(list(categories))
    
    async def get_difficulties(self) -> List[str]:
        """获取所有难度级别"""
        difficulties = set()
        for question in self.questions:
            difficulties.add(question.get("difficulty", "medium"))
        return sorted(list(difficulties))
    
    async def get_statistics(self) -> Dict:
        """获取数据统计信息"""
        try:
            categories = await self.get_categories()
            difficulties = await self.get_difficulties()
            
            category_counts = {}
            difficulty_counts = {}
            
            for question in self.questions:
                category = question.get("category", "general")
                difficulty = question.get("difficulty", "medium")
                
                category_counts[category] = category_counts.get(category, 0) + 1
                difficulty_counts[difficulty] = difficulty_counts.get(difficulty, 0) + 1
            
            return {
                "total_questions": len(self.questions),
                "total_answers": len(self.answers),
                "coverage_rate": len(self.answers) / len(self.questions) if self.questions else 0,
                "categories": categories,
                "difficulties": difficulties,
                "category_distribution": category_counts,
                "difficulty_distribution": difficulty_counts
            }
            
        except Exception as e:
            self.logger.error(f"获取统计信息失败: {str(e)}")
            return {}
    
    async def refresh_data(self):
        """刷新数据（重新加载）"""
        await self.load_questions()
        await self.load_answers()
        self.logger.info("数据已刷新")
    
    async def export_data(self, export_path: str):
        """导出数据"""
        try:
            export_data = {
                "questions": self.questions,
                "answers": list(self.answers.values()),
                "exported_at": datetime.now().isoformat(),
                "statistics": await self.get_statistics()
            }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"数据已导出到: {export_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"导出数据失败: {str(e)}")
            return False 