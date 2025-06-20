#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型管理器测试
功能：测试模型管理器和各种模型实现
作者：AI助手
创建时间：2024年
"""

import pytest
import asyncio
import os
import sys
from unittest.mock import Mock, AsyncMock, patch

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models.model_manager import ModelManager, OpenAIModel, CustomAPIModel, AgentModel


class TestBaseModel:
    """基础模型测试"""
    
    def test_base_model_initialization(self):
        """测试基础模型初始化"""
        from models.model_manager import BaseModel
        
        # 由于BaseModel是抽象类，我们创建一个具体实现来测试
        class TestModel(BaseModel):
            async def generate(self, prompt: str, **kwargs):
                return {"content": "test response"}
            
            def count_tokens(self, text: str) -> int:
                return len(text.split())
        
        model = TestModel("test_model", "test_id", "test_key")
        
        assert model.name == "test_model"
        assert model.model_id == "test_id"
        assert model.api_key == "test_key"
        assert model.token_count == 0
        assert model.request_count == 0
    
    def test_get_stats(self):
        """测试获取统计信息"""
        from models.model_manager import BaseModel
        
        class TestModel(BaseModel):
            async def generate(self, prompt: str, **kwargs):
                return {"content": "test response"}
            
            def count_tokens(self, text: str) -> int:
                return len(text.split())
        
        model = TestModel("test_model", "test_id", "test_key")
        model.token_count = 100
        model.request_count = 5
        
        stats = model.get_stats()
        assert stats["name"] == "test_model"
        assert stats["model_id"] == "test_id"
        assert stats["token_count"] == 100
        assert stats["request_count"] == 5


class TestOpenAIModel:
    """OpenAI模型测试"""
    
    @pytest.fixture
    def openai_model(self):
        """创建OpenAI模型实例"""
        return OpenAIModel("gpt-3.5-turbo", "gpt-3.5-turbo", "test_api_key")
    
    def test_openai_model_initialization(self, openai_model):
        """测试OpenAI模型初始化"""
        assert openai_model.name == "gpt-3.5-turbo"
        assert openai_model.model_id == "gpt-3.5-turbo"
        assert openai_model.api_key == "test_api_key"
        assert openai_model.client is not None
    
    @pytest.mark.asyncio
    async def test_openai_generate_success(self, openai_model):
        """测试OpenAI模型成功生成"""
        # Mock OpenAI client response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response"
        mock_response.usage = Mock()
        mock_response.usage.total_tokens = 50
        
        with patch.object(openai_model.client.chat.completions, 'create', 
                         return_value=mock_response):
            result = await openai_model.generate("Test prompt")
            
            assert result["content"] == "Test response"
            assert result["tokens_used"] == 50
            assert result["model"] == "gpt-3.5-turbo"
            assert "timestamp" in result
            assert openai_model.request_count == 1
            assert openai_model.token_count == 50
    
    @pytest.mark.asyncio
    async def test_openai_generate_error(self, openai_model):
        """测试OpenAI模型生成错误"""
        with patch.object(openai_model.client.chat.completions, 'create',
                         side_effect=Exception("API Error")):
            result = await openai_model.generate("Test prompt")
            
            assert "生成失败" in result["content"]
            assert result["tokens_used"] == 0
            assert result["error"] == "API Error"
    
    def test_count_tokens(self, openai_model):
        """测试token计数"""
        text = "这是一个测试 hello world"
        tokens = openai_model.count_tokens(text)
        assert tokens > 0
        assert isinstance(tokens, int)


class TestCustomAPIModel:
    """自定义API模型测试"""
    
    @pytest.fixture
    def custom_model(self):
        """创建自定义API模型实例"""
        return CustomAPIModel("custom_model", "custom_id", "test_key", "https://api.example.com")
    
    def test_custom_model_initialization(self, custom_model):
        """测试自定义模型初始化"""
        assert custom_model.name == "custom_model"
        assert custom_model.model_id == "custom_id"
        assert custom_model.base_url == "https://api.example.com"
        assert "Authorization" in custom_model.headers
    
    @pytest.mark.asyncio
    async def test_custom_generate_success(self, custom_model):
        """测试自定义模型成功生成"""
        mock_response_data = {
            "choices": [{"message": {"content": "Custom response"}}],
            "usage": {"total_tokens": 30}
        }
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_post = AsyncMock()
            mock_post.json.return_value = mock_response_data
            mock_post.raise_for_status.return_value = None
            
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_post)
            
            result = await custom_model.generate("Test prompt")
            
            assert result["content"] == "Custom response"
            assert result["tokens_used"] == 30
            assert custom_model.request_count == 1


class TestAgentModel:
    """Agent模型测试"""
    
    @pytest.fixture
    def agent_model(self):
        """创建Agent模型实例"""
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "test_tool",
                    "description": "A test tool"
                }
            }
        ]
        return AgentModel("agent_gpt", "gpt-4", "test_key", tools=tools)
    
    def test_agent_model_initialization(self, agent_model):
        """测试Agent模型初始化"""
        assert agent_model.name == "agent_gpt"
        assert len(agent_model.tools) == 1
        assert agent_model.client is not None
    
    @pytest.mark.asyncio
    async def test_agent_generate_with_tools(self, agent_model):
        """测试Agent模型带工具生成"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Agent response"
        mock_response.choices[0].message.tool_calls = [Mock()]
        mock_response.choices[0].message.tool_calls[0].function.name = "test_tool"
        mock_response.choices[0].message.tool_calls[0].function.arguments = "{}"
        mock_response.usage = Mock()
        mock_response.usage.total_tokens = 75
        
        with patch.object(agent_model.client.chat.completions, 'create',
                         return_value=mock_response):
            result = await agent_model.generate("Test prompt")
            
            assert result["content"] == "Agent response"
            assert result["tool_calls"] is not None
            assert len(result["tool_calls"]) == 1
            assert result["tokens_used"] == 75


