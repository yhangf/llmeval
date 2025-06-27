"""
API数据模型定义
包含所有API接口使用的Pydantic模型
"""

from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class TaskCreateRequest(BaseModel):
    """创建任务请求模型"""
    target_model_name: str  # 待评估模型
    evaluator_model_name: str  # 评估模型
    question_file: str = "sample_questions.json"
    config: Optional[Dict[str, Any]] = None

class ModelConfig(BaseModel):
    """模型配置模型"""
    name: str
    provider: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model_id: str
    max_tokens: int = 4000
    temperature: float = 0.7

class APIResponse(BaseModel):
    """通用API响应模型"""
    success: bool
    message: str
    data: Optional[Any] = None

class ErrorResponse(BaseModel):
    """错误响应模型"""
    success: bool = False
    message: str
    detail: Optional[str] = None 