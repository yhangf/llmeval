"""
API端点测试文件
测试FastAPI应用的各个端点功能，包括模型列表、任务管理、评估等
作者: AI助手
创建时间: 2024
"""

import pytest
import asyncio
import json
import os
import sys
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from models.model_manager import ModelManager
from core.task_manager import TaskManager
from utils.data_loader import DataLoader


class TestAPI:
    """API测试类"""
    
    @pytest.fixture
    async def client(self):
        """创建测试客户端"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac
    
    @pytest.fixture
    async def mock_dependencies(self):
        """模拟依赖项"""
        with patch('main.model_manager') as mock_model_manager, \
             patch('main.task_manager') as mock_task_manager, \
             patch('main.data_loader') as mock_data_loader:
            
            # 配置模型管理器模拟
            mock_model_manager.get_available_models.return_value = [
                {
                    "name": "test-model-1",
                    "info": {"provider": "Test", "type": "LLM"}
                },
                {
                    "name": "test-model-2", 
                    "info": {"provider": "Test", "type": "LLM"}
                }
            ]
            
            # 配置数据加载器模拟
            mock_data_loader.get_questions.return_value = [
                {
                    "id": "q001",
                    "content": "测试问题1",
                    "category": "测试",
                    "difficulty": "easy"
                },
                {
                    "id": "q002",
                    "content": "测试问题2", 
                    "category": "测试",
                    "difficulty": "medium"
                }
            ]
            
            # 配置任务管理器模拟
            mock_task_manager.get_all_tasks.return_value = [
                {
                    "task_id": "test-task-1",
                    "target_model": "test-model-1",
                    "evaluator_model": "test-model-2",
                    "status": "completed",
                    "created_at": "2024-01-01T00:00:00Z",
                    "question_ids": ["q001", "q002"]
                }
            ]
            
            mock_task_manager.get_statistics.return_value = {
                "total_tasks": 1,
                "completed_evaluations": 1,
                "average_score": 8.5
            }
            
            yield {
                "model_manager": mock_model_manager,
                "task_manager": mock_task_manager,
                "data_loader": mock_data_loader
            }
    
    @pytest.mark.asyncio
    async def test_root_endpoint(self, client):
        """测试根端点"""
        response = await client.get("/")
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/html")
    
    @pytest.mark.asyncio
    async def test_get_models(self, client, mock_dependencies):
        """测试获取模型列表端点"""
        response = await client.get("/api/models")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert "models" in data
        assert len(data["models"]) == 2
        assert data["models"][0]["name"] == "test-model-1"
    
    @pytest.mark.asyncio
    async def test_get_questions(self, client, mock_dependencies):
        """测试获取问题列表端点"""
        response = await client.get("/api/questions")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert "questions" in data
        assert len(data["questions"]) == 2
        assert data["questions"][0]["id"] == "q001"
    
    @pytest.mark.asyncio
    async def test_get_tasks(self, client, mock_dependencies):
        """测试获取任务列表端点"""
        response = await client.get("/api/tasks")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert "tasks" in data
        assert len(data["tasks"]) == 1
        assert data["tasks"][0]["task_id"] == "test-task-1"
    
    @pytest.mark.asyncio
    async def test_get_statistics(self, client, mock_dependencies):
        """测试获取统计信息端点"""
        response = await client.get("/api/statistics")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert "statistics" in data
        assert data["statistics"]["total_tasks"] == 1
    
    @pytest.mark.asyncio
    async def test_start_evaluation_success(self, client, mock_dependencies):
        """测试成功启动评估任务"""
        mock_dependencies["task_manager"].add_task.return_value = "test-task-id"
        
        form_data = {
            "target_model": "test-model-1",
            "evaluator_model": "test-model-2",
            "question_ids": json.dumps(["q001", "q002"])
        }
        
        response = await client.post("/api/evaluation/start", data=form_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert "task_id" in data
        assert "message" in data
    
    @pytest.mark.asyncio
    async def test_start_evaluation_missing_params(self, client):
        """测试启动评估任务时缺少参数"""
        form_data = {
            "target_model": "test-model-1"
            # 缺少 evaluator_model 和 question_ids
        }
        
        response = await client.post("/api/evaluation/start", data=form_data)
        assert response.status_code == 422  # FastAPI 验证错误
    
    @pytest.mark.asyncio
    async def test_get_task_detail_success(self, client, mock_dependencies):
        """测试获取任务详情成功"""
        task_detail = {
            "task_id": "test-task-1",
            "target_model": "test-model-1",
            "evaluator_model": "test-model-2",
            "status": "completed",
            "created_at": "2024-01-01T00:00:00Z",
            "question_ids": ["q001", "q002"],
            "results": {
                "summary": {
                    "average_score": 8.5,
                    "total_tokens": {"total_tokens": 1000},
                    "cost_estimate": {"total_cost_cny": 0.72}
                }
            }
        }
        
        mock_dependencies["task_manager"].get_task.return_value = task_detail
        
        response = await client.get("/api/tasks/test-task-1")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert data["task"]["task_id"] == "test-task-1"
        assert "results" in data["task"]
    
    @pytest.mark.asyncio
    async def test_get_task_detail_not_found(self, client, mock_dependencies):
        """测试获取不存在的任务详情"""
        mock_dependencies["task_manager"].get_task.return_value = None
        
        response = await client.get("/api/tasks/non-existent-task")
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_get_evaluation_results_success(self, client, mock_dependencies):
        """测试获取评估结果成功"""
        evaluation_results = {
            "evaluation_id": "eval_20240101_120000",
            "summary": {
                "average_score": 8.5,
                "total_questions": 2,
                "total_tokens": {"total_tokens": 1000}
            },
            "results": [
                {
                    "question_id": "q001",
                    "score": 8.0,
                    "model_answer": "测试答案1"
                },
                {
                    "question_id": "q002", 
                    "score": 9.0,
                    "model_answer": "测试答案2"
                }
            ]
        }
        
        mock_dependencies["task_manager"].get_task_results.return_value = evaluation_results
        
        response = await client.get("/api/results/test-task-1")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert data["results"]["summary"]["average_score"] == 8.5
        assert len(data["results"]["results"]) == 2
    
    @pytest.mark.asyncio
    async def test_get_evaluation_results_not_found(self, client, mock_dependencies):
        """测试获取不存在的评估结果"""
        mock_dependencies["task_manager"].get_task_results.return_value = None
        
        response = await client.get("/api/results/non-existent-task")
        assert response.status_code == 404


class TestAPIErrorHandling:
    """API错误处理测试类"""
    
    @pytest.fixture
    async def client(self):
        """创建测试客户端"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac
    
    @pytest.mark.asyncio
    async def test_models_endpoint_error(self, client):
        """测试模型端点错误处理"""
        with patch('main.model_manager') as mock_model_manager:
            mock_model_manager.get_available_models.side_effect = Exception("模型加载失败")
            
            response = await client.get("/api/models")
            assert response.status_code == 500
    
    @pytest.mark.asyncio
    async def test_questions_endpoint_error(self, client):
        """测试问题端点错误处理"""
        with patch('main.data_loader') as mock_data_loader:
            mock_data_loader.get_questions.side_effect = Exception("数据加载失败")
            
            response = await client.get("/api/questions")
            assert response.status_code == 500
    
    @pytest.mark.asyncio
    async def test_tasks_endpoint_error(self, client):
        """测试任务端点错误处理"""
        with patch('main.task_manager') as mock_task_manager:
            mock_task_manager.get_all_tasks.side_effect = Exception("任务加载失败")
            
            response = await client.get("/api/tasks")
            assert response.status_code == 500
    
    @pytest.mark.asyncio
    async def test_evaluation_start_error(self, client):
        """测试启动评估时错误处理"""
        with patch('main.task_manager') as mock_task_manager:
            mock_task_manager.add_task.side_effect = Exception("任务创建失败")
            
            form_data = {
                "target_model": "test-model-1",
                "evaluator_model": "test-model-2", 
                "question_ids": json.dumps(["q001"])
            }
            
            response = await client.post("/api/evaluation/start", data=form_data)
            assert response.status_code == 500


