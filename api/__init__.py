"""
API模块
包含所有的路由定义和API处理逻辑
"""

from .models import router as models_router
from .tasks import router as tasks_router
from .datasets import router as datasets_router
from .evaluations import router as evaluations_router

__all__ = [
    'models_router',
    'tasks_router', 
    'datasets_router',
    'evaluations_router'
]
