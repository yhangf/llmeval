/**
 * 工具提示管理器
 * 负责管理评分规则相关的气泡提示
 */
class TooltipManager {
    constructor() {
        this.tooltips = new Map();
        this.initializeTooltips();
    }

    /**
     * 初始化所有工具提示内容
     */
    initializeTooltips() {
        // 评分相关的提示
        this.tooltips.set('总分', {
            hasStandard: '根据子问题权重加权平均计算：<br>总分 = Σ(子问题分数 × 权重)',
            noStandard: '由三个维度平均计算：<br>总分 = (准确性 + 完整性 + 清晰度) ÷ 3',
            notCompleted: '如果未完成需求，直接为 0 分'
        });

        this.tooltips.set('准确性', {
            description: '代码逻辑是否正确，能否正确实现所需功能'
        });

        this.tooltips.set('完整性', {
            description: '是否包含了题目要求的所有功能'
        });

        this.tooltips.set('清晰度', {
            description: '代码结构是否清晰，命名是否规范'
        });

        this.tooltips.set('子问题分数', {
            description: '每个子问题的单独评分，会根据权重影响最终总分'
        });

        this.tooltips.set('需求完成情况', {
            description: '判断是否完成了题目的基本要求，未完成则总分为0'
        });

        this.tooltips.set('权重', {
            description: '该子问题在总分中所占的比重，所有权重之和为1.0'
        });

        this.tooltips.set('评估模型', {
            description: '用于评估答案质量的大语言模型'
        });

        this.tooltips.set('标准答案', {
            description: '题目的参考答案，用于对比评估'
        });
    }

    /**
     * 创建带工具提示的文本元素
     * @param {string} text - 要显示的文本
     * @param {string} tooltipKey - 工具提示的键名
     * @param {Object} context - 上下文信息（如是否有标准答案等）
     * @param {string} position - 气泡位置（default, right, left）
     * @returns {string} HTML字符串
     */
    createTooltipElement(text, tooltipKey, context = {}, position = 'default') {
        const tooltip = this.tooltips.get(tooltipKey);
        if (!tooltip) {
            return text; // 如果没有找到对应的提示，直接返回原文本
        }

        let tooltipContent = '';
        
        // 根据上下文选择合适的提示内容
        if (tooltipKey === '总分') {
            if (context.requirementCompleted === false) {
                tooltipContent = tooltip.notCompleted;
            } else if (context.hasStandardAnswer) {
                tooltipContent = tooltip.hasStandard;
            } else {
                tooltipContent = tooltip.noStandard;
            }
        } else if (tooltip.description) {
            tooltipContent = tooltip.description;
        } else {
            tooltipContent = tooltip.hasStandard || tooltip.description || '暂无说明';
        }

        const positionClass = position !== 'default' ? `tooltip-${position}` : '';
        
        return `<span class="tooltip-term ${positionClass}">${text}<div class="tooltip-bubble">${tooltipContent}</div></span>`;
    }

    /**
     * 为指定元素添加工具提示
     * @param {string} selector - CSS选择器
     * @param {string} tooltipKey - 工具提示的键名
     * @param {Object} context - 上下文信息
     */
    addTooltipToElement(selector, tooltipKey, context = {}) {
        const elements = document.querySelectorAll(selector);
        elements.forEach(element => {
            const originalText = element.textContent;
            element.innerHTML = this.createTooltipElement(originalText, tooltipKey, context);
        });
    }

    /**
     * 批量添加工具提示到表格标题
     * @param {string} tableSelector - 表格选择器
     * @param {Object} columnMappings - 列标题到工具提示键的映射
     * @param {Object} context - 全局上下文
     */
    addTooltipsToTable(tableSelector, columnMappings, context = {}) {
        const table = document.querySelector(tableSelector);
        if (!table) return;

        const headers = table.querySelectorAll('thead th');
        headers.forEach(header => {
            const headerText = header.textContent.trim();
            if (columnMappings[headerText]) {
                header.innerHTML = this.createTooltipElement(
                    headerText, 
                    columnMappings[headerText], 
                    context
                );
            }
        });
    }

