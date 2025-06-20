#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大模型测评系统主应用
功能：FastAPI应用，提供模型测评的RESTful API接口
作者：AI助手
创建时间：2024年
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import os
import uuid
from datetime import datetime

from models.model_manager import ModelManager
from core.evaluator import Evaluator
from core.task_manager import TaskManager
from utils.data_loader import DataLoader
from utils.prompt_loader import PromptLoader

# 创建FastAPI应用实例
app = FastAPI(
    title="大模型测评系统",
    description="一个完整的大模型测评和评估系统",
    version="1.0.0"
)

# 静态文件和模板配置
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 全局组件初始化
model_manager = ModelManager()
task_manager = TaskManager()
data_loader = DataLoader()
prompt_loader = PromptLoader()
evaluator = Evaluator(model_manager, prompt_loader)

def get_matching_answer_file(question_file: str) -> str:
    """根据问题集文件名自动匹配对应的答案集文件"""
    # 定义问题集到答案集的映射关系
    question_to_answer_mapping = {
        "sample_questions.json": "sample_answers.json",
        "programming_questions.json": "programming_answers.json", 
        "programming_questions_mixed.json": "programming_answers_mixed.json"
    }
    
    # 直接映射
    if question_file in question_to_answer_mapping:
        return question_to_answer_mapping[question_file]
    
    # 基于文件名规则的自动匹配
    if question_file.startswith("programming_questions"):
        return question_file.replace("questions", "answers")
    elif question_file.endswith("_questions.json"):
        return question_file.replace("_questions.json", "_answers.json")
    elif "question" in question_file:
        return question_file.replace("question", "answer")
    else:
        # 默认返回sample答案集
        return "sample_answers.json"

# Pydantic模型定义
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
    max_tokens: int = 1000
    temperature: float = 0.7

