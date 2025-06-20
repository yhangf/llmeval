#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
评估类型定义和数据结构
"""

from enum import Enum
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


class EvaluationType(Enum):
    """评估类型枚举"""
    ACCURACY = "accuracy"
    COMPLETENESS = "completeness" 
    CLARITY = "clarity"
    PROGRAMMING = "programming"
    GENERAL = "general"


class QuestionType(Enum):
    """问题类型枚举"""
    STANDARD_ANSWER = "standard_answer"
    NO_STANDARD_ANSWER = "no_standard_answer"
    GENERAL = "general"


@dataclass
class EvaluationScores:
    """评估分数数据结构"""
    accuracy: float = 0.0
    completeness: float = 0.0
    clarity: float = 0.0
    overall: float = 0.0


@dataclass
class EvaluationResult:
    """评估结果数据结构"""
    scores: EvaluationScores = field(default_factory=EvaluationScores)
    feedback: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    evaluation_tokens: int = 0
    requirement_completed: bool = False
    sub_question_scores: List[int] = field(default_factory=list)


@dataclass
class QuestionData:
    """问题数据结构"""
    id: Any
    content: str
    category: str = ""
    type: str = "general"
    difficulty: str = ""
    sub_questions: List[Dict[str, Any]] = field(default_factory=list)
    evaluation_prompt: str = ""


@dataclass
class ModelResponse:
    """模型回答数据结构"""
    content: str = ""
    tokens_used: int = 0
    error: Optional[str] = None
    timestamp: Optional[str] = None


@dataclass
class ReferenceAnswer:
    """参考答案数据结构"""
    question_id: Any = None
    standard_answer: Optional[str] = None
    answer: Optional[str] = None
    content: Optional[str] = None
    type: str = "general" 