class TestModelManager:
    """模型管理器测试"""
    
    @pytest.fixture
    def model_manager(self):
        """创建模型管理器实例"""
        # 使用不存在的配置文件避免加载实际配置
        return ModelManager("tests/test_models.json")
    
    def test_model_manager_initialization(self, model_manager):
        """测试模型管理器初始化"""
        assert isinstance(model_manager.models, dict)
        assert model_manager.config_file == "tests/test_models.json"
    
    def test_add_openai_model(self, model_manager):
        """测试添加OpenAI模型"""
        model_manager.add_model(
            name="test_gpt",
            provider="openai",
            model_id="gpt-3.5-turbo",
            api_key="test_key"
        )
        
        assert "test_gpt" in model_manager.models
        assert isinstance(model_manager.models["test_gpt"], OpenAIModel)
    
    def test_add_custom_model(self, model_manager):
        """测试添加自定义模型"""
        model_manager.add_model(
            name="test_custom",
            provider="custom",
            model_id="custom_model",
            api_key="test_key",
            base_url="https://api.example.com"
        )
        
        assert "test_custom" in model_manager.models
        assert isinstance(model_manager.models["test_custom"], CustomAPIModel)
    
    def test_add_agent_model(self, model_manager):
        """测试添加Agent模型"""
        model_manager.add_model(
            name="test_agent",
            provider="agent",
            model_id="gpt-4",
            api_key="test_key"
        )
        
        assert "test_agent" in model_manager.models
        assert isinstance(model_manager.models["test_agent"], AgentModel)
    
    def test_add_invalid_provider(self, model_manager):
        """测试添加无效提供商模型"""
        with pytest.raises(ValueError):
            model_manager.add_model(
                name="test_invalid",
                provider="invalid_provider",
                model_id="test_model",
                api_key="test_key"
            )
    
    def test_get_model(self, model_manager):
        """测试获取模型"""
        model_manager.add_model(
            name="test_model",
            provider="openai",
            model_id="gpt-3.5-turbo",
            api_key="test_key"
        )
        
        model = model_manager.get_model("test_model")
        assert model is not None
        assert model.name == "test_model"
        
        # 测试获取不存在的模型
        assert model_manager.get_model("non_existent") is None
    
    def test_has_model(self, model_manager):
        """测试检查模型是否存在"""
        model_manager.add_model(
            name="test_model",
            provider="openai",
            model_id="gpt-3.5-turbo",
            api_key="test_key"
        )
        
        assert model_manager.has_model("test_model") is True
        assert model_manager.has_model("non_existent") is False
    
    def test_list_models(self, model_manager):
        """测试列出所有模型"""
        model_manager.add_model(
            name="test_model1",
            provider="openai",
            model_id="gpt-3.5-turbo",
            api_key="test_key"
        )
        
        model_manager.add_model(
            name="test_model2",
            provider="custom",
            model_id="custom_model",
            api_key="test_key",
            base_url="https://api.example.com"
        )
        
        models = model_manager.list_models()
        assert len(models) == 2
        assert any(m["name"] == "test_model1" for m in models)
        assert any(m["name"] == "test_model2" for m in models)
    
    def test_remove_model(self, model_manager):
        """测试移除模型"""
        model_manager.add_model(
            name="test_model",
            provider="openai",
            model_id="gpt-3.5-turbo",
            api_key="test_key"
        )
        
        assert model_manager.has_model("test_model") is True
        
        success = model_manager.remove_model("test_model")
        assert success is True
        assert model_manager.has_model("test_model") is False
        
        # 测试移除不存在的模型
        success = model_manager.remove_model("non_existent")
        assert success is False
    
    @pytest.mark.asyncio
    async def test_test_model(self, model_manager):
        """测试模型连接测试"""
        # 添加一个模型
        model_manager.add_model(
            name="test_model",
            provider="openai",
            model_id="gpt-3.5-turbo",
            api_key="test_key"
        )
        
        # Mock generate方法
        model = model_manager.get_model("test_model")
        with patch.object(model, 'generate', return_value={"content": "Hello"}):
            result = await model_manager.test_model("test_model")
            
            assert result["success"] is True
            assert result["model"] == "test_model"
        
        # 测试不存在的模型
        result = await model_manager.test_model("non_existent")
        assert result["success"] is False


class TestModelIntegration:
    """模型集成测试"""
    
    @pytest.mark.asyncio
    async def test_model_workflow(self):
        """测试完整的模型工作流程"""
        manager = ModelManager("tests/test_models.json")
        
        # 添加模型
        manager.add_model(
            name="test_workflow",
            provider="openai",
            model_id="gpt-3.5-turbo",
            api_key="test_key"
        )
        
        # 获取模型
        model = manager.get_model("test_workflow")
        assert model is not None
        
        # Mock生成响应
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Workflow test response"
        mock_response.usage = Mock()
        mock_response.usage.total_tokens = 25
        
        with patch.object(model.client.chat.completions, 'create',
                         return_value=mock_response):
            result = await model.generate("Test workflow")
            
            assert result["content"] == "Workflow test response"
            assert result["tokens_used"] == 25
            assert model.request_count == 1
            assert model.token_count == 25
        
        # 检查统计信息
        stats = model.get_stats()
        assert stats["token_count"] == 25
        assert stats["request_count"] == 1
        
        # 移除模型
        success = manager.remove_model("test_workflow")
        assert success is True
        assert not manager.has_model("test_workflow")


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"]) 