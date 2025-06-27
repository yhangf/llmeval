/**
 * 数据管理模块
 * 负责问题集、答案集和模型评估历史的管理
 */
class DataManager {
    constructor(apiManager, uiComponents, notificationManager) {
        this.apiManager = apiManager;
        this.uiComponents = uiComponents;
        this.notificationManager = notificationManager;
        this.questions = [];
        this.answers = [];
        this.modelEvaluations = [];
    }

    /**
     * 加载问题集
     */
    async loadQuestions() {
        try {
            const data = await this.apiManager.getQuestions();
            
            if (data.success) {
                this.questions = data.data;
                this.uiComponents.updateQuestionSets(data.data);
                this.updateQuestionSetsDropdown(data.data);
                
                // 如果有问题集，默认选择第一个并显示预览
                if (data.data.length > 0) {
                    this.updateQuestionPreview(data.data[0].preview);
                }
                
                return data.data;
            } else {
                throw new Error(data.message || '获取问题集失败');
            }
        } catch (error) {
            console.error('加载问题集失败:', error);
            this.notificationManager.error('加载问题集失败');
            throw error;
        }
    }

    /**
     * 加载答案集
     */
    async loadAnswers() {
        try {
            const data = await this.apiManager.getAnswers();
            
            if (data.success) {
                this.answers = data.data;
                this.uiComponents.updateAnswerSets(data.data);
                return data.data;
            } else {
                throw new Error(data.message || '获取答案集失败');
            }
        } catch (error) {
            console.error('加载答案集失败:', error);
            this.notificationManager.error('加载答案集失败');
            throw error;
        }
    }

    /**
     * 加载模型评估历史
     */
    async loadModelEvaluations() {
        try {
            const data = await this.apiManager.getModelEvaluations();
            
            if (data.success) {
                this.modelEvaluations = data.data;
                this.uiComponents.updateModelEvaluations(data.data);
                return data.data;
            } else {
                throw new Error(data.message || '获取模型评估历史失败');
            }
        } catch (error) {
            console.error('加载模型评估历史失败:', error);
            this.notificationManager.error('加载模型评估历史失败');
            throw error;
        }
    }

    /**
     * 获取问题集列表
     */
    getQuestions() {
        return this.questions;
    }

    /**
     * 获取答案集列表
     */
    getAnswers() {
        return this.answers;
    }

    /**
     * 获取模型评估历史
     */
    getModelEvaluations() {
        return this.modelEvaluations;
    }

    /**
     * 根据文件名获取问题集
     */
    getQuestionByFilename(filename) {
        return this.questions.find(q => q.filename === filename);
    }

    /**
     * 根据文件名获取答案集
     */
    getAnswerByFilename(filename) {
        return this.answers.find(a => a.filename === filename);
    }

    /**
     * 更新问题集下拉框
     */
    updateQuestionSetsDropdown(questionSets) {
        const questionSelect = document.getElementById('questionSet');
        if (!questionSelect) {
            console.warn('问题集下拉框元素未找到');
            return;
        }
        
        // 更新下拉框
        questionSelect.innerHTML = '';
        questionSets.forEach(set => {
            const option = document.createElement('option');
            option.value = set.filename;
            option.textContent = `${set.name || set.filename} (${set.count}题) - ${set.type || '通用'}`;
            questionSelect.appendChild(option);
        });
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
            if (this.questions) {
                const questionSet = this.questions.find(set => set.filename === filename);
                if (questionSet) {
                    this.updateQuestionPreview(questionSet.preview);
                    return;
                }
            }
            
            // 如果没有缓存，重新请求数据
            const data = await this.apiManager.getQuestions();
            
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
        if (!container) {
            console.warn('问题预览容器未找到');
            return;
        }
        
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
}

export default DataManager; 