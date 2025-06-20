# JavaScript 模块化结构说明

## 概述

原来的 `app.js` 文件已经被重构为模块化结构，将不同功能分离到独立的模块中，提高代码的可维护性和可扩展性。

## 模块结构

```
static/js/
├── app-main.js              # 主应用模块，整合所有子模块
├── app.js                   # 原始文件（已被模块化替代）
├── modules/                 # 模块目录
│   ├── api-manager.js       # API管理模块
│   ├── notification-manager.js  # 通知管理模块
│   ├── ui-components.js     # UI组件模块
│   ├── task-manager.js      # 任务管理模块
│   ├── data-manager.js      # 数据管理模块
│   └── model-manager.js     # 模型管理模块
└── README.md               # 本说明文档
```

## 各模块功能说明

### 1. API管理模块 (api-manager.js)
**职责**: 负责所有与后端API的通信
- 统一的API请求方法
- 模型相关API调用
- 任务相关API调用
- 数据相关API调用
- 错误处理和重试机制

**主要方法**:
- `request(url, options)` - 通用API请求
- `getModels()` - 获取模型列表
- `createTask(config)` - 创建评估任务
- `getTasks()` - 获取任务列表

### 2. 通知管理模块 (notification-manager.js)
**职责**: 负责显示各种类型的通知消息
- Toast通知显示
- 不同类型的通知样式
- 通知消息管理

**主要方法**:
- `show(message, type)` - 显示通知
- `success(message)` - 成功通知
- `error(message)` - 错误通知
- `warning(message)` - 警告通知

### 3. UI组件模块 (ui-components.js)
**职责**: 负责UI元素的更新和渲染
- 页面元素的动态更新
- 状态样式管理
- 通用UI工具方法

**主要方法**:
- `updateModelSelect(models)` - 更新模型选择框
- `updateModelsDisplay(models)` - 更新模型显示
- `getStatusBadgeClass(status)` - 获取状态样式
- `getScoreBadgeClass(score)` - 获取分数样式

### 4. 任务管理模块 (task-manager.js)
**职责**: 负责评估任务的创建、监控和管理
- 任务创建和配置验证
- 进度监控和显示
- 任务详情查看
- 任务结果导出

**主要方法**:
- `createTask(config)` - 创建评估任务
- `startProgressMonitoring(taskId)` - 开始进度监控
- `viewTaskDetail(taskId)` - 查看任务详情
- `deleteTask(taskId)` - 删除任务

### 5. 数据管理模块 (data-manager.js)
**职责**: 负责问题集和答案集的加载和管理
- 问题集数据管理
- 答案集数据管理
- 数据预览功能
- 数据缓存机制

**主要方法**:
- `loadQuestions()` - 加载问题集
- `loadAnswers()` - 加载答案集
- `loadQuestionPreview(filename)` - 加载问题预览
- `getQuestionSetByFilename(filename)` - 根据文件名获取问题集

### 6. 模型管理模块 (model-manager.js)
**职责**: 负责模型的加载、添加和管理
- 模型列表管理
- 模型添加和配置
- 模型状态检查
- UI字段控制

**主要方法**:
- `loadModels()` - 加载模型列表
- `addModel(formData)` - 添加新模型
- `getModelByName(name)` - 根据名称获取模型
- `toggleBaseUrlField(provider)` - 切换Base URL字段

### 7. 主应用模块 (app-main.js)
**职责**: 整合所有子模块，协调各模块之间的交互
- 模块初始化和依赖注入
- 事件绑定和处理
- 全局状态管理
- 页面生命周期管理

**主要方法**:
- `init()` - 应用初始化
- `bindEvents()` - 绑定事件监听器
- `loadInitialData()` - 加载初始数据
- `startEvaluation()` - 开始评估

## 模块依赖关系

```
app-main.js
├── api-manager.js (无依赖)
├── notification-manager.js (无依赖)
├── ui-components.js (无依赖)
├── task-manager.js (依赖: api-manager, ui-components, notification-manager)
├── data-manager.js (依赖: api-manager, ui-components, notification-manager)
└── model-manager.js (依赖: api-manager, ui-components, notification-manager)
```

## 优势

1. **模块化**: 每个模块职责单一，便于维护和测试
2. **可复用性**: 模块可以在其他项目中复用
3. **可扩展性**: 新功能可以通过添加新模块实现
4. **依赖管理**: 清晰的依赖关系，便于理解和调试
5. **代码组织**: 代码结构更清晰，便于团队协作

## 使用方式

HTML页面中使用模块化JavaScript：
```html
<script type="module" src="/static/js/app-main.js"></script>
```

## 注意事项

1. 使用ES6模块语法，需要在现代浏览器中运行
2. 模块间通过依赖注入的方式共享实例
3. 全局变量 `app` 仍然可用，保持与HTML中onclick事件的兼容性
4. 原有的 `app.js` 文件可以保留作为备份，但不再使用

## 扩展指南

要添加新功能模块：

1. 在 `modules/` 目录下创建新的模块文件
2. 定义模块类和导出
3. 在 `app-main.js` 中导入并初始化
4. 根据需要注入依赖的其他模块
5. 更新本README文档 