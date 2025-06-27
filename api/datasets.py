"""
数据集管理API路由
处理问题集和答案集的查询操作
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import os
import json

from .dependencies import get_data_loader
from utils.data_loader import DataLoader

router = APIRouter(prefix="/api", tags=["datasets"])

def get_matching_answer_file(question_file: str) -> str:
    """根据问题集文件名自动匹配对应的答案集文件"""
    question_to_answer_mapping = {
        "sample_questions.json": "sample_answers.json",
        "programming_questions.json": "programming_answers.json", 
        "programming_questions_mixed.json": "programming_answers_mixed.json"
    }
    
    if question_file in question_to_answer_mapping:
        return question_to_answer_mapping[question_file]
    
    if question_file.startswith("programming_questions"):
        return question_file.replace("questions", "answers")
    elif question_file.endswith("_questions.json"):
        return question_file.replace("_questions.json", "_answers.json")
    elif "question" in question_file:
        return question_file.replace("question", "answer")
    else:
        return "sample_answers.json"

@router.get("/questions")
async def get_questions(data_loader: DataLoader = Depends(get_data_loader)) -> Dict[str, Any]:
    """获取问题集列表"""
    try:
        questions_dir = "data/questions"
        if not os.path.exists(questions_dir):
            return {"success": True, "data": [], "message": "问题目录不存在"}
        
        files = []
        for filename in os.listdir(questions_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(questions_dir, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                    question_count = len(data) if isinstance(data, list) else len(data.get('questions', []))
                    answer_file = get_matching_answer_file(filename)
                    answer_path = os.path.join("data/answers", answer_file)
                    has_answers = os.path.exists(answer_path)
                    
                    files.append({
                        "filename": filename,
                        "question_count": question_count,
                        "answer_file": answer_file,
                        "has_answers": has_answers,
                        "size": os.path.getsize(file_path),
                        "modified": os.path.getmtime(file_path)
                    })
                except Exception as e:
                    print(f"读取文件 {filename} 失败: {e}")
                    files.append({
                        "filename": filename,
                        "question_count": 0,
                        "answer_file": get_matching_answer_file(filename),
                        "has_answers": False,
                        "size": os.path.getsize(file_path),
                        "modified": os.path.getmtime(file_path),
                        "error": str(e)
                    })
        
        return {"success": True, "data": files, "message": "问题集列表获取成功"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取问题集列表失败: {str(e)}")

@router.get("/dataset/{filename}")
async def get_full_dataset(filename: str, data_loader: DataLoader = Depends(get_data_loader)) -> Dict[str, Any]:
    """获取完整的数据集内容"""
    try:
        questions_path = os.path.join("data/questions", filename)
        if not os.path.exists(questions_path):
            raise HTTPException(status_code=404, detail=f"问题集文件 {filename} 不存在")
        
        with open(questions_path, 'r', encoding='utf-8') as f:
            questions_data = json.load(f)
        
        answer_filename = get_matching_answer_file(filename)
        answers_path = os.path.join("data/answers", answer_filename)
        answers_data = []
        
        if os.path.exists(answers_path):
            try:
                with open(answers_path, 'r', encoding='utf-8') as f:
                    answers_data = json.load(f)
            except Exception as e:
                print(f"读取答案集失败: {e}")
        
        questions_list = questions_data if isinstance(questions_data, list) else questions_data.get('questions', [])
        answers_list = answers_data if isinstance(answers_data, list) else answers_data.get('answers', [])
        
        return {
            "success": True,
            "data": {
                "filename": filename,
                "questions": {
                    "data": questions_list,
                    "count": len(questions_list),
                    "file_exists": True
                },
                "answers": {
                    "data": answers_list,
                    "count": len(answers_list),
                    "filename": answer_filename,
                    "file_exists": os.path.exists(answers_path)
                },
                "statistics": {
                    "total_questions": len(questions_list),
                    "total_answers": len(answers_list),
                    "has_matching_answers": len(questions_list) == len(answers_list)
                }
            },
            "message": "数据集获取成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取数据集失败: {str(e)}")

@router.get("/answers")
async def get_answers(data_loader: DataLoader = Depends(get_data_loader)) -> Dict[str, Any]:
    """获取答案集列表"""
    try:
        answers_dir = "data/answers"
        if not os.path.exists(answers_dir):
            return {"success": True, "data": [], "message": "答案目录不存在"}
        
        files = []
        for filename in os.listdir(answers_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(answers_dir, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                    answer_count = len(data) if isinstance(data, list) else len(data.get('answers', []))
                    
                    files.append({
                        "filename": filename,
                        "answer_count": answer_count,
                        "size": os.path.getsize(file_path),
                        "modified": os.path.getmtime(file_path)
                    })
                except Exception as e:
                    print(f"读取答案文件 {filename} 失败: {e}")
                    files.append({
                        "filename": filename,
                        "answer_count": 0,
                        "size": os.path.getsize(file_path),
                        "modified": os.path.getmtime(file_path),
                        "error": str(e)
                    })
        
        return {"success": True, "data": files, "message": "答案集列表获取成功"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取答案集列表失败: {str(e)}") 