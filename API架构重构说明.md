# API架构重构说明

## 重构概述

本次重构将原本集中在`main.py`文件中的所有路由定义解耦到`api`文件夹中，实现了更好的代码组织和模块化。

## 新的项目结构

```
llm-auto-test/
├── api/                          # API路由模块
│   ├── __init__.py              # 模块初始化文件
│   ├── dependencies.py         # 依赖注入管理
│   ├── schemas.py              # 数据模型定义
│   ├── models.py               # 模型管理路由
│   ├── tasks.py                # 任务管理路由
│   ├── datasets.py             # 数据集管理路由
│   └── evaluations.py          # 评估历史路由
├── main.py                      # 主应用文件（简化后）
└── ...                         # 其他原有文件
```

## 模块说明

### 1. `api/dependencies.py` - 依赖注入管理
- 管理所有组件的单例实例
- 提供依赖注入函数
- 统一初始化所有依赖组件

**主要功能：**
- `init_dependencies()`: 初始化所有组件
- `get_model_manager()`: 获取模型管理器
- `get_task_manager()`: 获取任务管理器
- `get_data_loader()`: 获取数据加载器
- `get_evaluator()`: 获取评估器
- `get_evaluation_history()`: 获取评估历史

### 2. `api/schemas.py` - 数据模型定义
- 集中定义所有API使用的Pydantic模型
- 包含请求和响应模型

**主要模型：**
- `TaskCreateRequest`: 创建任务请求
- `ModelConfig`: 模型配置
- `APIResponse`: 通用API响应
- `ErrorResponse`: 错误响应

### 3. `api/models.py` - 模型管理路由
- 处理模型的增删查改操作
- 路由前缀: `/api/models`

**API端点：**
- `GET /api/models`: 获取模型列表
- `POST /api/models`: 添加新模型
- `DELETE /api/models/{model_name}`: 删除模型

### 4. `api/tasks.py` - 任务管理路由
- 处理评估任务的生命周期管理
- 路由前缀: `/api/tasks`

**API端点：**
- `POST /api/tasks`: 创建新任务
- `GET /api/tasks`: 获取任务列表
- `GET /api/tasks/{task_id}`: 获取任务详情
- `DELETE /api/tasks/{task_id}`: 删除任务

### 5. `api/datasets.py` - 数据集管理路由
- 处理问题集和答案集的查询
- 路由前缀: `/api`

**API端点：**
- `GET /api/questions`: 获取问题集列表
- `GET /api/answers`: 获取答案集列表
- `GET /api/dataset/{filename}`: 获取完整数据集

### 6. `api/evaluations.py` - 评估历史路由
- 处理模型评估历史的查询
- 路由前缀: `/api`

**API端点：**
- `GET /api/model-evaluations`: 获取评估历史

## 重构优势

### 1. **代码组织清晰**
- 按功能模块分离路由
- 每个文件职责单一明确
- 便于维护和扩展

### 2. **依赖管理优化**
- 统一的依赖注入机制
- 避免循环依赖问题
- 便于单元测试

### 3. **可扩展性强**
- 新增API只需创建新的路由文件
- 模块间松耦合
- 支持独立开发和测试

### 4. **主文件简化**
- `main.py`只负责应用配置和路由注册
- 移除了大量路由定义代码
- 更加专注于应用启动逻辑

## 使用方式

### 启动应用
```bash
python main.py
```

### 添加新的API路由
1. 在`api`文件夹中创建新的路由文件
2. 定义路由处理函数
3. 在`api/__init__.py`中导入路由
4. 在`main.py`中注册路由

### 示例：添加新路由模块
```python
# api/new_module.py
from fastapi import APIRouter

router = APIRouter(prefix="/api/new", tags=["new"])

@router.get("/endpoint")
async def new_endpoint():
    return {"message": "Hello from new module"}

# api/__init__.py
from .new_module import router as new_router

# main.py
app.include_router(new_router)
```

## 兼容性

- 所有原有的API端点保持不变
- 前端代码无需修改
- 功能完全兼容重构前的版本

## 测试验证

重构后的应用已通过以下测试：
- ✅ 依赖注入正常工作
- ✅ 所有路由正确注册
- ✅ API端点功能完整
- ✅ 应用正常启动

重构完成，代码结构更加清晰，便于后续开发和维护。 