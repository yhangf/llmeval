/**
 * 任务管理模块
 * 负责评估任务的创建、监控和管理
 */
class TaskManager {
    constructor(apiManager, uiComponents, notificationManager) {
        this.apiManager = apiManager;
        this.uiComponents = uiComponents;
        this.notificationManager = notificationManager;
        this.currentTask = null;
        this.progressInterval = null;
        this.currentTaskDetail = null;
        this.lastProgress = 0; // 用于防抖动的上次进度值
    }

    /**
     * 创建评估任务
     */
    async createTask(config) {
        try {
            // 验证配置
            if (!config.target_model_name) {
                this.notificationManager.warning('请选择待评估模型');
                return;
            }
            
            if (!config.evaluator_model_name) {
                this.notificationManager.warning('请选择评估模型');
                return;
            }

            const data = await this.apiManager.createTask(config);
            
            if (data.success) {
                this.currentTask = data.data.task_id;
                this.showInlineProgress(this.currentTask, config);
                this.startProgressMonitoring(this.currentTask);
                this.notificationManager.success('评估任务已创建');
                return data.data;
            } else {
                throw new Error(data.message || '创建任务失败');
            }
        } catch (error) {
            console.error('创建任务失败:', error);
            this.notificationManager.error('创建任务失败: ' + error.message);
            throw error;
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
        
        if (!progressSection) {
            console.warn('进度显示元素未找到');
            return;
        }
        
        // 显示进度区域
        progressSection.style.display = 'block';
        
        // 重置进度状态
        this.lastProgress = 0;
        
        // 初始化显示信息
        if (progressTaskInfo) progressTaskInfo.textContent = `任务ID: ${taskId}`;
        if (progressModel) progressModel.textContent = `待评估: ${config.target_model_name} | 评估: ${config.evaluator_model_name}`;
        if (progressPercent) progressPercent.textContent = '0%';
        if (progressBar) {
            progressBar.style.width = '0%';
            progressBar.style.transition = ''; // 清除之前的过渡效果
            progressBar.classList.remove('bg-success', 'bg-danger');
            progressBar.classList.add('progress-bar-animated');
        }
        if (progressStatus) progressStatus.textContent = '准备中...';
        if (currentTask) currentTask.textContent = '等待开始...';
        
        // 滚动到进度区域
        progressSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
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
                const data = await this.apiManager.getTask(taskId);
                
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
                this.notificationManager.error('监控进度失败');
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
            this.notificationManager.success('评估任务完成！');
            
            // 5秒后自动隐藏进度条
            setTimeout(() => {
                this.hideProgress();
            }, 5000);
        } else if (task.status === 'failed') {
            this.notificationManager.error('评估任务失败: ' + (task.error || '未知错误'));
            
            // 3秒后自动隐藏进度条
            setTimeout(() => {
                this.hideProgress();
            }, 3000);
        }
    }

    /**
     * 隐藏进度显示
     */
    hideProgress() {
        const progressSection = document.getElementById('progressSection');
        if (progressSection) {
            progressSection.style.display = 'none';
        }
        this.stopProgressMonitoring();
        
        // 清理完成任务记录
        if (this.completedTasks) {
            this.completedTasks.clear();
        }
    }

    /**
     * 查看任务详情
     */
    async viewTaskDetail(taskId) {
        try {
            const data = await this.apiManager.getTask(taskId);
            
            if (data.success) {
                this.showTaskDetailModal(data.data);
            } else {
                throw new Error(data.message || '获取任务详情失败');
            }
        } catch (error) {
            console.error('查看任务详情失败:', error);
            this.notificationManager.error('查看任务详情失败');
        }
    }

