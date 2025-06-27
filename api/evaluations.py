"""
评估历史API路由
处理模型评估历史的查询操作
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any

from .dependencies import get_evaluation_history
from utils.model_evaluation_history import ModelEvaluationHistory

router = APIRouter(prefix="/api", tags=["evaluations"])

@router.get("/model-evaluations")
async def get_model_evaluations(
    evaluation_history: ModelEvaluationHistory = Depends(get_evaluation_history)
) -> Dict[str, Any]:
    """获取模型评估历史"""
    try:
        evaluations = evaluation_history.get_all_evaluations()
        return {
            "success": True,
            "data": evaluations,
            "message": "评估历史获取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取评估历史失败: {str(e)}") 