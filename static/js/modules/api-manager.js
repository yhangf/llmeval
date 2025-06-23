/**
 * API管理模块
 * 负责所有与后端API的通信
 */
class ApiManager {
    constructor() {
        this.baseUrl = '';
    }

    /**
     * 通用API请求方法
     */
    async request(url, options = {}) {
        try {
            const response = await fetch(this.baseUrl + url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            const data = await response.json();
            
            if (!response.ok) {
                const errorMessage = data.detail || data.message || `HTTP ${response.status}`;
                console.error(`API错误详情 [${url}]:`, data);
                throw new Error(errorMessage);
            }
            
            return data;
        } catch (error) {
            console.error(`API请求失败 [${url}]:`, error);
            throw error;
        }
    }

    /**
     * 获取模型列表
     */
    async getModels() {
        return this.request('/api/models');
    }

    /**
     * 添加模型
     */
    async addModel(config) {
        return this.request('/api/models', {
            method: 'POST',
            body: JSON.stringify(config)
        });
    }

    /**
     * 删除模型
     */
    async deleteModel(modelName) {
        return this.request(`/api/models/${encodeURIComponent(modelName)}`, {
            method: 'DELETE'
        });
    }

    /**
     * 获取问题集列表
     */
    async getQuestions() {
        return this.request('/api/questions');
    }

    /**
     * 获取答案集列表
     */
    async getAnswers() {
        return this.request('/api/answers');
    }

    /**
     * 获取任务列表
     */
    async getTasks() {
        return this.request('/api/tasks');
    }

    /**
     * 创建评估任务
     */
    async createTask(config) {
        return this.request('/api/tasks', {
            method: 'POST',
            body: JSON.stringify(config)
        });
    }

    /**
     * 获取任务详情
     */
    async getTask(taskId) {
        return this.request(`/api/tasks/${taskId}`);
    }

    /**
     * 删除任务
     */
    async deleteTask(taskId) {
        return this.request(`/api/tasks/${taskId}`, {
            method: 'DELETE'
        });
    }
}

export default ApiManager; 