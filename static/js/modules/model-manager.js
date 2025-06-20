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
        // 调试：检查FormData内容
        console.log('FormData内容:');
        for (let [key, value] of formData.entries()) {
            console.log(`  ${key}: "${value}"`);
        }

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
            throw new Error('请填写所有必需字段：模型名称、提供商和模型ID');
        }

        // 调试：打印发送的配置
        console.log('准备发送的模型配置:', config);

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
        this.uiComponents.toggleBaseUrlField(provider);
    }
}

export default ModelManager; 