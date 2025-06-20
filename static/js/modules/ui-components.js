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
     * 获取分数对应的徽章样式
     */
    getScoreBadgeClass(score) {
        if (score >= 80) return 'bg-success';
        if (score >= 60) return 'bg-warning';
        if (score >= 40) return 'bg-info';
        return 'bg-danger';
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
}

export default UIComponents; 