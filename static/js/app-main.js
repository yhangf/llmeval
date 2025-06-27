/**
 * 主应用模块
 * 整合所有子模块，协调各模块之间的交互
 */
import ApiManager from './modules/api-manager.js';
import NotificationManager from './modules/notification-manager.js';
import UIComponents from './modules/ui-components.js';
import TaskManager from './modules/task-manager.js';
import DataManager from './modules/data-manager.js';
import ModelManager from './modules/model-manager.js';

class EvaluationApp {
    constructor() {
        // 初始化各个模块
        this.apiManager = new ApiManager();
        this.notificationManager = new NotificationManager();
        this.uiComponents = new UIComponents();
        
        // 创建依赖其他模块的管理器
        this.taskManager = new TaskManager(this.apiManager, this.uiComponents, this.notificationManager);
        this.dataManager = new DataManager(this.apiManager, this.uiComponents, this.notificationManager);
        this.modelManager = new ModelManager(this.apiManager, this.uiComponents, this.notificationManager);
        
        this.init();
    }

    /**
     * 初始化应用
     */
    init() {
        this.bindEvents();
        this.loadInitialData();
        this.updateTemperatureDisplay();
    }

    /**
     * 绑定事件监听器
     */
    bindEvents() {
        // 评估表单提交
        document.getElementById('evaluationForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.startEvaluation();
        });

