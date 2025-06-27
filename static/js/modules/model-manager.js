/**
 * 模型管理模块
 * 负责模型的加载、添加和管理
 */
class ModelManager {
    constructor(apiManager, uiComponents, notificationManager) {
        this.apiManager = apiManager;
        this.uiComponents = uiComponents;
        this.notificationManager = notificationManager;
        this.models = [];
        
        // 预设API地址配置
        this.baseUrlOptions = {
            qianwen: 'https://dashscope.aliyuncs.com/api/v1',
            custom: ''
        };
        
        this.initializeEventListeners();
    }

    /**
     * 初始化事件监听器
     */
    initializeEventListeners() {
        // 提供商选择变化时切换Base URL字段
        document.getElementById('modelProvider')?.addEventListener('change', (e) => {
            this.toggleBaseUrlField(e.target.value);
        });
    }



    /**
     * 加载模型列表
     */
    async loadModels() {
        try {
            const data = await this.apiManager.getModels();
            
            if (data.success) {
                this.models = data.data;
                this.uiComponents.updateModelSelect(data.data);
                this.uiComponents.updateModelsDisplay(data.data);
                return data.data;
            } else {
                throw new Error(data.message || '获取模型列表失败');
            }
        } catch (error) {
            console.error('加载模型失败:', error);
            this.notificationManager.error('加载模型列表失败');
            throw error;
        }
    }

    /**
     * 添加模型
     */
    async addModel(formData) {
        // 处理通义千问提供商，将其转换为custom类型
        let provider = formData.get('modelProvider');
        let baseUrl = formData.get('baseUrl');
        
        if (provider === 'qianwen') {
            provider = 'custom';
            baseUrl = baseUrl || 'https://dashscope.aliyuncs.com/api/v1';
        }

        const config = {
            name: formData.get('modelName'),
            provider: provider,
            model_id: formData.get('modelId'),
            api_key: formData.get('apiKey') || null,
            base_url: baseUrl || null,
            max_tokens: 4000,
            temperature: 0.7
        };

        // 验证必需字段
        if (!config.name || !config.provider || !config.model_id) {
            throw new Error('请填写所有必需字段：模型名称、提供商和模型ID');
        }

        // 验证API密钥
        if (!config.api_key) {
            throw new Error('请输入API密钥');
        }

        console.log('添加模型配置:', config);

        try {
            const data = await this.apiManager.addModel(config);
            
            if (data.success) {
                this.notificationManager.success('模型添加成功');
                // 重新加载模型列表
                await this.loadModels();
                return data;
            } else {
                throw new Error(data.message || '添加模型失败');
            }
        } catch (error) {
            console.error('添加模型失败:', error);
            this.notificationManager.error('添加模型失败: ' + error.message);
            throw error;
        }
    }

    /**
     * 获取模型列表
     */
    getModels() {
        return this.models;
    }

    /**
     * 根据名称获取模型
     */
    getModelByName(name) {
        return this.models.find(model => model.name === name);
    }

    /**
     * 检查模型是否存在
     */
    hasModel(name) {
        return this.models.some(model => model.name === name);
    }

    /**
     * 删除模型
     */
    async deleteModel(modelName) {
        try {
            const data = await this.apiManager.deleteModel(modelName);
            
            if (data.success) {
                this.notificationManager.success('模型删除成功');
                // 重新加载模型列表
                await this.loadModels();
                return data;
            } else {
                throw new Error(data.message || '删除模型失败');
            }
        } catch (error) {
            console.error('删除模型失败:', error);
            this.notificationManager.error('删除模型失败: ' + error.message);
            throw error;
        }
    }

    /**
     * 切换Base URL字段显示
     */
    toggleBaseUrlField(provider) {
        const baseUrlGroup = document.getElementById('baseUrlGroup');
        const baseUrlInput = document.getElementById('baseUrl');
        
        if (!baseUrlGroup) return;
        
        if (provider === 'custom' || provider === 'qianwen') {
            baseUrlGroup.style.display = 'block';
            if (baseUrlInput) {
                baseUrlInput.required = true;
                // 如果是通义千问，设置默认API地址
                if (provider === 'qianwen') {
                    baseUrlInput.value = this.baseUrlOptions.qianwen;
                }
            }
        } else {
            baseUrlGroup.style.display = 'none';
            if (baseUrlInput) {
                baseUrlInput.required = false;
                baseUrlInput.value = '';
            }
        }
    }
}

export default ModelManager; 