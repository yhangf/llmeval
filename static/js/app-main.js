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
                max_tokens: parseInt(document.getElementById('maxTokens')?.value || '1000')
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
                </div>
            `;
            return;
        }

        // 按创建时间排序
        tasks.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

        container.innerHTML = tasks.map(task => `
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

}

// 初始化应用
let app;
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM加载完成，初始化模块化应用...');
    app = new EvaluationApp();
    window.app = app; // 将app实例暴露到全局
});

// 全局函数（供HTML调用）
window.refreshTasks = () => {
    if (app) {
        app.refreshTasks();
    }
}; 