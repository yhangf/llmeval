/**
 * 数据管理模块
 * 负责问题集和答案集的加载和管理
 */
class DataManager {
    constructor(apiManager, uiComponents, notificationManager) {
        this.apiManager = apiManager;
        this.uiComponents = uiComponents;
        this.notificationManager = notificationManager;
        this.questionSets = [];
        this.answerSets = [];
    }

    /**
     * 加载问题集
     */
    async loadQuestions() {
        try {
            const data = await this.apiManager.getQuestions();
            
            if (data.success) {
                this.questionSets = data.data;
                this.updateQuestionSetsDisplay(data.data);
                
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
     * 更新问题集显示
     */
    updateQuestionSetsDisplay(questionSets) {
        const questionSelect = document.getElementById('questionSet');
        const container = document.getElementById('questionSetsContainer');
        
        if (!questionSelect || !container) {
            console.warn('问题集相关元素未找到');
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

    /**
     * 获取问题集列表
     */
    getQuestionSets() {
        return this.questionSets;
    }

    /**
     * 根据文件名获取问题集
     */
    getQuestionSetByFilename(filename) {
        return this.questionSets.find(set => set.filename === filename);
    }
}

export default DataManager; 