class TestAPIIntegration:
    """API集成测试类"""
    
    @pytest.fixture
    async def client(self):
        """创建测试客户端"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac
    
    @pytest.mark.asyncio
    async def test_full_evaluation_workflow(self, client):
        """测试完整的评估流程"""
        # 这是一个端到端的测试，验证完整的评估工作流程
        
        with patch('main.model_manager') as mock_model_manager, \
             patch('main.task_manager') as mock_task_manager, \
             patch('main.data_loader') as mock_data_loader, \
             patch('main.evaluation_engine') as mock_evaluation_engine:
            
            # 1. 获取模型列表
            mock_model_manager.get_available_models.return_value = [
                {"name": "gpt-3.5-turbo", "info": {"provider": "OpenAI", "type": "LLM"}},
                {"name": "gpt-4", "info": {"provider": "OpenAI", "type": "LLM"}}
            ]
            
            response = await client.get("/api/models")
            assert response.status_code == 200
            models_data = response.json()
            assert len(models_data["models"]) == 2
            
            # 2. 获取问题列表
            mock_data_loader.get_questions.return_value = [
                {"id": "q001", "content": "测试问题", "category": "测试"}
            ]
            
            response = await client.get("/api/questions")
            assert response.status_code == 200
            questions_data = response.json()
            assert len(questions_data["questions"]) == 1
            
            # 3. 启动评估任务
            mock_task_manager.add_task.return_value = "workflow-task-id"
            
            form_data = {
                "target_model": "gpt-3.5-turbo",
                "evaluator_model": "gpt-4",
                "question_ids": json.dumps(["q001"])
            }
            
            response = await client.post("/api/evaluation/start", data=form_data)
            assert response.status_code == 200
            start_data = response.json()
            assert start_data["status"] == "success"
            
            # 4. 检查任务状态
            mock_task_manager.get_task.return_value = {
                "task_id": "workflow-task-id",
                "status": "running",
                "progress": 50.0
            }
            
            response = await client.get("/api/tasks/workflow-task-id")
            assert response.status_code == 200
            task_data = response.json()
            assert task_data["task"]["status"] == "running"
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, client):
        """测试并发请求处理"""
        with patch('main.model_manager') as mock_model_manager:
            mock_model_manager.get_available_models.return_value = [
                {"name": "test-model", "info": {"provider": "Test", "type": "LLM"}}
            ]
            
            # 发送多个并发请求
            tasks = []
            for i in range(5):
                task = asyncio.create_task(client.get("/api/models"))
                tasks.append(task)
            
            responses = await asyncio.gather(*tasks)
            
            # 验证所有请求都成功
            for response in responses:
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "success"


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"]) 