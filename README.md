# 🤖 大模型测评系统

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](tests/)

一个功能强大的大语言模型评估平台，支持多种模型接入、自动化评估和可视化结果展示。

## ✨ 特性

### 🔧 核心功能
- **多模型支持**：OpenAI、自定义API、Agent模型
- **自动化评估**：基于问答对的自动评估流程
- **实时监控**：任务进度实时跟踪和状态更新
- **可视化界面**：现代化的Web界面，支持响应式设计
- **结果分析**：详细的评估报告和统计分析

### 🚀 技术特点
- **异步处理**：基于FastAPI的高性能异步架构
- **模块化设计**：清晰的代码结构和组件分离
- **扩展性强**：易于添加新的模型和评估指标
- **容错机制**：完善的错误处理和重试机制
- **测试覆盖**：全面的单元测试和集成测试

## 🏗️ 系统架构

```
大模型测评系统
├── 前端界面 (HTML/CSS/JS)
├── API层 (FastAPI)
├── 业务逻辑层
│   ├── 模型管理器
│   ├── 任务管理器
│   ├── 评估引擎
│   └── 数据加载器
├── 数据层
│   ├── 问题集
│   ├── 答案集
│   └── 结果存储
└── 配置层
    ├── 模型配置
    └── 系统配置
```

## 📦 安装指南

### 环境要求
- Python 3.8+
- pip 或 conda

### 快速安装

```bash
# 克隆项目
git clone https://github.com/yourusername/llm-eval-system.git
cd llm-eval-system

# 安装依赖
pip install -r requirements.txt

# 启动服务
python main.py
```

### Docker 部署

```bash
# 构建镜像
docker build -t llm-eval-system .

# 运行容器
docker run -p 8000:8000 llm-eval-system
```

## 🚀 快速开始

### 1. 配置模型

编辑 `config/models.json` 文件，添加你的模型配置：

```json
{
  "models": [
    {
      "name": "gpt-4",
      "provider": "openai",
      "model_id": "gpt-4",
      "api_key": "your-api-key-here",
      "max_tokens": 2000,
      "temperature": 0.7,
      "description": "OpenAI GPT-4 模型"
    }
  ]
}
```

### 2. 准备数据

#### 问题集格式 (`data/questions/`)
```json
[
  {
    "id": 1,
    "question": "什么是人工智能？",
    "category": "基础概念",
    "difficulty": "easy",
    "tags": ["AI", "概念"]
  }
]
```

#### 答案集格式 (`data/answers/`)
```json
[
  {
    "question_id": 1,
    "answer": "人工智能是计算机科学的一个分支...",
    "score": 5,
    "explanation": "标准答案解释"
  }
]
```

### 3. 启动系统

```bash
# 开发模式
python main.py

# 生产模式
uvicorn main:app --host 0.0.0.0 --port 8000
```

访问 `http://localhost:8000` 开始使用！

## 📖 使用指南

### Web界面操作

1. **开始评估**
   - 选择要评估的模型
   - 选择问题集和答案集
   - 配置评估参数
   - 点击"开始评估"

2. **任务管理**
   - 查看所有评估任务
   - 监控任务进度
   - 查看详细结果
   - 下载评估报告

3. **模型管理**
   - 添加新模型
   - 配置模型参数
   - 测试模型连接
   - 查看模型统计

4. **数据管理**
   - 上传问题集
   - 管理答案集
   - 预览数据内容

### API接口

#### 模型管理
```bash
# 获取模型列表
curl http://localhost:8000/api/models

# 添加模型
curl -X POST http://localhost:8000/api/models \
  -H "Content-Type: application/json" \
  -d '{"name": "test-model", "provider": "openai", "model_id": "gpt-3.5-turbo", "api_key": "sk-..."}'
```

#### 任务管理
```bash
# 创建评估任务
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"model_name": "gpt-4", "question_file": "sample_questions.json", "answer_file": "sample_answers.json"}'

# 获取任务状态
curl http://localhost:8000/api/tasks/{task_id}

# 获取任务列表
curl http://localhost:8000/api/tasks
```

## 🔧 配置说明

### 模型配置

支持的模型提供商：

#### OpenAI
```json
{
  "name": "gpt-4",
  "provider": "openai",
  "model_id": "gpt-4",
  "api_key": "sk-...",
  "max_tokens": 2000,
  "temperature": 0.7
}
```

#### 自定义API
```json
{
  "name": "custom-model",
  "provider": "custom",
  "model_id": "custom-model-id",
  "api_key": "your-api-key",
  "base_url": "https://api.example.com/v1",
  "max_tokens": 1500,
  "temperature": 0.7
}
```

#### Agent模型
```json
{
  "name": "agent-gpt-4",
  "provider": "agent",
  "model_id": "gpt-4",
  "api_key": "sk-...",
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "search_web",
        "description": "搜索网络信息"
      }
    }
  ]
}
```

### 评估配置

