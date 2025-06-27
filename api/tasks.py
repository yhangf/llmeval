"""
任务管理API路由
处理评估任务的创建、查询、删除等操作
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import Dict, Any
import uuid
from datetime import datetime

from .dependencies import get_task_manager, get_evaluator, get_evaluation_history
from .schemas import TaskCreateRequest
from core.task_manager import TaskManager
from core.evaluator import Evaluator
from utils.model_evaluation_history import ModelEvaluationHistory

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

@router.post("")
async def create_task(
    request: TaskCreateRequest, 
    background_tasks: BackgroundTasks,
    task_manager: TaskManager = Depends(get_task_manager)
) -> Dict[str, Any]:
    """创建新的评估任务"""
    try:
        print(f"=== 创建任务API被调用 ===")
        print(f"请求数据: {request}")
        
        # 生成任务ID
        task_id = str(uuid.uuid4())[:8]
        
        # 创建任务数据
        task_data = {
            "task_id": task_id,
            "target_model_name": request.target_model_name,
            "evaluator_model_name": request.evaluator_model_name,
            "question_file": request.question_file,
            "config": request.config or {},
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "progress": 0
        }
        
        print(f"创建的任务数据: {task_data}")
        
        # 保存任务
        success = task_manager.create_task(task_id, task_data)
        if not success:
            raise HTTPException(status_code=500, detail="创建任务失败")
        
        # 添加后台任务
        background_tasks.add_task(run_evaluation, task_id, request)
        
        return {
            "success": True,
            "data": {"task_id": task_id},
            "message": "任务创建成功，开始执行评估"
        }
        
    except Exception as e:
        print(f"创建任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建任务失败: {str(e)}")

@router.get("/{task_id}")
async def get_task(
    task_id: str,
    task_manager: TaskManager = Depends(get_task_manager)
) -> Dict[str, Any]:
    """获取指定任务的详细信息"""
    try:
        task = task_manager.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail=f"任务 {task_id} 不存在")
        
        return {
            "success": True,
            "data": task,
            "message": "任务信息获取成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取任务信息失败: {str(e)}")

@router.get("")
async def list_tasks(
    task_manager: TaskManager = Depends(get_task_manager)
) -> Dict[str, Any]:
    """获取所有任务列表"""
    try:
        tasks = task_manager.list_tasks()
        return {
            "success": True,
            "data": tasks,
            "message": "任务列表获取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取任务列表失败: {str(e)}")

@router.delete("/{task_id}")
async def delete_task(
    task_id: str,
    task_manager: TaskManager = Depends(get_task_manager)
) -> Dict[str, Any]:
    """删除指定任务"""
    try:
        success = task_manager.delete_task(task_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"任务 {task_id} 不存在或删除失败")
        
        return {
            "success": True,
            "message": f"任务 {task_id} 删除成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除任务失败: {str(e)}")

async def run_evaluation(task_id: str, request: TaskCreateRequest):
    """运行评估任务的后台函数"""
    from .dependencies import get_task_manager, get_evaluator, get_evaluation_history
    
    task_manager = get_task_manager()
    evaluator = get_evaluator()
    evaluation_history = get_evaluation_history()
    
    try:
        print(f"=== 开始执行任务 {task_id} ===")
        
        # 更新任务状态为运行中
        task_manager.update_task_status(task_id, "running")
        
        def progress_callback(progress, current_question=None, total_questions=None):
            """进度回调函数"""
            try:
                task_manager.update_task_progress(task_id, progress)
                if current_question and total_questions:
                    print(f"任务 {task_id} 进度: {progress}% ({current_question}/{total_questions})")
                else:
                    print(f"任务 {task_id} 进度: {progress}%")
            except Exception as e:
                print(f"更新进度失败: {e}")
        
        # 执行评估
        results = await evaluator.evaluate_model(
            target_model_name=request.target_model_name,
            evaluator_model_name=request.evaluator_model_name,
            question_file=request.question_file,
            config=request.config or {},
            progress_callback=progress_callback
        )
        
        print(f"任务 {task_id} 评估完成，结果: {type(results)}")
        
        # 更新任务结果
        task_manager.update_task_results(task_id, results)
        
        # 更新任务状态为完成
        task_manager.update_task_status(task_id, "completed")
        
        # 更新评估历史
        task_data = task_manager.get_task(task_id)
        if task_data:
            evaluation_history.update_model_evaluation(task_data)
        
        print(f"任务 {task_id} 执行成功")
        
    except Exception as e:
        print(f"任务 {task_id} 执行失败: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # 更新任务状态为失败
        task_manager.update_task_status(task_id, "failed", str(e))
        
        print(f"任务 {task_id} 状态已更新为失败") 