        // 添加模型表单提交
        document.getElementById('addModelForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.addModel();
        });

        // 温度参数滑块
        document.getElementById('temperature')?.addEventListener('input', (e) => {
            document.getElementById('tempValue').textContent = e.target.value;
        });

        // 模型提供商选择
        document.getElementById('modelProvider')?.addEventListener('change', (e) => {
            this.modelManager.toggleBaseUrlField(e.target.value);
        });

        // 问题集选择
        document.getElementById('questionSet')?.addEventListener('change', (e) => {
            this.dataManager.loadQuestionPreview(e.target.value);
        });

        // 标签页切换
        document.querySelectorAll('[data-bs-toggle="tab"]').forEach(tab => {
            tab.addEventListener('shown.bs.tab', (e) => {
                this.onTabSwitch(e.target.getAttribute('data-bs-target'));
            });
        });
    }

    /**
     * 加载初始数据
     */
    async loadInitialData() {
        try {
            await Promise.all([
                this.modelManager.loadModels(),
                this.dataManager.loadQuestions(),
                this.dataManager.loadAnswers(),
                this.dataManager.loadModelEvaluations(),
                this.loadTasks()
            ]);
        } catch (error) {
            console.error('加载初始数据失败:', error);
            this.notificationManager.error('加载数据失败');
        }
    }

    /**
     * 开始评估
     */
    async startEvaluation() {
        const form = document.getElementById('evaluationForm');
        if (!form) {
            console.warn('评估表单未找到');
            return;
        }

        const config = {
            target_model_name: document.getElementById('targetModelSelect')?.value,
            evaluator_model_name: document.getElementById('evaluatorModelSelect')?.value,
            question_file: document.getElementById('questionSet')?.value,
            config: {
                temperature: parseFloat(document.getElementById('temperature')?.value || '0.7'),
                max_tokens: parseInt(document.getElementById('maxTokens')?.value || '4000')
            }
        };

        try {
            await this.taskManager.createTask(config);
            // 刷新任务列表
            this.loadTasks();
        } catch (error) {
            // 错误已在taskManager中处理
        }
    }

    /**
     * 添加模型
     */
    async addModel() {
        const form = document.getElementById('addModelForm');
        if (!form) {
            console.warn('添加模型表单未找到');
            return;
        }

        const formData = new FormData(form);
        
        try {
            await this.modelManager.addModel(formData);
            form.reset();
        } catch (error) {
            // 错误已在modelManager中处理
        }
    }

    /**
     * 删除模型
     */
    async deleteModel(modelName) {
        // 显示确认对话框
        const confirmed = await this.showConfirmDialog(
            '确认删除模型',
            `确定要删除模型 "${modelName}" 吗？此操作无法撤销。`,
            '删除',
            'danger'
        );

        if (!confirmed) {
            return;
        }

        try {
            await this.modelManager.deleteModel(modelName);
        } catch (error) {
            // 错误已在modelManager中处理
        }
    }

    /**
     * 加载任务列表
     */
    async loadTasks() {
        try {
            const data = await this.apiManager.getTasks();
            
            if (data.success) {
                this.updateTasksDisplay(data.data);
            } else {
                throw new Error(data.message || '获取任务列表失败');
            }
        } catch (error) {
            console.error('加载任务列表失败:', error);
            this.notificationManager.error('加载任务列表失败');
        }
    }

    /**
     * 更新任务显示
     */
    updateTasksDisplay(tasks) {
        const container = document.getElementById('tasksContainer');
        if (!container) {
            console.warn('任务容器元素未找到');
            return;
        }
        
        if (tasks.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted">
                    <i class="bi bi-inbox fs-1"></i>
                    <p class="mt-2">暂无评估任务</p>
                    <small class="text-muted">系统会自动保留最近的5个任务记录</small>
                </div>
            `;
            return;
        }

        // 按创建时间排序
        tasks.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

        // 添加任务数量提示
        const taskCountInfo = tasks.length >= 5 ? 
            `<div class="alert alert-info mb-3">
                <i class="bi bi-info-circle"></i> 
                当前显示 ${tasks.length} 个任务，系统会自动保留最近的5个任务记录，旧任务会被自动清理
            </div>` : 
            `<div class="alert alert-success mb-3">
                <i class="bi bi-check-circle"></i> 
                当前有 ${tasks.length} 个任务记录，系统会自动保留最近的5个任务
            </div>`;

        container.innerHTML = taskCountInfo + tasks.map(task => `
            <div class="card task-card status-${task.status}">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <h6 class="card-title mb-1">
                                ${task.target_model_name || task.model_name}
                                <span class="badge ${this.uiComponents.getStatusBadgeClass(task.status)}">${this.uiComponents.getStatusText(task.status)}</span>
                            </h6>
                            <small class="text-muted">任务ID: ${task.task_id}</small>
                            ${task.evaluator_model_name ? `
                                <div class="mt-1">
                                    <small class="text-muted">
                                        <i class="bi bi-arrow-right"></i> 评估模型: <span class="badge bg-success">${task.evaluator_model_name}</span>
                                    </small>
                                </div>
                            ` : ''}
                            <div class="mt-2">
                                <small class="text-muted">
                                    创建时间: ${new Date(task.created_at).toLocaleString()}
                                </small>
                            </div>
                            ${task.status === 'running' ? `
                                <div class="mt-2">
                                    <div class="progress" style="height: 5px;">
                                        <div class="progress-bar" style="width: ${task.progress}%"></div>
                                    </div>
                                    <small class="text-muted">${task.progress}% 完成</small>
                                </div>
                            ` : ''}
                        </div>
                        <div class="dropdown">
                            <button class="btn btn-sm btn-outline-secondary dropdown-toggle" 
                                    data-bs-toggle="dropdown">
                                操作
                            </button>
                            <ul class="dropdown-menu">
                                <li><a class="dropdown-item" href="#" onclick="app.viewTaskDetail('${task.task_id}')">
                                    <i class="bi bi-eye"></i> 查看详情
                                </a></li>
                                ${task.status === 'completed' ? `
                                    <li><a class="dropdown-item" href="#" onclick="app.downloadResults('${task.task_id}')">
                                        <i class="bi bi-download"></i> 下载结果
                                    </a></li>
                                ` : ''}
                                <li><hr class="dropdown-divider"></li>
                                <li><a class="dropdown-item text-danger" href="#" onclick="app.deleteTask('${task.task_id}')">
                                    <i class="bi bi-trash"></i> 删除任务
                                </a></li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }

    /**
     * 查看任务详情
     */
    async viewTaskDetail(taskId) {
        await this.taskManager.viewTaskDetail(taskId);
    }

    /**
     * 下载任务结果
     */
    downloadTaskResults() {
        this.taskManager.downloadTaskResults();
    }

    /**
     * 删除任务
     */
    async deleteTask(taskId) {
        try {
            await this.taskManager.deleteTask(taskId);
            this.loadTasks(); // 刷新任务列表
        } catch (error) {
            // 错误已在taskManager中处理
        }
    }

    /**
     * 显示完整数据集
     */
    async showFullDataset(filename) {
        try {
            this.notificationManager.info('正在加载数据集...');
            
            const result = await this.apiManager.getFullDataset(filename);
            
            if (result.success) {
                this.uiComponents.showFullDatasetModal(result.data);
                this.notificationManager.success('数据集加载成功');
            } else {
                throw new Error(result.message || '获取数据集失败');
            }
        } catch (error) {
            console.error('获取数据集失败:', error);
            this.notificationManager.error(`获取数据集失败: ${error.message}`);
        }
    }

    /**
     * 刷新任务列表
     */
    refreshTasks() {
        this.loadTasks();
    }

    /**
     * 标签页切换处理
     */
    onTabSwitch(target) {
        switch (target) {
            case '#tasks':
                this.loadTasks();
                break;
            case '#models':
                this.modelManager.loadModels();
                break;
            case '#data':
                this.dataManager.loadQuestions();
                this.dataManager.loadAnswers();
                break;
            case '#comparison':
                this.dataManager.loadModelEvaluations();
                break;
        }
    }

    /**
     * 更新温度显示
     */
    updateTemperatureDisplay() {
        this.uiComponents.updateTemperatureDisplay();
    }

    /**
     * 下载结果
     */
    downloadResults(taskId) {
        this.notificationManager.info('下载功能开发中...');
    }

    /**
     * 显示确认对话框
     */
    async showConfirmDialog(title, message, confirmText = '确认', type = 'primary') {
        return new Promise((resolve) => {
            // 创建模态框
            const modalId = 'confirmModal_' + Date.now();
            const modal = document.createElement('div');
            modal.className = 'modal fade';
            modal.id = modalId;
            modal.innerHTML = `
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">${title}</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <p>${message}</p>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                            <button type="button" class="btn btn-${type}" id="confirmBtn">
                                ${confirmText}
                            </button>
                        </div>
                    </div>
                </div>
            `;

            document.body.appendChild(modal);

            // 绑定事件
            const confirmBtn = modal.querySelector('#confirmBtn');
            const modalElement = new bootstrap.Modal(modal);

            confirmBtn.addEventListener('click', () => {
                modalElement.hide();
                resolve(true);
            });

            modal.addEventListener('hidden.bs.modal', () => {
                document.body.removeChild(modal);
                resolve(false);
            });

            modalElement.show();
        });
    }

}

