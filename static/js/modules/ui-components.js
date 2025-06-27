import TooltipManager from './tooltip-manager.js';

/**
 * UI组件模块
 * 负责UI元素的更新和渲染
 */
class UIComponents {
    constructor() {
        this.statusClasses = {
            'pending': 'bg-warning',
            'running': 'bg-primary',
            'completed': 'bg-success',
            'failed': 'bg-danger'
        };

        this.statusTexts = {
            'pending': '等待中',
            'running': '运行中',
            'completed': '已完成',
            'failed': '已失败'
        };
        
        // 初始化工具提示管理器
        this.tooltipManager = new TooltipManager();
    }

    /**
     * 更新模型选择下拉框
     */
    updateModelSelect(models) {
        const targetSelect = document.getElementById('targetModelSelect');
        const evaluatorSelect = document.getElementById('evaluatorModelSelect');
        
        if (!targetSelect || !evaluatorSelect) {
            console.warn('模型选择下拉框元素未找到');
            return;
        }
        
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
        if (!container) {
            console.warn('模型容器元素未找到');
            return;
        }
        
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
                                        onclick="app.deleteModel('${model.name.replace(/'/g, '\\\'')}')"
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
     * 获取状态徽章样式
     */
    getStatusBadgeClass(status) {
        return this.statusClasses[status] || 'bg-secondary';
    }

    /**
     * 获取状态文本
     */
    getStatusText(status) {
        return this.statusTexts[status] || '未知';
    }



    /**
     * 更新温度显示
     */
    updateTemperatureDisplay() {
        const temperatureSlider = document.getElementById('temperature');
        const tempValue = document.getElementById('tempValue');
        if (temperatureSlider && tempValue) {
            tempValue.textContent = temperatureSlider.value;
        }
    }

    /**
     * 更新问题集显示
     */
    updateQuestionSets(questionSets) {
        const container = document.getElementById('questionSetsContainer');
        if (!container) {
            console.warn('问题集容器元素未找到');
            return;
        }
        
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
                    <div class="d-flex justify-content-between align-items-start">
                        <div class="flex-grow-1">
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
                        </div>
                        <div class="ms-3">
                            ${!set.error ? `
                                <button class="btn btn-outline-primary btn-sm" 
                                        onclick="app.showFullDataset('${set.filename.replace(/'/g, '\\\'')}')"
                                        title="查看完整数据集">
                                    <i class="bi bi-eye"></i> 查看详情
                                </button>
                            ` : ''}
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }

    /**
     * 更新答案集显示
     */
    updateAnswerSets(answerSets) {
        // 答案集通常不需要单独显示，因为会自动匹配

    }

    /**
     * 显示完整数据集内容
     */
    showFullDatasetModal(dataset) {
        const modal = document.createElement('div');
        modal.className = 'custom-modal show';
        modal.innerHTML = `
            <div class="custom-modal-dialog" style="max-width: 95%;">
                <div class="custom-modal-header">
                    <h5 class="custom-modal-title">
                        <i class="bi bi-database"></i> ${dataset.filename}
                    </h5>
                    <button type="button" class="custom-modal-close" onclick="this.closest('.custom-modal').remove()">
                        <i class="bi bi-x"></i>
                    </button>
                </div>
                <div class="custom-modal-body">
                    <div class="row mb-3">
                        <div class="col-md-3">
                            <div class="card text-center">
                                <div class="card-body">
                                    <h3 class="text-primary">${dataset.question_count}</h3>
                                    <small class="text-muted">问题总数</small>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card text-center">
                                <div class="card-body">
                                    <h3 class="text-success">${dataset.answer_count}</h3>
                                    <small class="text-muted">答案总数</small>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card text-center">
                                <div class="card-body">
                                    <h3 class="text-info">${dataset.type}</h3>
                                    <small class="text-muted">数据集类型</small>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card text-center">
                                <div class="card-body">
                                    <h3 class="${dataset.has_answers ? 'text-success' : 'text-warning'}">${dataset.has_answers ? '有' : '无'}</h3>
                                    <small class="text-muted">标准答案</small>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <ul class="nav nav-tabs" role="tablist">
                        <li class="nav-item" role="presentation">
                            <button class="nav-link active" data-bs-toggle="tab" data-bs-target="#questions-tab" type="button" role="tab">
                                <i class="bi bi-question-circle"></i> 问题集 (${dataset.question_count})
                            </button>
                        </li>
                        ${dataset.has_answers ? `
                            <li class="nav-item" role="presentation">
                                <button class="nav-link" data-bs-toggle="tab" data-bs-target="#answers-tab" type="button" role="tab">
                                    <i class="bi bi-check-circle"></i> 答案集 (${dataset.answer_count})
                                </button>
                            </li>
                        ` : ''}
                    </ul>
                    
                    <div class="tab-content mt-3">
                        <div class="tab-pane fade show active" id="questions-tab" role="tabpanel">
                            ${this.generateQuestionsTable(dataset.questions)}
                        </div>
                        ${dataset.has_answers ? `
                            <div class="tab-pane fade" id="answers-tab" role="tabpanel">
                                ${this.generateAnswersTable(dataset.answers)}
                            </div>
                        ` : ''}
                    </div>
                </div>
                <div class="custom-modal-footer">
                    <button type="button" class="btn btn-secondary" onclick="this.closest('.custom-modal').remove()">
                        关闭
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // 添加标签页切换功能
        modal.querySelectorAll('[data-bs-toggle="tab"]').forEach(tab => {
            tab.addEventListener('click', (e) => {
                e.preventDefault();
                
                // 移除所有active类
                modal.querySelectorAll('.nav-link').forEach(link => link.classList.remove('active'));
                modal.querySelectorAll('.tab-pane').forEach(pane => {
                    pane.classList.remove('show', 'active');
                });
                
                // 添加active类到当前标签
                tab.classList.add('active');
                const targetId = tab.getAttribute('data-bs-target');
                const targetPane = modal.querySelector(targetId);
                if (targetPane) {
                    targetPane.classList.add('show', 'active');
                }
            });
        });
    }

    /**
     * 生成问题表格
     */
    generateQuestionsTable(questions) {
        if (!questions || questions.length === 0) {
            return '<div class="text-center text-muted p-4">暂无问题数据</div>';
        }

        return `
            <div class="table-responsive">
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>问题内容</th>
                            <th>分类</th>
                            <th>难度</th>
                            <th>类型</th>
                            <th>子问题</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${questions.map(q => `
                            <tr>
                                <td><span class="badge bg-primary">${q.id}</span></td>
                                <td>
                                    <div class="question-content" style="max-width: 400px;">
                                        ${this.truncateText(q.question || q.content || '无内容', 150)}
                                    </div>
                                </td>
                                <td><span class="badge bg-secondary">${q.category || '未分类'}</span></td>
                                <td><span class="badge bg-info">${q.difficulty || '未知'}</span></td>
                                <td><span class="badge bg-warning">${q.type || '通用'}</span></td>
                                <td>
                                    ${q.sub_questions && q.sub_questions.length > 0 ? 
                                        `<span class="badge bg-success">${q.sub_questions.length} 个</span>` : 
                                        '<span class="badge bg-light text-dark">无</span>'
                                    }
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    }

    /**
     * 生成答案表格
     */
    generateAnswersTable(answers) {
        if (!answers || answers.length === 0) {
            return '<div class="text-center text-muted p-4">暂无答案数据</div>';
        }

        return `
            <div class="table-responsive">
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>问题ID</th>
                            <th>答案内容</th>
                            <th>类型</th>
                            <th>说明</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${answers.map(a => `
                            <tr>
                                <td><span class="badge bg-primary">${a.question_id}</span></td>
                                <td>
                                    <div class="answer-content" style="max-width: 500px;">
                                        ${this.truncateText(a.answer || a.content || a.standard_answer || '无内容', 200)}
                                    </div>
                                </td>
                                <td><span class="badge bg-success">${a.type || '标准答案'}</span></td>
                                <td>
                                    ${a.explanation ? 
                                        `<small class="text-muted">${this.truncateText(a.explanation, 100)}</small>` : 
                                        '<small class="text-muted">无说明</small>'
                                    }
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    }

    /**
     * 截断文本
     */
    truncateText(text, maxLength) {
        if (!text) return '';
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }

    /**
     * 更新模型评估历史显示
     */
    updateModelEvaluations(evaluations) {
        const container = document.getElementById('modelEvaluationsContainer');
        if (!container) {
            console.warn('模型评估历史容器元素未找到');
            return;
        }
        
        if (evaluations.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted">
                    <i class="bi bi-graph-up fs-1"></i>
                    <p class="mt-2">暂无评估历史</p>
                    <small>完成评估任务后将在此显示历史记录</small>
                </div>
            `;
            return;
        }

        container.innerHTML = `
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead class="table-dark">
                        <tr>
                            <th>模型名称</th>
                            <th>平均分</th>
                            <th>完全满足</th>
                            <th>部分满足</th>
                            <th>未满足</th>
                            <th>Token数</th>
                            <th>总耗时</th>
                            <th>评估模型</th>
                            <th>详情</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${evaluations.map(evaluation => `
                            <tr>
                                <td>
                                    <strong>${evaluation.model_name}</strong>
                                    <br><small class="text-muted">${new Date(evaluation.created_at).toLocaleString()}</small>
                                </td>
                                <td>
                                    <span class="badge ${this.getScoreBadgeClass(evaluation.average_score)} fs-5">
                                        ${evaluation.average_score}
                                    </span>
                                </td>
                                <td>
                                    <span class="badge bg-success">${evaluation.fully_met_requirements}</span>
                                    <small class="text-muted">/${evaluation.total_questions}</small>
                                </td>
                                <td>
                                    <span class="badge bg-warning">${evaluation.partially_met_requirements}</span>
                                    <small class="text-muted">/${evaluation.total_questions}</small>
                                </td>
                                <td>
                                    <span class="badge bg-danger">${evaluation.unmet_requirements}</span>
                                    <small class="text-muted">/${evaluation.total_questions}</small>
                                </td>
                                <td>
                                    <span class="badge bg-info">${evaluation.total_tokens.toLocaleString()}</span>
                                </td>
                                <td>
                                    <span class="badge bg-secondary">${evaluation.total_duration_formatted || '未知'}</span>
                                </td>
                                <td>
                                    <small>${evaluation.evaluator_model || '未知'}</small>
                                </td>
                                <td>
                                    ${evaluation.task_exists ? 
                                        `<button class="btn btn-outline-primary btn-sm" onclick="openTaskDetailWindow('${evaluation.task_id}')">
                                            <i class="bi bi-box-arrow-up-right"></i> 查看详情
                                        </button>` : 
                                        `<span class="text-muted">
                                            <i class="bi bi-archive"></i> 已删除
                                        </span>`
                                    }
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    }

    /**
     * 获取分数对应的徽章样式
     */
    getScoreBadgeClass(score) {
        if (score >= 80) return 'bg-success';
        if (score >= 60) return 'bg-warning';
        if (score >= 40) return 'bg-orange';
        return 'bg-danger';
    }

    /**
     * 切换Base URL字段显示
     */
    toggleBaseUrlField(provider) {
        const baseUrlGroup = document.getElementById('baseUrlGroup');
        if (baseUrlGroup) {
            if (provider === 'custom' || provider === 'agent') {
                baseUrlGroup.style.display = 'block';
            } else {
                baseUrlGroup.style.display = 'none';
            }
        }
    }

    /**
     * 生成任务详情HTML
     */
    generateTaskDetailHtml(task) {
        let resultsHtml = '';
        let detailTableHtml = '';
        
        
        
        if (task.results && task.results.summary) {
            const summary = task.results.summary;
            const results = task.results.results || [];

            
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
                                    <h5 class="card-title text-info">${summary.total_duration_formatted || '未知'}</h5>
                                    <p class="card-text">总耗时</p>
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
                        <div class="table-responsive" style="overflow: visible;">
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
                                                <span class="badge ${this.getScoreBadgeClass(accuracy)} fs-6">
                                                    ${accuracy.toFixed(1)}
                                                </span>
                                            </td>
                                            <td>
                                                <span class="badge ${this.getScoreBadgeClass(completeness)} fs-6">
                                                    ${completeness.toFixed(1)}
                                                </span>
                                            </td>
                                            <td>
                                                <span class="badge ${this.getScoreBadgeClass(clarity)} fs-6">
                                                    ${clarity.toFixed(1)}
                                                </span>
                                            </td>
                                            <td>
                                                <span class="badge ${this.getScoreBadgeClass(overall)} fs-5">
                                                    ${overall.toFixed(1)}
                                                </span>
                                            </td>
                                            <td><small class="text-muted">${tokensUsed}</small></td>
                                            <td>
                                                <button class="btn btn-sm btn-outline-primary" 
                                                        onclick="app.taskManager.showQuestionDetail(${index})"
                                                        title="查看问题详情">
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

        const htmlContent = `
            <div class="mb-4">
                <h6><i class="bi bi-info-circle"></i> 任务信息</h6>
                <div class="row">
                    <div class="col-md-6">
                        <ul class="list-unstyled">
                            <li><strong>任务ID:</strong> <code>${task.task_id}</code></li>
                            <li><strong>待评估模型:</strong> <span class="badge bg-primary">${task.target_model_name || task.model_name}</span></li>
                            <li><strong>${this.tooltipManager.createTooltipElement('评估模型', '评估模型', {}, 'right')}:</strong> <span class="badge bg-success">${task.evaluator_model_name || '程序评估'}</span></li>
                            <li><strong>状态:</strong> <span class="badge ${this.getStatusBadgeClass(task.status)}">${this.getStatusText(task.status)}</span></li>
                        </ul>
                    </div>
                    <div class="col-md-6">
                        <ul class="list-unstyled">
                            <li><strong>创建时间:</strong> ${new Date(task.created_at).toLocaleString()}</li>
                            <li><strong>问题集:</strong> <code>${task.question_file}</code></li>
                            <li><strong>${this.tooltipManager.createTooltipElement('标准答案', '标准答案', {}, 'left')}集:</strong> <code>${task.answer_file}</code></li>
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
            ` : task.status === 'failed' ? `
                <div class="alert alert-danger">
                    <h6><i class="bi bi-exclamation-triangle"></i> 任务执行失败</h6>
                    <p class="mb-0">${task.error || '未知错误'}</p>
                </div>
            ` : task.status === 'running' ? `
                <div class="alert alert-info">
                    <h6><i class="bi bi-arrow-repeat"></i> 任务正在执行中</h6>
                    <p class="mb-0">进度: ${task.progress || 0}%</p>
                </div>
            ` : `
                <div class="alert alert-secondary">
                    <h6><i class="bi bi-clock"></i> 任务等待执行</h6>
                    <p class="mb-0">任务已创建，等待开始执行</p>
                </div>
            `}
        `;
        
        // 异步设置工具提示，在DOM更新后生效
        setTimeout(() => {
            this.setupAdditionalTooltips(task);
        }, 100);
        
        return htmlContent;
    }

    /**
     * 设置额外的工具提示
     * @param {Object} task - 任务数据
     */
    setupAdditionalTooltips(task) {
        // 不再为总分数字添加工具提示，只保留表格标题的工具提示
        // 表格标题的工具提示已在 generateTaskDetailHtml 中处理
        
        // 为其他可能需要工具提示的关键词添加提示（但排除数字）
        const context = {
            hasStandardAnswer: task.answer_file && task.answer_file !== 'N/A'
        };
        
        // 只为文本关键词添加工具提示，不包括数字
        setTimeout(() => {
            // 查找特定的关键词，但不包括数字
            const keywordSelectors = [
                '.badge:contains("程序评估")',
                '.badge:contains("评估模型")',
                'code:contains("答案")'
            ];
            
            keywordSelectors.forEach(selector => {
                try {
                    // 由于CSS选择器不支持:contains，这里用JavaScript手动查找
                    const elements = document.querySelectorAll('.badge, code');
                    elements.forEach(el => {
                        if (el.textContent.includes('程序评估') || el.textContent.includes('评估模型')) {
                            if (!el.classList.contains('tooltip-term') && !el.querySelector('.tooltip-term')) {
                                el.innerHTML = this.tooltipManager.createTooltipElement(
                                    el.textContent, 
                                    '评估模型', 
                                    context, 
                                    'right'
                                );
                            }
                        }
                    });
                } catch (error) {
                    console.warn('添加工具提示时出错:', error);
                }
            });
        }, 200);
    }
}

export default UIComponents; 