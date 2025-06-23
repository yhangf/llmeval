/**
 * 大模型测评系统前端应用
 * 功能：前端交互逻辑，API调用，UI更新
 * 作者：AI助手
 * 创建时间：2024年
 */

/**
 * 已弃用
 * 时间：2025/6/19
 */ 
class EvaluationApp {
    constructor() {
        this.currentTask = null;
        this.progressInterval = null;
        this.lastProgress = 0; // 用于防抖动的上次进度值
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
        document.getElementById('evaluationForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.startEvaluation();
        });

        // 添加模型表单提交
        document.getElementById('addModelForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.addModel();
        });

        // 温度参数滑块
        document.getElementById('temperature').addEventListener('input', (e) => {
            document.getElementById('tempValue').textContent = e.target.value;
        });

        // 模型提供商选择
        document.getElementById('modelProvider').addEventListener('change', (e) => {
            this.toggleBaseUrlField(e.target.value);
        });

        // 问题集选择
        document.getElementById('questionSet').addEventListener('change', (e) => {
            this.loadQuestionPreview(e.target.value);
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
                this.loadModels(),
                this.loadQuestions(),
                this.loadAnswers(),
                this.loadTasks()
            ]);
        } catch (error) {
            console.error('加载初始数据失败:', error);
            this.showNotification('加载数据失败', 'error');
        }
    }

    /**
     * 加载模型列表
     */
    async loadModels() {
        try {
            const response = await fetch('/api/models');
            const data = await response.json();
            
            if (data.success) {
                this.updateModelSelect(data.data);
                this.updateModelsDisplay(data.data);
            } else {
                throw new Error(data.message || '获取模型列表失败');
            }
        } catch (error) {
            console.error('加载模型失败:', error);
            this.showNotification('加载模型列表失败', 'error');
        }
    }

    /**
     * 更新模型选择下拉框
     */
    updateModelSelect(models) {
        const targetSelect = document.getElementById('targetModelSelect');
        const evaluatorSelect = document.getElementById('evaluatorModelSelect');
        
        // 清空现有选项
        targetSelect.innerHTML = '<option value="">请选择待评估模型...</option>';
        evaluatorSelect.innerHTML = '<option value="">请选择评估模型...</option>';
        
        // 添加模型选项到两个下拉框
        models.forEach(model => {
            const targetOption = document.createElement('option');
            targetOption.value = model.name;
            targetOption.textContent = `${model.name} (${model.type})`;
            targetSelect.appendChild(targetOption);
            
            const evaluatorOption = document.createElement('option');
            evaluatorOption.value = model.name;
            evaluatorOption.textContent = `${model.name} (${model.type})`;
            evaluatorSelect.appendChild(evaluatorOption);
        });
    }

    /**
     * 更新模型显示
     */
    updateModelsDisplay(models) {
        const container = document.getElementById('modelsContainer');
        
        if (models.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted">
                    <i class="bi bi-inbox fs-1"></i>
                    <p class="mt-2">暂无配置的模型</p>
                </div>
            `;
            return;
        }

        container.innerHTML = models.map(model => `
            <div class="card model-card model-type-${model.type.toLowerCase()}">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <h6 class="card-title mb-1">${model.name}</h6>
                            <small class="text-muted">${model.model_id}</small>
                            <div class="mt-2">
                                <span class="badge bg-secondary">${model.type}</span>
                            </div>
                        </div>
                        <div class="text-end">
                            <small class="text-muted">Token: ${model.stats.token_count}</small><br>
                            <small class="text-muted">请求: ${model.stats.request_count}</small>
                            <div class="mt-2">
                                <button class="btn btn-outline-danger btn-sm" 
                                        onclick="deleteModel('${model.name.replace(/'/g, '\\\'')}')"
                                        title="删除模型">
                                    <i class="bi bi-trash"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }

    /**
     * 加载问题集
     */
    async loadQuestions() {
        try {
            const response = await fetch('/api/questions');
            const data = await response.json();
            
            if (data.success) {
                this.updateQuestionSets(data.data);
            } else {
                throw new Error(data.message || '获取问题集失败');
            }
        } catch (error) {
            console.error('加载问题集失败:', error);
            this.showNotification('加载问题集失败', 'error');
        }
    }

    /**
     * 加载答案集
     */
    async loadAnswers() {
        try {
            const response = await fetch('/api/answers');
            const data = await response.json();
            
            if (data.success) {
                this.updateAnswerSets(data.data);
            } else {
                throw new Error(data.message || '获取答案集失败');
            }
        } catch (error) {
            console.error('加载答案集失败:', error);
            this.showNotification('加载答案集失败', 'error');
        }
    }

    /**
     * 更新问题集显示
     */
    updateQuestionSets(questionSets) {
        const questionSelect = document.getElementById('questionSet');
        const container = document.getElementById('questionSetsContainer');
        
        // 保存问题集数据供后续使用
        this.questionSets = questionSets;
        
        // 更新下拉框
        questionSelect.innerHTML = '';
        questionSets.forEach(set => {
            const option = document.createElement('option');
            option.value = set.filename;
            option.textContent = `${set.name || set.filename} (${set.count}题) - ${set.type || '通用'}`;
            questionSelect.appendChild(option);
        });
        
        // 如果有问题集，默认选择第一个并显示预览
        if (questionSets.length > 0) {
            this.updateQuestionPreview(questionSets[0].preview);
        }

        // 更新显示容器
        if (questionSets.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted">
                    <i class="bi bi-file-text fs-1"></i>
                    <p class="mt-2">暂无问题集</p>
                </div>
            `;
            return;
        }

        container.innerHTML = questionSets.map(set => `
            <div class="card mb-3">
                <div class="card-body">
                    <h6 class="card-title">${set.name || set.filename}</h6>
                    <p class="card-text">
                        <span class="badge bg-primary">${set.count} 题</span>
                        <span class="badge bg-secondary ms-2">${set.type || '通用'}</span>
                        ${set.error ? `<span class="badge bg-danger ms-2">读取错误</span>` : ''}
                    </p>
                    ${set.error ? `
                        <div class="alert alert-warning mt-2">
                            <small>错误信息: ${set.error}</small>
                        </div>
                    ` : ''}
                    <div class="mt-2">
                        ${set.preview && set.preview.length > 0 ? set.preview.map(q => `
                            <div class="question-item">
                                <small><strong>Q${q.id}:</strong> ${(q.question || q.content || '无内容').substring(0, 50)}...</small>
                            </div>
                        `).join('') : '<small class="text-muted">暂无预览</small>'}
                    </div>
                </div>
            </div>
        `).join('');
    }

    /**
     * 更新答案集显示
     */
    updateAnswerSets(answerSets) {
        const answerSelect = document.getElementById('answerSet');
        const container = document.getElementById('answerSetsContainer');
        
        // 更新下拉框
        answerSelect.innerHTML = '';
        answerSets.forEach(set => {
            const option = document.createElement('option');
            option.value = set.filename;
            option.textContent = `${set.name || set.filename} (${set.count}答案) - ${set.type || '通用'}`;
            answerSelect.appendChild(option);
        });

        // 更新显示容器
        if (answerSets.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted">
                    <i class="bi bi-file-check fs-1"></i>
                    <p class="mt-2">暂无答案集</p>
                </div>
            `;
            return;
        }

        container.innerHTML = answerSets.map(set => `
            <div class="card mb-3">
                <div class="card-body">
                    <h6 class="card-title">${set.name || set.filename}</h6>
                    <p class="card-text">
                        <span class="badge bg-success">${set.count} 答案</span>
                        <span class="badge bg-secondary ms-2">${set.type || '通用'}</span>
                        ${set.error ? `<span class="badge bg-danger ms-2">读取错误</span>` : ''}
                    </p>
                    ${set.error ? `
                        <div class="alert alert-warning mt-2">
                            <small>错误信息: ${set.error}</small>
                        </div>
                    ` : ''}
                    <div class="mt-2">
                        ${set.preview && set.preview.length > 0 ? set.preview.map(a => `
                            <div class="question-item">
                                <small><strong>A${a.question_id}:</strong> ${(a.answer || a.content || '无内容').substring(0, 50)}...</small>
                            </div>
                        `).join('') : '<small class="text-muted">暂无预览</small>'}
                    </div>
                </div>
            </div>
        `).join('');
    }

    /**
     * 加载问题预览
     */
    async loadQuestionPreview(filename) {
        if (!filename) {
            this.updateQuestionPreview([]);
            return;
        }
        
        try {
            // 首先检查是否已经有缓存的问题集数据
            if (this.questionSets) {
                const questionSet = this.questionSets.find(set => set.filename === filename);
                if (questionSet) {
                    this.updateQuestionPreview(questionSet.preview);
                    return;
                }
            }
            
            // 如果没有缓存，重新请求数据
            const response = await fetch('/api/questions');
            const data = await response.json();
            
            if (data.success) {
                const questionSet = data.data.find(set => set.filename === filename);
                if (questionSet) {
                    this.updateQuestionPreview(questionSet.preview);
                } else {
                    this.updateQuestionPreview([]);
                }
            } else {
                this.updateQuestionPreview([]);
            }
        } catch (error) {
            console.error('加载问题预览失败:', error);
            this.updateQuestionPreview([]);
        }
    }

    /**
     * 更新问题预览
     */
    updateQuestionPreview(questions) {
        const container = document.getElementById('questionPreview');
        
        if (!questions || questions.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted">
                    <i class="bi bi-question-circle fs-1"></i>
                    <p class="mt-2">暂无问题预览</p>
                </div>
            `;
            return;
        }

        container.innerHTML = `
            <div class="question-preview">
                ${questions.map(q => `
                    <div class="question-item">
                        <div class="d-flex justify-content-between align-items-start">
                            <div>
                                <h6 class="mb-1">问题 ${q.id}</h6>
                                <p class="mb-1">${q.question || q.content || '无问题内容'}</p>
                                <small class="text-muted">
                                    分类: ${q.category || '未分类'} | 难度: ${q.difficulty || '未知'}
                                </small>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    /**
     * 加载任务列表
     */
    async loadTasks() {
        try {
            const response = await fetch('/api/tasks');
            const data = await response.json();
            
            if (data.success) {
                this.updateTasksDisplay(data.data);
            } else {
                throw new Error(data.message || '获取任务列表失败');
            }
        } catch (error) {
            console.error('加载任务列表失败:', error);
            this.showNotification('加载任务列表失败', 'error');
        }
    }

    /**
     * 更新任务显示
     */
    updateTasksDisplay(tasks) {
        const container = document.getElementById('tasksContainer');
        
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
                                <span class="badge ${this.getStatusBadgeClass(task.status)}">${this.getStatusText(task.status)}</span>
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
     * 开始评估
     */
    async startEvaluation() {
        const form = document.getElementById('evaluationForm');
        const formData = new FormData(form);
        
        const config = {
            target_model_name: document.getElementById('targetModelSelect').value,
            evaluator_model_name: document.getElementById('evaluatorModelSelect').value,
            question_file: document.getElementById('questionSet').value,
            answer_file: document.getElementById('answerSet').value,
            config: {
                temperature: parseFloat(document.getElementById('temperature').value),
                max_tokens: parseInt(document.getElementById('maxTokens').value)
            }
        };

        if (!config.target_model_name) {
            this.showNotification('请选择待评估模型', 'warning');
            return;
        }
        
        if (!config.evaluator_model_name) {
            this.showNotification('请选择评估模型', 'warning');
            return;
        }

        try {
            const response = await fetch('/api/tasks', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(config)
            });

            const data = await response.json();
            
            if (data.success) {
                this.currentTask = data.data.task_id;
                this.showInlineProgress(this.currentTask, config);
                this.startProgressMonitoring(this.currentTask);
                this.showNotification('评估任务已创建', 'success');
            } else {
                throw new Error(data.message || '创建任务失败');
            }
        } catch (error) {
            console.error('开始评估失败:', error);
            this.showNotification('开始评估失败: ' + error.message, 'error');
        }
    }

    /**
     * 显示内联进度
     */
    showInlineProgress(taskId, config) {
        const progressSection = document.getElementById('progressSection');
        const progressTaskInfo = document.getElementById('progressTaskInfo');
        const progressModel = document.getElementById('progressModel');
        const progressPercent = document.getElementById('progressPercent');
        const progressBar = document.getElementById('progressBar');
        const progressStatus = document.getElementById('progressStatus');
        const currentTask = document.getElementById('currentTask');
        
        // 显示进度区域
        progressSection.style.display = 'block';
        
        // 重置进度状态
        this.lastProgress = 0;
        
        // 初始化显示信息
        progressTaskInfo.textContent = `任务ID: ${taskId}`;
        progressModel.textContent = `待评估: ${config.target_model_name} | 评估: ${config.evaluator_model_name}`;
        progressPercent.textContent = '0%';
        progressBar.style.width = '0%';
        progressBar.style.transition = ''; // 清除之前的过渡效果
        progressBar.classList.remove('bg-success', 'bg-danger');
        progressBar.classList.add('progress-bar-animated');
        progressStatus.textContent = '准备中...';
        currentTask.textContent = '等待开始...';
        
        // 滚动到进度区域
        progressSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    /**
     * 隐藏进度显示
     */
    hideProgress() {
        const progressSection = document.getElementById('progressSection');
        progressSection.style.display = 'none';
        this.stopProgressMonitoring();
        
        // 清理完成任务记录
        if (this.completedTasks) {
            this.completedTasks.clear();
        }
    }

    /**
     * 开始进度监控
     */
    startProgressMonitoring(taskId) {
        // 停止之前的监控（如果存在）
        this.stopProgressMonitoring();
        
        // 清理完成任务记录，为新任务做准备
        if (this.completedTasks) {
            this.completedTasks.clear();
        }
        
        this.progressInterval = setInterval(async () => {
            try {
                const response = await fetch(`/api/tasks/${taskId}`);
                const data = await response.json();
                
                if (data.success) {
                    const task = data.data;
                    this.updateProgress(task);
                    
                    if (task.status === 'completed' || task.status === 'failed') {
                        this.stopProgressMonitoring();
                        this.handleTaskCompletion(task);
                    }
                } else {
                    throw new Error(data.message || '获取任务状态失败');
                }
            } catch (error) {
                console.error('监控进度失败:', error);
                this.stopProgressMonitoring();
                this.showNotification('监控进度失败', 'error');
            }
        }, 2000);
    }

    /**
     * 停止进度监控
     */
    stopProgressMonitoring() {
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
            this.progressInterval = null;
        }
    }

    /**
     * 更新进度显示
     */
    updateProgress(task) {
        const progress = task.progress || 0;
        const progressPercent = document.getElementById('progressPercent');
        const progressBar = document.getElementById('progressBar');
        const progressStatus = document.getElementById('progressStatus');
        const currentTask = document.getElementById('currentTask');
        
        // 防抖动逻辑：只有进度实际变化时才更新
        if (this.lastProgress !== progress) {
            // 平滑进度更新：确保进度只能递增，不能回退
            const smoothProgress = Math.max(this.lastProgress || 0, progress);
            this.lastProgress = smoothProgress;
            
            if (progressPercent) progressPercent.textContent = `${smoothProgress}%`;
            if (progressBar) {
                // 添加CSS过渡效果
                progressBar.style.transition = 'width 0.3s ease-in-out';
                progressBar.style.width = `${smoothProgress}%`;
            }
        }
        
        let statusText = '';
        let currentTaskText = '';
        
        switch (task.status) {
            case 'pending':
                statusText = '等待执行...';
                currentTaskText = '准备中...';
                break;
            case 'running':
                statusText = '正在评估...';
                if (task.current_question) {
                    currentTaskText = `正在处理第 ${task.current_question} 题`;
                } else {
                    currentTaskText = `进度 ${progress}%`;
                }
                break;
            case 'completed':
                statusText = '评估完成';
                currentTaskText = '所有题目已完成';
                // 确保完成时进度为100%
                this.lastProgress = 100;
                if (progressPercent) progressPercent.textContent = '100%';
                if (progressBar) {
                    progressBar.style.width = '100%';
                    progressBar.classList.remove('progress-bar-animated');
                    progressBar.classList.add('bg-success');
                }
                break;
            case 'failed':
                statusText = '评估失败';
                currentTaskText = task.error || '执行出错';
                if (progressBar) {
                    progressBar.classList.remove('progress-bar-animated');
                    progressBar.classList.add('bg-danger');
                }
                break;
            default:
                statusText = '未知状态';
                currentTaskText = '状态未知';
        }
        
        if (progressStatus) progressStatus.textContent = statusText;
        if (currentTask) currentTask.textContent = currentTaskText;
    }

    /**
     * 处理任务完成
     */
    handleTaskCompletion(task) {
        // 防止重复通知：检查是否已经处理过这个任务的完成状态
        if (this.completedTasks && this.completedTasks.has(task.task_id)) {
            return;
        }
        
        // 记录已完成的任务
        if (!this.completedTasks) {
            this.completedTasks = new Set();
        }
        this.completedTasks.add(task.task_id);
        
        if (task.status === 'completed') {
            this.showNotification('评估任务完成！', 'success');
            this.loadTasks(); // 刷新任务列表
            
            // 5秒后自动隐藏进度条
            setTimeout(() => {
                this.hideProgress();
            }, 5000);
        } else if (task.status === 'failed') {
            this.showNotification('评估任务失败: ' + (task.error || '未知错误'), 'error');
            
            // 3秒后自动隐藏进度条
            setTimeout(() => {
                this.hideProgress();
            }, 3000);
        }
    }

    /**
     * 查看任务详情
     */
    async viewTaskDetail(taskId) {
        try {
            const response = await fetch(`/api/tasks/${taskId}`);
            const data = await response.json();
            
            if (data.success) {
                this.showTaskDetailModal(data.data);
            } else {
                throw new Error(data.message || '获取任务详情失败');
            }
        } catch (error) {
            console.error('查看任务详情失败:', error);
            this.showNotification('查看任务详情失败', 'error');
        }
    }

    /**
     * 显示任务详情模态框
     */
    showTaskDetailModal(task) {
        console.log('显示任务详情:', task);
        const content = document.getElementById('taskDetailContent');
        this.currentTaskDetail = task; // 保存当前任务详情，用于导出
        
        let resultsHtml = '';
        let detailTableHtml = '';
        
        console.log('任务状态:', task.status);
        console.log('任务结果:', task.results);
        
        if (task.results && task.results.summary) {
            const summary = task.results.summary;
            const results = task.results.results || [];
            console.log('汇总信息:', summary);
            console.log('详细结果数量:', results.length);
            
            // 汇总统计
            resultsHtml = `
                <div class="row mb-4">
                    <div class="col-md-4">
                        <div class="card bg-light">
                            <div class="card-body text-center">
                                <h5 class="card-title text-primary">${summary.total_questions}</h5>
                                <p class="card-text">总问题数</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card bg-light">
                            <div class="card-body text-center">
                                <h5 class="card-title text-info">${summary.total_tokens}</h5>
                                <p class="card-text">总Token数</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card bg-light">
                            <div class="card-body text-center">
                                <h5 class="card-title text-success">${Math.round(summary.average_tokens_per_question)}</h5>
                                <p class="card-text">平均Token/题</p>
                            </div>
                        </div>
                    </div>
                </div>
                
                ${summary.score_statistics && summary.score_statistics.overall ? `
                    <div class="row mb-4">
                        <div class="col-md-3">
                            <div class="card border-success">
                                <div class="card-body text-center">
                                    <h5 class="card-title text-success">${(summary.score_statistics.overall.mean || 0).toFixed(1)}</h5>
                                    <p class="card-text">平均分</p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card border-primary">
                                <div class="card-body text-center">
                                    <h5 class="card-title text-primary">${(summary.score_statistics.overall.max || 0).toFixed(1)}</h5>
                                    <p class="card-text">最高分</p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card border-warning">
                                <div class="card-body text-center">
                                    <h5 class="card-title text-warning">${(summary.score_statistics.overall.min || 0).toFixed(1)}</h5>
                                    <p class="card-text">最低分</p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card border-info">
                                <div class="card-body text-center">
                                    <h5 class="card-title text-info">${(summary.score_statistics.overall.std || 0).toFixed(1)}</h5>
                                    <p class="card-text">标准差</p>
                                </div>
                            </div>
                        </div>
                    </div>
                ` : '<div class="alert alert-info">暂无评分统计数据</div>'}
            `;
            
            // 详细结果表格
            if (results.length > 0) {
                detailTableHtml = `
                    <div class="mt-4">
                        <h6><i class="bi bi-table"></i> 详细评估结果</h6>
                        <div class="table-responsive">
                            <table class="table table-striped table-hover">
                                <thead class="table-dark">
                                    <tr>
                                        <th>题号</th>
                                        <th>问题</th>
                                        <th>准确性</th>
                                        <th>完整性</th>
                                        <th>清晰度</th>
                                        <th>总分</th>
                                        <th>Token数</th>
                                        <th>操作</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${results.map((result, index) => {
                                        console.log(`处理结果 ${index}:`, result);
                                        
                                        // 安全检查
                                        const questionId = result.question_id || 'N/A';
                                        const question = result.question || '无问题内容';
                                        const tokensUsed = result.tokens_used || 0;
                                        
                                        // 检查评估结果
                                        const evaluation = result.evaluation || {};
                                        const scores = evaluation.scores || {};
                                        const accuracy = scores.accuracy || 0;
                                        const completeness = scores.completeness || 0;
                                        const clarity = scores.clarity || 0;
                                        const overall = scores.overall || 0;
                                        
                                        return `
                                        <tr>
                                            <td><span class="badge bg-secondary">${questionId}</span></td>
                                            <td>
                                                <div class="text-truncate" style="max-width: 200px;" 
                                                     title="${question.replace(/"/g, '&quot;')}">
                                                    ${question}
                                                </div>
                                            </td>
                                            <td>
                                                <span class="badge ${this.getScoreBadgeClass(accuracy)}">
                                                    ${accuracy.toFixed(1)}
                                                </span>
                                            </td>
                                            <td>
                                                <span class="badge ${this.getScoreBadgeClass(completeness)}">
                                                    ${completeness.toFixed(1)}
                                                </span>
                                            </td>
                                            <td>
                                                <span class="badge ${this.getScoreBadgeClass(clarity)}">
                                                    ${clarity.toFixed(1)}
                                                </span>
                                            </td>
                                            <td>
                                                <span class="badge ${this.getScoreBadgeClass(overall)} fs-6">
                                                    ${overall.toFixed(1)}
                                                </span>
                                            </td>
                                            <td><small class="text-muted">${tokensUsed}</small></td>
                                            <td>
                                                <button class="btn btn-sm btn-outline-primary" 
                                                        onclick="app.showQuestionDetail(${index})">
                                                    <i class="bi bi-eye"></i>
                                                </button>
                                            </td>
                                        </tr>
                                        `;
                                    }).join('')}
                                </tbody>
                            </table>
                        </div>
                    </div>
                `;
            }
        }

        content.innerHTML = `
            <div class="mb-4">
                <h6><i class="bi bi-info-circle"></i> 任务信息</h6>
                <div class="row">
                    <div class="col-md-6">
                        <ul class="list-unstyled">
                            <li><strong>任务ID:</strong> <code>${task.task_id}</code></li>
                            <li><strong>待评估模型:</strong> <span class="badge bg-primary">${task.target_model_name || task.model_name}</span></li>
                            <li><strong>评估模型:</strong> <span class="badge bg-success">${task.evaluator_model_name || '程序评估'}</span></li>
                            <li><strong>状态:</strong> <span class="badge ${this.getStatusBadgeClass(task.status)}">${this.getStatusText(task.status)}</span></li>
                        </ul>
                    </div>
                    <div class="col-md-6">
                        <ul class="list-unstyled">
                            <li><strong>创建时间:</strong> ${new Date(task.created_at).toLocaleString()}</li>
                            <li><strong>问题集:</strong> <code>${task.question_file}</code></li>
                            <li><strong>答案集:</strong> <code>${task.answer_file}</code></li>
                        </ul>
                    </div>
                </div>
            </div>
            
            ${task.status === 'completed' && resultsHtml ? `
                <div class="mb-4">
                    <h6><i class="bi bi-bar-chart"></i> 评估结果汇总</h6>
                    ${resultsHtml}
                </div>
                ${detailTableHtml}
            ` : ''}
            
            ${task.error ? `
                <div class="mb-3">
                    <h6><i class="bi bi-exclamation-triangle"></i> 错误信息</h6>
                    <div class="alert alert-danger">${task.error}</div>
                </div>
            ` : ''}
        `;

        const modal = new bootstrap.Modal(document.getElementById('taskDetailModal'));
        modal.show();
    }

    /**
     * 删除任务
     */
    async deleteTask(taskId) {
        if (!confirm('确定要删除这个任务吗？')) {
            return;
        }

        try {
            const response = await fetch(`/api/tasks/${taskId}`, {
                method: 'DELETE'
            });

            const data = await response.json();
            
            if (data.success) {
                this.showNotification('任务已删除', 'success');
                this.loadTasks();
            } else {
                throw new Error(data.message || '删除任务失败');
            }
        } catch (error) {
            console.error('删除任务失败:', error);
            this.showNotification('删除任务失败', 'error');
        }
    }

    /**
     * 添加模型
     */
    async addModel() {
        const form = document.getElementById('addModelForm');
        const formData = new FormData(form);
        
        const config = {
            name: formData.get('modelName'),
            provider: formData.get('modelProvider'),
            model_id: formData.get('modelId'),
            api_key: formData.get('apiKey') || null,
            base_url: formData.get('baseUrl') || null,
            max_tokens: 4000,
            temperature: 0.7
        };

        // 验证必需字段
        if (!config.name || !config.provider || !config.model_id) {
            this.showNotification('请填写所有必需字段：模型名称、提供商和模型ID', 'error');
            return;
        }

        try {
            const response = await fetch('/api/models', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(config)
            });

            const data = await response.json();
            
            if (data.success) {
                this.showNotification('模型添加成功', 'success');
                form.reset();
                this.loadModels();
            } else {
                throw new Error(data.message || '添加模型失败');
            }
        } catch (error) {
            console.error('添加模型失败:', error);
            this.showNotification('添加模型失败: ' + error.message, 'error');
        }
    }

    /**
     * 切换Base URL字段显示
     */
    toggleBaseUrlField(provider) {
        const baseUrlGroup = document.getElementById('baseUrlGroup');
        if (provider === 'custom' || provider === 'agent') {
            baseUrlGroup.style.display = 'block';
        } else {
            baseUrlGroup.style.display = 'none';
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
                this.loadModels();
                break;
            case '#data':
                this.loadQuestions();
                this.loadAnswers();
                break;
        }
    }

    /**
     * 更新温度显示
     */
    updateTemperatureDisplay() {
        const tempSlider = document.getElementById('temperature');
        const tempValue = document.getElementById('tempValue');
        tempValue.textContent = tempSlider.value;
    }

    /**
     * 获取状态徽章样式
     */
    getStatusBadgeClass(status) {
        const statusClasses = {
            'pending': 'bg-warning',
            'running': 'bg-primary',
            'completed': 'bg-success',
            'failed': 'bg-danger'
        };
        return statusClasses[status] || 'bg-secondary';
    }

    /**
     * 获取状态文本
     */
    getStatusText(status) {
        const statusTexts = {
            'pending': '等待中',
            'running': '运行中',
            'completed': '已完成',
            'failed': '已失败'
        };
        return statusTexts[status] || '未知';
    }

    /**
     * 显示通知
     */
    showNotification(message, type = 'info') {
        const toast = document.getElementById('notificationToast');
        const toastMessage = document.getElementById('toastMessage');
        
        // 设置图标和样式
        const icons = {
            'success': 'bi-check-circle-fill text-success',
            'error': 'bi-x-circle-fill text-danger',
            'warning': 'bi-exclamation-triangle-fill text-warning',
            'info': 'bi-info-circle-fill text-primary'
        };
        
        const icon = icons[type] || icons.info;
        const header = toast.querySelector('.toast-header i');
        header.className = `${icon} me-2`;
        
        toastMessage.textContent = message;
        
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
    }

    /**
     * 获取分数对应的徽章样式
     */
    getScoreBadgeClass(score) {
        if (score >= 80) return 'bg-success';
        if (score >= 60) return 'bg-warning';
        if (score >= 40) return 'bg-info';
        return 'bg-danger';
    }

    /**
     * 显示问题详情
     */
    showQuestionDetail(index) {
        console.log('显示问题详情，索引:', index);
        console.log('当前任务详情:', this.currentTaskDetail);
        
        if (!this.currentTaskDetail || !this.currentTaskDetail.results) {
            console.error('没有任务详情或结果数据');
            this.showNotification('没有可显示的任务详情', 'error');
            return;
        }
        
        const results = this.currentTaskDetail.results.results;
        if (!results || !Array.isArray(results)) {
            console.error('结果数据格式错误:', results);
            this.showNotification('结果数据格式错误', 'error');
            return;
        }
        
        const result = results[index];
        if (!result) {
            console.error('找不到指定索引的结果:', index, '总数:', results.length);
            this.showNotification('找不到指定的问题结果', 'error');
            return;
        }
        
        console.log('问题结果:', result);
        
        // 安全获取数据
        const questionId = result.question_id || 'N/A';
        const question = result.question || '无问题内容';
        const modelResponse = result.model_response || '无模型回答';
        const referenceAnswer = result.reference_answer || '无参考答案';
        const tokensUsed = result.tokens_used || 0;
        const timestamp = result.timestamp || new Date().toISOString();
        
        // 安全获取评估数据
        const evaluation = result.evaluation || {};
        const scores = evaluation.scores || {};
        const feedback = evaluation.feedback || '无评估反馈';
        
        const accuracy = scores.accuracy || 0;
        const completeness = scores.completeness || 0;
        const clarity = scores.clarity || 0;
        const overall = scores.overall || 0;

        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">问题详情 - 第${questionId}题</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="mb-3">
                            <h6><i class="bi bi-question-circle"></i> 问题</h6>
                            <div class="card bg-light">
                                <div class="card-body">${question}</div>
                            </div>
                        </div>
                        
                        <div class="mb-3">
                            <h6><i class="bi bi-robot"></i> 模型回答</h6>
                            <div class="card border-primary">
                                <div class="card-body">
                                    <pre class="mb-0" style="white-space: pre-wrap;">${modelResponse}</pre>
                                </div>
                            </div>
                        </div>
                        
                        <div class="mb-3">
                            <h6><i class="bi bi-check-circle"></i> 参考答案</h6>
                            <div class="card border-success">
                                <div class="card-body">
                                    <pre class="mb-0" style="white-space: pre-wrap;">${referenceAnswer}</pre>
                                </div>
                            </div>
                        </div>
                        
                        <div class="mb-3">
                            <h6><i class="bi bi-bar-chart"></i> 评分详情</h6>
                            <div class="row">
                                <div class="col-md-3">
                                    <div class="text-center">
                                        <div class="badge ${this.getScoreBadgeClass(accuracy)} fs-5">
                                            ${accuracy.toFixed(1)}
                                        </div>
                                        <p class="small mt-1">准确性</p>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="text-center">
                                        <div class="badge ${this.getScoreBadgeClass(completeness)} fs-5">
                                            ${completeness.toFixed(1)}
                                        </div>
                                        <p class="small mt-1">完整性</p>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="text-center">
                                        <div class="badge ${this.getScoreBadgeClass(clarity)} fs-5">
                                            ${clarity.toFixed(1)}
                                        </div>
                                        <p class="small mt-1">清晰度</p>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="text-center">
                                        <div class="badge ${this.getScoreBadgeClass(overall)} fs-4">
                                            ${overall.toFixed(1)}
                                        </div>
                                        <p class="small mt-1">总分</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="mb-3">
                            <h6><i class="bi bi-chat-dots"></i> 评估反馈</h6>
                            <div class="alert alert-info">
                                ${feedback}
                            </div>
                        </div>
                        
                        <div class="row">
                            <div class="col-md-6">
                                <small class="text-muted">
                                    <i class="bi bi-cpu"></i> Token消耗: ${tokensUsed}
                                </small>
                            </div>
                            <div class="col-md-6">
                                <small class="text-muted">
                                    <i class="bi bi-clock"></i> 时间: ${new Date(timestamp).toLocaleString()}
                                </small>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">关闭</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
        
        // 模态框关闭后移除DOM元素
        modal.addEventListener('hidden.bs.modal', () => {
            document.body.removeChild(modal);
        });
    }

    /**
     * 导出任务结果
     */
    downloadTaskResults() {
        if (!this.currentTaskDetail || !this.currentTaskDetail.results) {
            this.showNotification('没有可导出的结果', 'warning');
            return;
        }
        
        const data = {
            task_info: {
                task_id: this.currentTaskDetail.task_id,
                model_name: this.currentTaskDetail.model_name,
                created_at: this.currentTaskDetail.created_at,
                question_file: this.currentTaskDetail.question_file,
                answer_file: this.currentTaskDetail.answer_file
            },
            results: this.currentTaskDetail.results
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `evaluation_results_${this.currentTaskDetail.task_id}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.showNotification('结果已导出', 'success');
    }

    /**
     * 下载结果
     */
    downloadResults(taskId) {
        // 这里可以实现结果下载功能
        this.showNotification('下载功能开发中...', 'info');
    }
}

// 初始化应用
let app;
document.addEventListener('DOMContentLoaded', function() {
    app = new EvaluationApp();
});

// 全局函数（供HTML调用）
window.refreshTasks = () => app.refreshTasks();
window.app = app;

window.deleteModel = async function(modelName) {
    // 显示确认对话框
    const confirmed = confirm(`确定要删除模型 "${modelName}" 吗？此操作无法撤销。`);
    
    if (!confirmed) {
        return;
    }

    try {
        const response = await fetch(`/api/models/${encodeURIComponent(modelName)}`, {
            method: 'DELETE'
        });

        const data = await response.json();
        
        if (data.success) {
            app.showNotification('模型删除成功', 'success');
            app.loadModels(); // 重新加载模型列表
        } else {
            throw new Error(data.message || '删除模型失败');
        }
    } catch (error) {
        console.error('删除模型失败:', error);
        app.showNotification('删除模型失败: ' + error.message, 'error');
    }
}; 