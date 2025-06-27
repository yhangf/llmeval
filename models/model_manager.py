#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型管理器
功能：管理多种大模型的统一接口，支持OpenAI、Claude、通义千问等
作者：AI助手
创建时间：2024年
"""

import json
import os
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, AsyncIterator
import openai
import httpx
from datetime import datetime

class BaseModel(ABC):
    """模型基类，定义统一接口"""
    
    def __init__(self, name: str, model_id: str, api_key: Optional[str] = None, 
                 base_url: Optional[str] = None, **kwargs):
        self.name = name
        self.model_id = model_id
        self.api_key = api_key
        self.base_url = base_url
        self.config = kwargs
        self.token_count = 0
        self.request_count = 0
    
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """生成回复"""
        pass
    
    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """计算token数量"""
        pass
    
    def get_stats(self) -> Dict[str, Any]:
        """获取使用统计"""
        return {
            "name": self.name,
            "model_id": self.model_id,
            "token_count": self.token_count,
            "request_count": self.request_count
        }

class OpenAIModel(BaseModel):
    """OpenAI模型实现"""
    
    def __init__(self, name: str, model_id: str, api_key: str, 
                 base_url: Optional[str] = None, **kwargs):
        super().__init__(name, model_id, api_key, base_url, **kwargs)
        self.client = openai.AsyncOpenAI(
            api_key=api_key,
            base_url=base_url
        )
    
    async def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """使用OpenAI API生成回复"""
        try:
            self.request_count += 1
            
            # 构建消息
            messages = [{"role": "user", "content": prompt}]
            
            print(f"📡 调用OpenAI API: {self.model_id}")
            print(f"📝 完整消息结构:")
            print(json.dumps({
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }, ensure_ascii=False, indent=2))
            print(f"🔧 请求参数: model={self.model_id}, max_tokens={kwargs.get('max_tokens', self.config.get('max_tokens', 4000))}, temperature={kwargs.get('temperature', self.config.get('temperature', 0.7))}")
            
            response = await self.client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                max_tokens=kwargs.get('max_tokens', self.config.get('max_tokens', 4000)),
                temperature=kwargs.get('temperature', self.config.get('temperature', 0.7)),
                **{k: v for k, v in kwargs.items() if k not in ['max_tokens', 'temperature']}
            )
            
            content = response.choices[0].message.content
            print(f"✅ OpenAI响应成功: {len(content)} 字符")
            
            # 统计token使用
            if hasattr(response, 'usage') and response.usage:
                self.token_count += response.usage.total_tokens
                tokens_used = response.usage.total_tokens
            else:
                tokens_used = self.count_tokens(prompt + content)
                self.token_count += tokens_used
            
            return {
                "content": content,
                "tokens_used": tokens_used,
                "model": self.model_id,
                "timestamp": datetime.now().isoformat(),
                "usage": response.usage.__dict__ if hasattr(response, 'usage') and response.usage else {}
            }
            
        except Exception as e:
            print(f"❌ OpenAI请求失败: {str(e)}")
            return {
                "content": f"生成失败: {str(e)}",
                "tokens_used": 0,
                "model": self.model_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def count_tokens(self, text: str) -> int:
        """简单的token计数估算"""
        # 粗略估算：中文字符算1个token，英文单词按空格分割
        chinese_chars = len([c for c in text if '\u4e00' <= c <= '\u9fff'])
        english_words = len(text.replace('，', ' ').replace('。', ' ').split())
        return chinese_chars + english_words

class CustomAPIModel(BaseModel):
    """自定义API模型实现（如通义千问、DeepSeek等）"""
    
    def __init__(self, name: str, model_id: str, api_key: str, 
                 base_url: str, **kwargs):
        super().__init__(name, model_id, api_key, base_url, **kwargs)
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    async def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """使用自定义API生成回复"""
        try:
            self.request_count += 1
            
            # 构建请求数据
            data = {
                "model": self.model_id,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": kwargs.get('max_tokens', self.config.get('max_tokens', 4000)),
                "temperature": kwargs.get('temperature', self.config.get('temperature', 0.7))
            }
            
            print(f"📡 调用自定义API: {self.base_url}/chat/completions")
            print(f"📝 完整消息结构:")
            print(json.dumps({
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }, ensure_ascii=False, indent=2))
            print(f"🔧 请求参数: model={self.model_id}, max_tokens={data['max_tokens']}, temperature={data['temperature']}")
            
            # 设置更长的超时时间
            timeout_config = httpx.Timeout(
                connect=30.0,  # 连接超时
                read=120.0,    # 读取超时
                write=30.0,    # 写入超时
                pool=30.0      # 连接池超时
            )
            
            async with httpx.AsyncClient(timeout=timeout_config) as client:
                # 添加重试机制
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        print(f"尝试第 {attempt + 1} 次请求...")
                        response = await client.post(
                            f"{self.base_url}/chat/completions",
                            headers=self.headers,
                            json=data
                        )
                        print(f"响应状态码: {response.status_code}")
                        response.raise_for_status()
                        break
                    except httpx.TimeoutException as e:
                        if attempt == max_retries - 1:
                            raise e
                        wait_time = (attempt + 1) * 5  # 递增等待时间
                        print(f"请求超时，{wait_time}秒后重试: {str(e)}")
                        await asyncio.sleep(wait_time)
                    except httpx.HTTPStatusError as e:
                        if e.response.status_code in [429, 503]:  # 速率限制或服务不可用
                            if attempt == max_retries - 1:
                                raise e
                            wait_time = (attempt + 1) * 10  # 更长的等待时间
                            print(f"API限制或服务不可用，{wait_time}秒后重试: {str(e)}")
                            await asyncio.sleep(wait_time)
                        else:
                            raise e
                    except Exception as e:
                        if attempt == max_retries - 1:
                            raise e
                        wait_time = (attempt + 1) * 3
                        print(f"请求失败，{wait_time}秒后重试: {str(e)}")
                        await asyncio.sleep(wait_time)
                
                result = response.json()
                print(f"✅ 响应成功: {len(result.get('choices', []))} 个回答")
            
            content = result["choices"][0]["message"]["content"]
            
            # 统计token使用
            if "usage" in result:
                tokens_used = result["usage"]["total_tokens"]
                self.token_count += tokens_used
            else:
                tokens_used = self.count_tokens(prompt + content)
                self.token_count += tokens_used
            
            return {
                "content": content,
                "tokens_used": tokens_used,
                "model": self.model_id,
                "timestamp": datetime.now().isoformat(),
                "usage": result.get("usage", {})
            }
            
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP错误 {e.response.status_code}: {e.response.text}"
            print(f"模型 {self.name} API调用失败: {error_msg}")
            return {
                "content": f"生成失败: {error_msg}",
                "tokens_used": 0,
                "model": self.model_id,
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            }
        except httpx.TimeoutException as e:
            error_msg = "请求超时"
            print(f"模型 {self.name} 请求超时")
            return {
                "content": f"生成失败: {error_msg}",
                "tokens_used": 0,
                "model": self.model_id,
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            }
        except KeyError as e:
            error_msg = f"响应格式错误，缺少字段: {str(e)}"
            print(f"模型 {self.name} 响应格式错误: {error_msg}")
            return {
                "content": f"生成失败: {error_msg}",
                "tokens_used": 0,
                "model": self.model_id,
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            error_msg = str(e)
            print(f"模型 {self.name} 生成失败: {error_msg}")
            return {
                "content": f"生成失败: {error_msg}",
                "tokens_used": 0,
                "model": self.model_id,
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            }
    
    def count_tokens(self, text: str) -> int:
        """简单的token计数估算"""
        chinese_chars = len([c for c in text if '\u4e00' <= c <= '\u9fff'])
        english_words = len(text.replace('，', ' ').replace('。', ' ').split())
        return chinese_chars + english_words

class AgentModel(BaseModel):
    """Agent模型实现，支持工具调用"""
    
    def __init__(self, name: str, model_id: str, api_key: str, 
                 base_url: Optional[str] = None, tools: Optional[List[Dict]] = None, **kwargs):
        super().__init__(name, model_id, api_key, base_url, **kwargs)
        self.tools = tools or []
        self.client = openai.AsyncOpenAI(
            api_key=api_key,
            base_url=base_url
        )
    
    async def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """使用Agent模型生成回复，支持工具调用"""
        try:
            self.request_count += 1
            
            messages = [{"role": "user", "content": prompt}]
            
            # 如果有工具，添加工具调用
            if self.tools:
                response = await self.client.chat.completions.create(
                    model=self.model_id,
                    messages=messages,
                    tools=self.tools,
                    max_tokens=kwargs.get('max_tokens', self.config.get('max_tokens', 4000)),
                    temperature=kwargs.get('temperature', self.config.get('temperature', 0.7))
                )
            else:
                response = await self.client.chat.completions.create(
                    model=self.model_id,
                    messages=messages,
                    max_tokens=kwargs.get('max_tokens', self.config.get('max_tokens', 4000)),
                    temperature=kwargs.get('temperature', self.config.get('temperature', 0.7))
                )
            
            content = response.choices[0].message.content
            tool_calls = None
            
            # 处理工具调用
            if hasattr(response.choices[0].message, 'tool_calls') and response.choices[0].message.tool_calls:
                tool_calls = [
                    {
                        "function": call.function.name,
                        "arguments": call.function.arguments
                    }
                    for call in response.choices[0].message.tool_calls
                ]
            
            # 统计token使用
            if hasattr(response, 'usage') and response.usage:
                tokens_used = response.usage.total_tokens
                self.token_count += tokens_used
            else:
                tokens_used = self.count_tokens(prompt + (content or ""))
                self.token_count += tokens_used
            
            return {
                "content": content,
                "tool_calls": tool_calls,
                "tokens_used": tokens_used,
                "model": self.model_id,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "content": f"生成失败: {str(e)}",
                "tool_calls": None,
                "tokens_used": 0,
                "model": self.model_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def count_tokens(self, text: str) -> int:
        """简单的token计数估算"""
        chinese_chars = len([c for c in text if '\u4e00' <= c <= '\u9fff'])
        english_words = len(text.replace('，', ' ').replace('。', ' ').split())
        return chinese_chars + english_words

class ModelManager:
    """模型管理器，统一管理所有模型"""
    
    def __init__(self, config_file: str = "config/models.json"):
        self.models: Dict[str, BaseModel] = {}
        self.config_file = config_file
        self.load_models_from_config()
    
    def load_models_from_config(self):
        """从配置文件加载模型"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                for model_config in config.get('models', []):
                    self.add_model_from_config(model_config)
                    
            except Exception as e:
                print(f"加载模型配置失败: {e}")
    
    def add_model_from_config(self, config: Dict[str, Any]):
        """从配置添加模型"""
        try:
            provider = config.get('provider', 'openai').lower()
            name = config.get('name', 'unknown')
            api_key = config.get('api_key', '')
            
            # 检查API密钥
            if not api_key:
                print(f"警告: 模型 {name} 缺少API密钥，将跳过加载")
                return
            
            if provider == 'openai':
                model = OpenAIModel(**config)
            elif provider == 'custom':
                model = CustomAPIModel(**config)
            elif provider == 'agent':
                model = AgentModel(**config)
            else:
                print(f"不支持的模型提供商: {provider}")
                return
            
            self.models[config['name']] = model
            print(f"成功加载模型: {config['name']} (提供商: {provider})")
            
        except Exception as e:
            print(f"加载模型 {config.get('name', 'unknown')} 失败: {str(e)}")
    
    def add_model(self, name: str, provider: str, model_id: str, 
                  api_key: str, base_url: Optional[str] = None, **kwargs):
        """动态添加模型"""
        provider = provider.lower()
        
        if provider == 'openai':
            model = OpenAIModel(name, model_id, api_key, base_url, **kwargs)
        elif provider == 'custom':
            if not base_url:
                raise ValueError("自定义API模型需要指定base_url")
            model = CustomAPIModel(name, model_id, api_key, base_url, **kwargs)
        elif provider == 'agent':
            model = AgentModel(name, model_id, api_key, base_url, **kwargs)
        else:
            raise ValueError(f"不支持的模型提供商: {provider}")
        
        self.models[name] = model
        print(f"成功添加模型: {name}")
        
        # 保存到配置文件
        self.save_model_to_config(name, provider, model_id, api_key, base_url, **kwargs)
        
    def get_model(self, name: str) -> Optional[BaseModel]:
        """获取模型实例"""
        return self.models.get(name)
    
    def has_model(self, name: str) -> bool:
        """检查模型是否存在"""
        return name in self.models
    
    def list_models(self) -> List[Dict[str, Any]]:
        """列出所有模型"""
        return [
            {
                "name": name,
                "model_id": model.model_id,
                "type": model.__class__.__name__,
                "stats": model.get_stats()
            }
            for name, model in self.models.items()
        ]
    
    def remove_model(self, name: str) -> bool:
        """移除模型"""
        if name in self.models:
            del self.models[name]
            # 从配置文件中移除
            self.remove_model_from_config(name)
            return True
        return False
    
    def save_model_to_config(self, name: str, provider: str, model_id: str, 
                           api_key: str, base_url: Optional[str] = None, **kwargs):
        """保存模型配置到文件"""
        try:
            # 确保配置目录存在
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            # 加载现有配置
            config = {"models": []}
            if os.path.exists(self.config_file):
                try:
                    with open(self.config_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                except Exception as e:
                    print(f"读取配置文件失败，将创建新配置: {e}")
            
            # 检查是否已存在同名模型
            existing_models = config.get('models', [])
            model_exists = False
            for i, existing_model in enumerate(existing_models):
                if existing_model.get('name') == name:
                    # 更新现有模型配置
                    existing_models[i] = {
                        "name": name,
                        "provider": provider,
                        "model_id": model_id,
                        "api_key": api_key,
                        "base_url": base_url,
                        "max_tokens": kwargs.get('max_tokens', 4000),
                        "temperature": kwargs.get('temperature', 0.7),
                        "description": kwargs.get('description', f"{provider.title()} {model_id} 模型")
                    }
                    model_exists = True
                    break
            
            # 如果不存在，添加新模型
            if not model_exists:
                new_model_config = {
                    "name": name,
                    "provider": provider,
                    "model_id": model_id,
                    "api_key": api_key,
                    "base_url": base_url,
                    "max_tokens": kwargs.get('max_tokens', 4000),
                    "temperature": kwargs.get('temperature', 0.7),
                    "description": kwargs.get('description', f"{provider.title()} {model_id} 模型")
                }
                existing_models.append(new_model_config)
            
            config['models'] = existing_models
            
            # 确保包含默认配置
            if 'default_config' not in config:
                config['default_config'] = {
                    "max_tokens": 4000,
                    "temperature": 0.7,
                    "top_p": 1.0,
                    "frequency_penalty": 0.0,
                    "presence_penalty": 0.0
                }
            
            # 保存配置文件
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            print(f"模型配置已保存到 {self.config_file}")
            
        except Exception as e:
            print(f"保存模型配置失败: {e}")
            raise e
    
    def remove_model_from_config(self, name: str):
        """从配置文件中移除模型"""
        try:
            if not os.path.exists(self.config_file):
                return
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 移除指定模型
            models = config.get('models', [])
            config['models'] = [m for m in models if m.get('name') != name]
            
            # 保存更新后的配置
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            print(f"已从配置文件中移除模型: {name}")
            
        except Exception as e:
            print(f"从配置文件移除模型失败: {e}")
    
    async def test_model(self, name: str, test_prompt: str = "你好") -> Dict[str, Any]:
        """测试模型是否正常工作"""
        model = self.get_model(name)
        if not model:
            return {"success": False, "error": f"模型 {name} 不存在"}
        
        try:
            result = await model.generate(test_prompt)
            return {
                "success": True,
                "model": name,
                "result": result
            }
        except Exception as e:
            return {
                "success": False,
                "model": name,
                "error": str(e)
            } 