// 初始化应用
let app;
document.addEventListener('DOMContentLoaded', function() {

    app = new EvaluationApp();
    window.app = app; // 将app实例暴露到全局
});

// 全局函数
window.refreshTasks = async () => {
    await app.loadTasks();
};

window.refreshModelEvaluations = async () => {
    await app.dataManager.loadModelEvaluations();
};

// 测试模态框函数
window.testModal = () => {
    
    
    const modalElement = document.getElementById('taskDetailModal');
    if (!modalElement) {
        console.error('找不到模态框元素');
        return;
    }
    
    // 设置测试内容
    const modalContent = document.getElementById('taskDetailContent');
    if (modalContent) {
        modalContent.innerHTML = `
            <div class="alert alert-success">
                <h4><i class="bi bi-check-circle"></i> 模态框测试</h4>
                <p>如果您能看到这个消息，说明模态框功能正常！</p>
                <hr>
                <p class="mb-0">当前时间: ${new Date().toLocaleString()}</p>
            </div>
        `;
    }
    
    // 显示模态框
    try {
        const modal = new bootstrap.Modal(modalElement, {
            keyboard: true,
            backdrop: true,
            focus: true
        });
        
        modal.show();

        
        // 强制设置样式
        setTimeout(() => {
            modalElement.style.display = 'block';
            modalElement.style.zIndex = '9999';
            modalElement.style.position = 'fixed';
            modalElement.style.top = '10%';
            modalElement.style.left = '50%';
            modalElement.style.transform = 'translateX(-50%)';
            modalElement.style.backgroundColor = 'rgba(255,255,255,0.95)';
            modalElement.style.border = '3px solid red';
            modalElement.style.padding = '20px';
            
    
        }, 100);
        
    } catch (error) {
        console.error('测试模态框失败:', error);
    }
};