    /**
     * 显示任务详情模态框
     */
    showTaskDetailModal(task) {
        console.log('显示任务详情:', task);
        const content = document.getElementById('taskDetailContent');
        if (!content) {
            console.warn('任务详情内容容器未找到');
            return;
        }
        
        this.currentTaskDetail = task; // 保存当前任务详情，用于导出
        
        let resultsHtml = '';
        let detailTableHtml = '';
        
        if (task.results && task.results.summary) {
            const summary = task.results.summary;
            const results = task.results.results || [];
            
            // 汇总统计
            resultsHtml = this.generateSummaryHtml(summary);
            
            // 详细结果表格
            if (results.length > 0) {
                detailTableHtml = this.generateDetailTableHtml(results);
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
                            <li><strong>状态:</strong> <span class="badge ${this.uiComponents.getStatusBadgeClass(task.status)}">${this.uiComponents.getStatusText(task.status)}</span></li>
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
     * 生成汇总统计HTML
     */
    generateSummaryHtml(summary) {
        return `
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
    }

    /**
     * 生成详细结果表格HTML
     */
    generateDetailTableHtml(results) {
        return `
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
                                <th>完成需求</th>
                                <th>Token数</th>
                                <th>操作</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${results.map((result, index) => {
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
                                
                                // 判断是否完成需求 - 编程题优先检查requirement_completed，其他题目基于总分判断
                                let requirementCompleted = false;
                                if (evaluation.requirement_completed !== undefined) {
                                    // 编程题有专门的需求完成标记
                                    requirementCompleted = evaluation.requirement_completed;
                                } else {
                                    // 其他题目基于总分判断（>=7分算完成需求）
                                    requirementCompleted = overall >= 7.0;
                                }
                                
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
                                        <span class="badge ${this.uiComponents.getScoreBadgeClass(accuracy)}">
                                            ${accuracy.toFixed(1)}
                                        </span>
                                    </td>
                                    <td>
                                        <span class="badge ${this.uiComponents.getScoreBadgeClass(completeness)}">
                                            ${completeness.toFixed(1)}
                                        </span>
                                    </td>
                                    <td>
                                        <span class="badge ${this.uiComponents.getScoreBadgeClass(clarity)}">
                                            ${clarity.toFixed(1)}
                                        </span>
                                    </td>
                                    <td>
                                        <span class="badge ${this.uiComponents.getScoreBadgeClass(overall)} fs-6">
                                            ${overall.toFixed(1)}
                                        </span>
                                    </td>
                                    <td>
                                        <span class="badge ${requirementCompleted ? 'bg-success' : 'bg-danger'}">
                                            ${requirementCompleted ? '✓ 已完成' : '✗ 未完成'}
                                        </span>
                                    </td>
                                    <td><small class="text-muted">${tokensUsed}</small></td>
                                    <td>
                                        <button class="btn btn-sm btn-outline-primary" 
                                                onclick="app.taskManager.showQuestionDetail(${index})">
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

    /**
     * 显示问题详情
     */
    showQuestionDetail(index) {
        if (!this.currentTaskDetail || !this.currentTaskDetail.results) {
            this.notificationManager.error('没有可显示的任务详情');
            return;
        }
        
        const results = this.currentTaskDetail.results.results;
        if (!results || !Array.isArray(results)) {
            this.notificationManager.error('结果数据格式错误');
            return;
        }
        
        const result = results[index];
        if (!result) {
            this.notificationManager.error('找不到指定的问题结果');
            return;
        }
        
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
        
        // 判断是否完成需求
        let requirementCompleted = false;
        if (evaluation.requirement_completed !== undefined) {
            requirementCompleted = evaluation.requirement_completed;
        } else {
            requirementCompleted = overall >= 7.0;
        }

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
                                <div class="col-md-2">
                                    <div class="text-center">
                                        <div class="badge ${this.uiComponents.getScoreBadgeClass(accuracy)} fs-5">
                                            ${accuracy.toFixed(1)}
                                        </div>
                                        <p class="small mt-1">准确性</p>
                                    </div>
                                </div>
                                <div class="col-md-2">
                                    <div class="text-center">
                                        <div class="badge ${this.uiComponents.getScoreBadgeClass(completeness)} fs-5">
                                            ${completeness.toFixed(1)}
                                        </div>
                                        <p class="small mt-1">完整性</p>
                                    </div>
                                </div>
                                <div class="col-md-2">
                                    <div class="text-center">
                                        <div class="badge ${this.uiComponents.getScoreBadgeClass(clarity)} fs-5">
                                            ${clarity.toFixed(1)}
                                        </div>
                                        <p class="small mt-1">清晰度</p>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="text-center">
                                        <div class="badge ${this.uiComponents.getScoreBadgeClass(overall)} fs-4">
                                            ${overall.toFixed(1)}
                                        </div>
                                        <p class="small mt-1">总分</p>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="text-center">
                                        <div class="badge ${requirementCompleted ? 'bg-success' : 'bg-danger'} fs-4">
                                            ${requirementCompleted ? '✓ 已完成' : '✗ 未完成'}
                                        </div>
                                        <p class="small mt-1">完成需求</p>
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
     * 删除任务
     */
    async deleteTask(taskId) {
        if (!confirm('确定要删除这个任务吗？')) {
            return;
        }

        try {
            const data = await this.apiManager.deleteTask(taskId);
            
            if (data.success) {
                this.notificationManager.success('任务已删除');
                return true;
            } else {
                throw new Error(data.message || '删除任务失败');
            }
        } catch (error) {
            console.error('删除任务失败:', error);
            this.notificationManager.error('删除任务失败');
            throw error;
        }
    }

    /**
     * 导出任务结果
     */
    downloadTaskResults() {
        if (!this.currentTaskDetail || !this.currentTaskDetail.results) {
            this.notificationManager.warning('没有可导出的结果');
            return;
        }
        
        const data = {
            task_info: {
                task_id: this.currentTaskDetail.task_id,
                target_model_name: this.currentTaskDetail.target_model_name,
                evaluator_model_name: this.currentTaskDetail.evaluator_model_name,
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
        
        this.notificationManager.success('结果已导出');
    }
}

export default TaskManager; 