    /**
     * 为评估结果表格添加工具提示
     * @param {Object} context - 评估上下文信息
     */
    setupEvaluationTableTooltips(context = {}) {
        // 表格列标题映射
        const columnMappings = {
            '准确性': '准确性',
            '完整性': '完整性', 
            '清晰度': '清晰度',
            '总分': '总分'
        };

        // 为主要的评估结果表格添加工具提示
        this.addTooltipsToTable('.table', columnMappings, context);
        
        // 为模态框中的表格也添加工具提示
        this.addTooltipsToTable('.custom-modal .table', columnMappings, context);
    }

    /**
     * 为任务详情中的特定文本添加工具提示
     * @param {Object} taskData - 任务数据
     */
    setupTaskDetailTooltips(taskData = {}) {
        // 检查是否有标准答案
        const hasStandardAnswer = taskData.answer_file && taskData.answer_file !== 'N/A';
        
        const context = {
            hasStandardAnswer: hasStandardAnswer,
            requirementCompleted: null // 这个需要根据具体结果动态设置
        };

        // 设置表格工具提示
        this.setupEvaluationTableTooltips(context);

        // 为其他关键词添加工具提示
        setTimeout(() => {
            // 评估模型相关
            const evaluatorElements = document.querySelectorAll('.badge:contains("评估模型")');
            evaluatorElements.forEach(el => {
                if (el.textContent.includes('评估模型') || el.textContent.includes('程序评估')) {
                    el.innerHTML = this.createTooltipElement(
                        el.textContent, 
                        '评估模型', 
                        context, 
                        'right'
                    );
                }
            });

            // 标准答案相关
            this.addTooltipToElement('[title*="标准答案"]', '标准答案', context);
        }, 100);
    }

    /**
     * 智能检测并添加工具提示
     * @param {string} containerSelector - 容器选择器
     * @param {Object} context - 上下文信息
     */
    autoDetectAndAddTooltips(containerSelector = 'body', context = {}) {
        const container = document.querySelector(containerSelector);
        if (!container) return;

        // 查找所有可能需要工具提示的文本
        const textNodes = this.getTextNodes(container);
        
        textNodes.forEach(node => {
            const text = node.textContent.trim();
            
            // 检查是否匹配任何工具提示关键词
            for (const [key] of this.tooltips) {
                if (text.includes(key)) {
                    const parent = node.parentElement;
                    if (parent && !parent.classList.contains('tooltip-term')) {
                        parent.innerHTML = parent.innerHTML.replace(
                            text,
                            this.createTooltipElement(text, key, context)
                        );
                    }
                    break;
                }
            }
        });
    }

    /**
     * 获取元素中的所有文本节点
     * @param {Element} element - 要搜索的元素
     * @returns {Array} 文本节点数组
     */
    getTextNodes(element) {
        const textNodes = [];
        const walker = document.createTreeWalker(
            element,
            NodeFilter.SHOW_TEXT,
            {
                acceptNode: function(node) {
                    // 跳过已经有工具提示的节点
                    if (node.parentElement.classList.contains('tooltip-term')) {
                        return NodeFilter.FILTER_REJECT;
                    }
                    // 跳过空文本节点
                    if (node.textContent.trim() === '') {
                        return NodeFilter.FILTER_REJECT;
                    }
                    return NodeFilter.FILTER_ACCEPT;
                }
            }
        );

        let node;
        while (node = walker.nextNode()) {
            textNodes.push(node);
        }
        
        return textNodes;
    }

    /**
     * 清除所有工具提示
     * @param {string} containerSelector - 容器选择器
     */
    clearTooltips(containerSelector = 'body') {
        const container = document.querySelector(containerSelector);
        if (!container) return;

        const tooltipElements = container.querySelectorAll('.tooltip-term');
        tooltipElements.forEach(element => {
            element.replaceWith(document.createTextNode(element.textContent));
        });
    }

    /**
     * 动态更新工具提示内容
     * @param {string} key - 工具提示键名
     * @param {Object} newContent - 新的内容对象
     */
    updateTooltip(key, newContent) {
        this.tooltips.set(key, { ...this.tooltips.get(key), ...newContent });
    }
}

export default TooltipManager; 