// 在新窗口中显示任务详情
window.openTaskDetailWindow = async (taskId) => {
    try {
    
        
        // 获取任务详情
        const response = await app.taskManager.apiManager.getTask(taskId);
        if (!response.success) {
            app.notificationManager.error('获取任务详情失败: ' + (response.message || response.error));
            return;
        }
        
        const task = response.data;
        
        // 生成任务详情HTML
        const detailHtml = app.taskManager.uiComponents.generateTaskDetailHtml(task);
        
        // 创建完整的HTML页面
        const fullHtml = `
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>任务详情 - ${task.task_id}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        body { 
            padding: 20px; 
            background-color: #f8f9fa; 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .main-container { max-width: 1200px; margin: 0 auto; }
        .header { 
            background: linear-gradient(135deg, #007bff, #0056b3); 
            color: white; 
            padding: 20px; 
            border-radius: 10px; 
            margin-bottom: 20px; 
        }
        .content-card { 
            background: white; 
            padding: 30px; 
            border-radius: 10px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1); 
        }
        .close-btn { 
            position: fixed; 
            top: 20px; 
            right: 20px; 
            z-index: 1000; 
        }
        
        /* 表格样式 */
        .table {
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        
        .table thead th {
            background: linear-gradient(135deg, #495057 0%, #343a40 100%) !important;
            color: white !important;
            border: none;
            font-weight: 600;
            padding: 12px 8px;
        }
        
        .table tbody tr:hover {
            background-color: rgba(102, 126, 234, 0.1);
        }
        
        .table td {
            vertical-align: middle;
            padding: 10px 8px;
        }
        
        /* 徽章样式 - 圆润设计 */
        .badge {
            border-radius: 25px !important;
            font-weight: 500;
            padding: 8px 15px !important;
            font-size: 0.85rem !important;
        }
        
        .badge.bg-warning {
            background: linear-gradient(135deg, #f39c12 0%, #f1c40f 100%) !important;
            color: white !important;
        }
        
        .badge.bg-primary {
            background: linear-gradient(135deg, #3498db 0%, #2980b9 100%) !important;
            color: white !important;
        }
        
        .badge.bg-success {
            background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%) !important;
            color: white !important;
        }
        
        .badge.bg-danger {
            background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%) !important;
            color: white !important;
        }
        
        .badge.bg-orange {
            background: linear-gradient(135deg, #fd7e14 0%, #e55a4e 100%) !important;
            color: white !important;
        }
        
        .badge.bg-secondary {
            background: linear-gradient(135deg, #6c757d 0%, #495057 100%) !important;
            color: white !important;
        }
        
        .badge.bg-info {
            background: linear-gradient(135deg, #17a2b8 0%, #138496 100%) !important;
            color: white !important;
        }
        
        .badge.bg-light {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%) !important;
            color: #495057 !important;
        }
        
        /* 大一点的徽章 */
        .badge.fs-5 {
            font-size: 1rem !important;
            padding: 10px 18px !important;
        }
        
        .badge.fs-6 {
            font-size: 0.9rem !important;
            padding: 8px 15px !important;
        }
        
        /* 响应式 */
        @media (max-width: 768px) {
            .badge {
                padding: 6px 12px !important;
                font-size: 0.75rem !important;
            }
        }
    </style>
</head>
<body>
    <div class="main-container">
        <button class="btn btn-outline-secondary close-btn" onclick="window.close()">
            <i class="bi bi-x-lg"></i> 关闭窗口
        </button>
        
        <div class="header">
            <h1><i class="bi bi-info-circle"></i> 任务详情</h1>
            <p class="mb-0">任务ID: <code style="color: #fff; background: rgba(255,255,255,0.2); padding: 2px 6px; border-radius: 4px;">${task.task_id}</code></p>
        </div>
        
        <div class="content-card">
            ${detailHtml}
        </div>
        
        <div class="text-center mt-4">
            <button class="btn btn-primary" onclick="downloadResults()">
                <i class="bi bi-download"></i> 导出结果
            </button>
            <button class="btn btn-secondary ms-2" onclick="window.close()">
                <i class="bi bi-x-circle"></i> 关闭
            </button>
        </div>
    </div>
    
    <script>
        function downloadResults() {
            const task = ${JSON.stringify(task)};
            if (!task.results) {
                alert('没有可导出的结果');
                return;
            }
            
            const data = {
                task_info: {
                    task_id: task.task_id,
                    target_model_name: task.target_model_name,
                    evaluator_model_name: task.evaluator_model_name,
                    created_at: task.created_at,
                    question_file: task.question_file,
                    answer_file: task.answer_file
                },
                results: task.results
            };
            
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'evaluation_results_' + task.task_id + '.json';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
    </script>
</body>
</html>
        `;
        
        // 在新窗口中打开
        const newWindow = window.open('', '_blank', 'width=1200,height=800,scrollbars=yes,resizable=yes');
        if (newWindow) {
            newWindow.document.write(fullHtml);
            newWindow.document.close();
        
        } else {
            // 如果无法打开新窗口，回退到模态框
            console.warn('无法打开新窗口，回退到模态框显示');
            await app.viewTaskDetail(taskId);
        }
        
    } catch (error) {
        console.error('打开任务详情窗口失败:', error);
        app.notificationManager.error('打开任务详情失败: ' + error.message);
    }
};