```json
{
  "default_config": {
    "max_tokens": 4000,
    "temperature": 0.7,
    "top_p": 1.0,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0
  },
  "evaluation_metrics": [
    "accuracy",
    "relevance",
    "coherence",
    "completeness"
  ]
}
```

## 📊 评估指标

### 基础指标
- **准确性 (Accuracy)**：答案的正确程度
- **相关性 (Relevance)**：答案与问题的相关程度
- **连贯性 (Coherence)**：答案的逻辑连贯性
- **完整性 (Completeness)**：答案的完整程度

### 统计指标
- **Token使用量**：每个问题的Token消耗
- **响应时间**：模型响应延迟
- **成功率**：成功回答的问题比例
- **错误率**：回答错误或失败的比例

## 🧪 测试

### 运行测试
```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_models.py

# 运行测试并生成覆盖率报告
pytest --cov=. --cov-report=html
```

### 测试覆盖
- **单元测试**：核心组件的功能测试
- **集成测试**：API接口的集成测试
- **性能测试**：系统性能和并发测试
- **错误处理测试**：异常情况的处理测试

## 📈 性能优化

### 系统性能
- **异步处理**：所有I/O操作都使用异步模式
- **连接池**：HTTP客户端连接复用
- **缓存机制**：频繁访问的数据缓存
- **批处理**：支持批量评估提高效率

### 扩展性
- **水平扩展**：支持多实例部署
- **负载均衡**：支持反向代理和负载均衡
- **数据库**：可扩展到关系型数据库
- **消息队列**：支持异步任务队列

## 🛠️ 开发指南

### 项目结构
```
llm-eval-system/
├── main.py                 # 主应用入口
├── requirements.txt        # 依赖包列表
├── config/                 # 配置文件
│   └── models.json        # 模型配置
├── core/                   # 核心业务逻辑
│   ├── evaluator.py       # 评估引擎
│   └── task_manager.py    # 任务管理器
├── models/                 # 模型管理
│   └── model_manager.py   # 模型管理器
├── utils/                  # 工具函数
│   ├── data_loader.py     # 数据加载器
│   └── prompt_loader.py   # 提示词加载器
├── data/                   # 数据文件
│   ├── questions/         # 问题集
│   └── answers/           # 答案集
├── templates/              # HTML模板
│   └── index.html         # 主页模板
├── static/                 # 静态资源
│   ├── css/               # 样式文件
│   └── js/                # JavaScript文件
└── tests/                  # 测试文件
    ├── test_models.py     # 模型测试
    └── test_api.py        # API测试
```

### 添加新模型

1. **继承BaseModel类**
```python
from models.model_manager import BaseModel

class CustomModel(BaseModel):
    async def generate(self, prompt: str, **kwargs):
        # 实现生成逻辑
        pass
    
    def count_tokens(self, text: str) -> int:
        # 实现token计数
        pass
```

2. **注册到ModelManager**
```python
# 在model_manager.py中添加
elif provider == "custom_provider":
    return CustomModel(name, model_id, api_key, **kwargs)
```

### 添加新评估指标

1. **扩展评估器**
```python
# 在evaluator.py中添加新指标
async def evaluate_custom_metric(self, question, answer, reference):
    # 实现自定义评估逻辑
    return score
```

2. **更新配置**
```json
{
  "evaluation_metrics": [
    "accuracy",
    "relevance",
    "custom_metric"
  ]
}
```

## 🤝 贡献指南

### 贡献流程
1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 代码规范
- 使用 Black 进行代码格式化
- 遵循 PEP 8 编码规范
- 添加适当的类型注解
- 编写详细的文档字符串

### 提交规范
- feat: 新功能
- fix: 修复bug
- docs: 文档更新
- style: 代码格式化
- refactor: 代码重构
- test: 测试相关
- chore: 构建过程或辅助工具的变动

## 📄 许可证

本项目采用 MIT 许可证。详情请参阅 [LICENSE](LICENSE) 文件。

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者！

特别感谢：
- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的Python Web框架
- [OpenAI](https://openai.com/) - 提供强大的语言模型API
- [Bootstrap](https://getbootstrap.com/) - 优秀的前端框架

## 📞 联系我们

- 项目主页：https://github.com/yourusername/llm-eval-system
- 问题反馈：https://github.com/yourusername/llm-eval-system/issues
- 邮箱：your.email@example.com

## 🔮 路线图

### v1.1 (计划中)
- [ ] 支持更多模型提供商
- [ ] 增加更多评估指标
- [ ] 支持自定义评估模板
- [ ] 添加用户权限管理

### v1.2 (计划中)
- [ ] 支持多语言评估
- [ ] 添加A/B测试功能
- [ ] 集成更多可视化图表
- [ ] 支持批量导入数据

### v2.0 (长期计划)
- [ ] 支持分布式部署
- [ ] 添加机器学习评估模型
- [ ] 支持实时流式评估
- [ ] 集成更多第三方服务

---

⭐ 如果这个项目对你有帮助，请给我们一个 Star！

�� **最后更新**: 2024年12月 