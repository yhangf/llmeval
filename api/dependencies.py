"""
API依赖注入模块
提供共享的组件实例和依赖注入函数
"""

from models.model_manager import ModelManager
from core.evaluator import Evaluator
from core.task_manager import TaskManager
from utils.data_loader import DataLoader
from utils.prompt_loader import PromptLoader
from utils.model_evaluation_history import ModelEvaluationHistory

# 全局组件实例
_model_manager = None
_task_manager = None
_data_loader = None
_prompt_loader = None
_evaluator = None
_evaluation_history = None

def init_dependencies():
    """初始化所有依赖组件"""
    global _model_manager, _task_manager, _data_loader, _prompt_loader, _evaluator, _evaluation_history
    
    _model_manager = ModelManager()
    _task_manager = TaskManager()
    _data_loader = DataLoader()
    _prompt_loader = PromptLoader()
    _evaluator = Evaluator(_model_manager, _prompt_loader)
    _evaluation_history = ModelEvaluationHistory()

def get_model_manager() -> ModelManager:
    """获取模型管理器实例"""
    if _model_manager is None:
        raise RuntimeError("Dependencies not initialized. Call init_dependencies() first.")
    return _model_manager

def get_task_manager() -> TaskManager:
    """获取任务管理器实例"""
    if _task_manager is None:
        raise RuntimeError("Dependencies not initialized. Call init_dependencies() first.")
    return _task_manager

def get_data_loader() -> DataLoader:
    """获取数据加载器实例"""
    if _data_loader is None:
        raise RuntimeError("Dependencies not initialized. Call init_dependencies() first.")
    return _data_loader

def get_prompt_loader() -> PromptLoader:
    """获取提示加载器实例"""
    if _prompt_loader is None:
        raise RuntimeError("Dependencies not initialized. Call init_dependencies() first.")
    return _prompt_loader

def get_evaluator() -> Evaluator:
    """获取评估器实例"""
    if _evaluator is None:
        raise RuntimeError("Dependencies not initialized. Call init_dependencies() first.")
    return _evaluator

def get_evaluation_history() -> ModelEvaluationHistory:
    """获取评估历史实例"""
    if _evaluation_history is None:
        raise RuntimeError("Dependencies not initialized. Call init_dependencies() first.")
    return _evaluation_history 