// 自定义模态框相关函数
let currentCustomModalTask = null;

// 显示自定义模态框
window.showCustomTaskDetail = async (taskId) => {
    try {
    
        
        // 获取任务详情
        const response = await app.taskManager.apiManager.getTask(taskId);
        if (!response.success) {
            app.notificationManager.error('获取任务详情失败: ' + (response.message || response.error));
            return;
        }
        
        const task = response.data;
        currentCustomModalTask = task; // 保存任务数据用于导出
        
        // 生成任务详情HTML
        const detailHtml = app.taskManager.uiComponents.generateTaskDetailHtml(task);
        
        // 更新模态框内容
        const modalContent = document.getElementById('customTaskDetailContent');
        if (modalContent) {
            modalContent.innerHTML = detailHtml;
        }
        
        // 显示模态框
        const modal = document.getElementById('customTaskDetailModal');
        if (modal) {
            modal.classList.add('show');
            document.body.classList.add('modal-open');
        
            
            // 添加点击背景关闭功能
            modal.addEventListener('click', function(e) {
                if (e.target === modal) {
                    closeCustomModal();
                }
            });
        }
        
    } catch (error) {
        console.error('显示自定义模态框失败:', error);
        app.notificationManager.error('显示任务详情失败: ' + error.message);
    }
};

// 关闭自定义模态框
window.closeCustomModal = () => {
    const modal = document.getElementById('customTaskDetailModal');
    if (modal) {
        modal.classList.remove('show');
        document.body.classList.remove('modal-open');

    }
    currentCustomModalTask = null;
};

// 导出自定义模态框的结果
window.downloadCustomModalResults = () => {
    if (!currentCustomModalTask || !currentCustomModalTask.results) {
        app.notificationManager.warning('没有可导出的结果');
        return;
    }
    
    const task = currentCustomModalTask;
    const data = {
        task_info: {
            task_id: task.task_id,
            target_model_name: task.target_model_name,
            evaluator_model_name: task.evaluator_model_name,
            created_at: task.created_at,
            question_file: task.question_file,
            answer_file: task.answer_file
        },
        results: task.results
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `evaluation_results_${task.task_id}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    app.notificationManager.success('结果已导出');
};

// ESC键关闭模态框
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeCustomModal();
    }
}); 