@app.get("/")
async def home(request: Request):
    """主页路由"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/models")
async def get_models() -> Dict[str, Any]:
    """获取可用模型列表"""
    try:
        models = model_manager.list_models()
        return {
            "success": True,
            "data": models,
            "message": "模型列表获取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取模型列表失败: {str(e)}")

@app.post("/api/models")
async def add_model(config: ModelConfig) -> Dict[str, Any]:
    """添加新模型配置"""
    try:
        model_manager.add_model(
            name=config.name,
            provider=config.provider,
            api_key=config.api_key,
            base_url=config.base_url,
            model_id=config.model_id,
            max_tokens=config.max_tokens,
            temperature=config.temperature
        )
        return {
            "success": True,
            "message": f"模型 {config.name} 添加成功"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"添加模型失败: {str(e)}")

@app.get("/api/questions")
async def get_questions() -> Dict[str, Any]:
    """获取问题集列表"""
    try:
        questions_dir = "data/questions"
        if not os.path.exists(questions_dir):
            return {"success": True, "data": [], "message": "问题目录不存在"}
        
        files = [f for f in os.listdir(questions_dir) if f.endswith('.json')]
        question_sets = []
        
        for file in files:
            file_path = os.path.join(questions_dir, file)
            try:
                # 直接读取文件内容
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # 处理不同的数据格式
                questions = []
                if isinstance(data, list):
                    questions = data
                elif isinstance(data, dict):
                    if "questions" in data:
                        questions = data["questions"]
                    elif "id" in data and "question" in data:
                        questions = [data]
                
                # 确定数据集类型
                dataset_type = "通用"
                if "programming" in file.lower():
                    if "standard" in file.lower():
                        dataset_type = "编程(有标准答案)"
                    elif "no_standard" in file.lower():
                        dataset_type = "编程(无标准答案)"
                    else:
                        dataset_type = "编程"
                elif "sample" in file.lower():
                    dataset_type = "示例"
                
                question_sets.append({
                    "filename": file,
                    "name": file.replace('.json', '').replace('_', ' ').title(),
                    "type": dataset_type,
                    "count": len(questions),
                    "preview": questions[:3] if questions else []
                })
            except Exception as file_error:
                # 如果单个文件读取失败，记录错误但继续处理其他文件
                print(f"读取文件 {file} 失败: {str(file_error)}")
                question_sets.append({
                    "filename": file,
                    "count": 0,
                    "preview": [],
                    "error": str(file_error)
                })
        
        return {
            "success": True,
            "data": question_sets,
            "message": "问题集获取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取问题集失败: {str(e)}")

@app.get("/api/answers")
async def get_answers() -> Dict[str, Any]:
    """获取答案集列表"""
    try:
        answers_dir = "data/answers"
        if not os.path.exists(answers_dir):
            return {"success": True, "data": [], "message": "答案目录不存在"}
        
        files = [f for f in os.listdir(answers_dir) if f.endswith('.json')]
        answer_sets = []
        
        for file in files:
            file_path = os.path.join(answers_dir, file)
            try:
                # 直接读取文件内容
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # 处理不同的数据格式
                answers = []
                if isinstance(data, list):
                    answers = data
                elif isinstance(data, dict):
                    if "answers" in data:
                        answers = data["answers"]
                    elif "question_id" in data and "answer" in data:
                        answers = [data]
                
                # 确定数据集类型
                dataset_type = "通用"
                if "programming" in file.lower():
                    if "standard" in file.lower():
                        dataset_type = "编程(有标准答案)"
                    elif "no_standard" in file.lower():
                        dataset_type = "编程(无标准答案)"
                    else:
                        dataset_type = "编程"
                elif "sample" in file.lower():
                    dataset_type = "示例"
                
                answer_sets.append({
                    "filename": file,
                    "name": file.replace('.json', '').replace('_', ' ').title(),
                    "type": dataset_type,
                    "count": len(answers),
                    "preview": answers[:3] if answers else []
                })
            except Exception as file_error:
                # 如果单个文件读取失败，记录错误但继续处理其他文件
                print(f"读取答案文件 {file} 失败: {str(file_error)}")
                answer_sets.append({
                    "filename": file,
                    "count": 0,
                    "preview": [],
                    "error": str(file_error)
                })
        
        return {
            "success": True,
            "data": answer_sets,
            "message": "答案集获取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取答案集失败: {str(e)}")

@app.post("/api/tasks")
async def create_task(request: TaskCreateRequest, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """创建评估任务"""
    try:
        # 验证待评估模型是否存在
        if not model_manager.has_model(request.target_model_name):
            raise HTTPException(status_code=400, detail=f"待评估模型 {request.target_model_name} 不存在")
        
        # 验证评估模型是否存在
        if not model_manager.has_model(request.evaluator_model_name):
            raise HTTPException(status_code=400, detail=f"评估模型 {request.evaluator_model_name} 不存在")
        
        # 测试待评估模型是否可用
        print(f"测试待评估模型 {request.target_model_name} 是否可用...")
        test_result = await model_manager.test_model(request.target_model_name, "测试")
        if not test_result.get('success'):
            error_msg = test_result.get('error', '未知错误')
            print(f"待评估模型测试失败: {error_msg}")
            raise HTTPException(status_code=400, detail=f"待评估模型 {request.target_model_name} 不可用: {error_msg}")
        else:
            print(f"待评估模型 {request.target_model_name} 测试成功")
        
        # 测试评估模型是否可用
        print(f"测试评估模型 {request.evaluator_model_name} 是否可用...")
        test_result = await model_manager.test_model(request.evaluator_model_name, "测试")
        if not test_result.get('success'):
            error_msg = test_result.get('error', '未知错误')
            print(f"评估模型测试失败: {error_msg}")
            raise HTTPException(status_code=400, detail=f"评估模型 {request.evaluator_model_name} 不可用: {error_msg}")
        else:
            print(f"评估模型 {request.evaluator_model_name} 测试成功")
        
        # 自动匹配答案集
        answer_file = get_matching_answer_file(request.question_file)
        print(f"问题集: {request.question_file} -> 答案集: {answer_file}")
        
        # 生成任务ID
        task_id = str(uuid.uuid4())
        
        # 创建任务
        task_info = {
            "task_id": task_id,
            "target_model_name": request.target_model_name,
            "evaluator_model_name": request.evaluator_model_name,
            "question_file": request.question_file,
            "answer_file": answer_file,
            "config": request.config or {},
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "progress": 0,
            "results": None
        }
        
        task_manager.create_task(task_id, task_info)
        
        # 添加后台任务执行评估
        background_tasks.add_task(run_evaluation, task_id, request)
        
        return {
            "success": True,
            "data": {"task_id": task_id},
            "message": "任务创建成功，正在后台执行"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建任务失败: {str(e)}")

@app.get("/api/tasks/{task_id}")
async def get_task(task_id: str) -> Dict[str, Any]:
    """获取任务状态和结果"""
    try:
        print(f"获取任务详情: {task_id}")
        task_info = task_manager.get_task(task_id)
        if not task_info:
            print(f"任务不存在: {task_id}")
            raise HTTPException(status_code=404, detail="任务不存在")
        
        print(f"任务状态: {task_info.get('status')}")
        print(f"任务进度: {task_info.get('progress')}")
        
        # 检查结果数据
        if task_info.get('results'):
            results = task_info['results']
            print(f"结果类型: {type(results)}")
            if isinstance(results, dict):
                print(f"结果键: {list(results.keys())}")
                if 'results' in results:
                    print(f"详细结果数量: {len(results['results'])}")
                if 'summary' in results:
                    print(f"汇总信息: {results['summary'].keys() if isinstance(results['summary'], dict) else 'not dict'}")
        
        return {
            "success": True,
            "data": task_info,
            "message": "任务信息获取成功"
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取任务失败: {str(e)}")

@app.get("/api/tasks")
async def list_tasks() -> Dict[str, Any]:
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

@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: str) -> Dict[str, Any]:
    """删除任务"""
    try:
        success = task_manager.delete_task(task_id)
        if not success:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        return {
            "success": True,
            "message": "任务删除成功"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除任务失败: {str(e)}")



async def run_evaluation(task_id: str, request: TaskCreateRequest):
    """后台执行评估任务"""
    try:
        print(f"开始执行评估任务 {task_id}")
        
        # 更新任务状态
        task_manager.update_task_status(task_id, "running")
        task_manager.update_task_progress(task_id, 10)
        
        # 加载问题和答案
        print(f"加载问题文件: {request.question_file}")
        questions = await data_loader.load_questions(request.question_file)
        print(f"成功加载 {len(questions)} 个问题")
        
        # 获取匹配的答案文件
        answer_file = get_matching_answer_file(request.question_file)
        print(f"加载答案文件: {answer_file}")
        answers = await data_loader.load_answers(answer_file)
        print(f"成功加载 {len(answers)} 个答案")
        
        task_manager.update_task_progress(task_id, 30)
        
        # 验证数据
        if not questions:
            raise ValueError("问题列表为空")
        if not answers:
            raise ValueError("答案列表为空")
        
        print(f"开始使用待评估模型 {request.target_model_name} 和评估模型 {request.evaluator_model_name} 进行评估")
        
        # 设置当前数据集文件信息到提示加载器
        evaluator.prompt_loader._current_dataset_file = request.question_file
        
        # 执行评估
        def progress_callback(progress, current_question=None, total_questions=None):
            task_manager.update_task_progress(task_id, progress, current_question, total_questions)
        
        results = await evaluator.evaluate_model(
            target_model_name=request.target_model_name,
            evaluator_model_name=request.evaluator_model_name,
            questions=questions,
            answers=answers,
            config=request.config or {},
            progress_callback=progress_callback
        )
        
        print(f"评估完成，处理了 {len(results.get('results', []))} 个问题")
        print(f"结果结构: {list(results.keys())}")
        
        # 更新任务结果
        task_manager.update_task_results(task_id, results)
        task_manager.update_task_status(task_id, "completed")
        task_manager.update_task_progress(task_id, 100)
        
        # 验证结果是否正确保存
        saved_task = task_manager.get_task(task_id)
        if saved_task and saved_task.get('results'):
            print(f"结果已保存，类型: {type(saved_task['results'])}")
            if isinstance(saved_task['results'], dict):
                print(f"保存的结果键: {list(saved_task['results'].keys())}")
        else:
            print("警告: 结果保存可能失败")
        
        print(f"任务 {task_id} 执行成功")
        
    except Exception as e:
        # 更新任务为失败状态
        error_msg = str(e)
        print(f"任务 {task_id} 执行失败: {error_msg}")
        print(f"错误详情: {type(e).__name__}")
        
        task_manager.update_task_status(task_id, "failed")
        task_manager.update_task_error(task_id, error_msg)
        
        # 添加调试信息
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import uvicorn
    print("启动大模型测评系统...")
    
    # 显示加载的模型信息
    models = model_manager.list_models()
    print(f"已加载 {len(models)} 个模型:")
    for model in models:
        print(f"  - {model['name']} ({model['type']}, {model['model_id']})")
    
    if not models:
        print("警告: 没有加载任何模型！请检查config/models.json文件。")
    
    print("访问地址: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000) 