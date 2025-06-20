#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提示词加载器
功能：管理和加载中文评估提示词模板
作者：AI助手
创建时间：2024年
"""

import os
import json
from typing import Dict, List, Any, Optional

class PromptLoader:
    """提示词加载器"""
    
    def __init__(self, prompts_dir: str = "data/prompts"):
        self.prompts_dir = prompts_dir
        self.prompts = {}
        
        # 确保目录存在
        os.makedirs(prompts_dir, exist_ok=True)
        
        # 加载提示词模板
        self.load_default_prompts()
        self.load_custom_prompts()
    
    def load_default_prompts(self):
        """加载默认提示词模板"""
        self.prompts = {
            "evaluation_prompt": """请对以下回答进行评估：

问题：{question}

待评估回答：{answer}

参考答案：{reference}

请从以下四个维度进行评分（0-100分）：
1. 准确性：回答内容是否正确、符合事实
2. 完整性：回答是否全面、覆盖关键要点
3. 清晰性：表达是否清楚、逻辑是否清晰
4. 总体质量：综合评价回答质量

请按以下格式输出评分：
准确性：XX分
完整性：XX分
清晰性：XX分
总体质量：XX分

评价理由：[详细说明评分理由]""",
            
            "accuracy_prompt": """请评估以下回答的准确性（0-100分）：

问题：{question}
回答：{answer}
参考答案：{reference}

评估标准：
- 90-100分：回答完全正确，无事实错误
- 70-89分：回答基本正确，有少量小错误
- 50-69分：回答部分正确，有一些错误
- 30-49分：回答有较多错误，但有部分正确内容
- 0-29分：回答错误严重或完全错误

请只返回分数（0-100的整数）""",
            
            "completeness_prompt": """请评估以下回答的完整性（0-100分）：

问题：{question}
回答：{answer}
参考答案：{reference}

评估标准：
- 90-100分：回答全面完整，覆盖所有要点
- 70-89分：回答较完整，覆盖大部分要点
- 50-69分：回答基本完整，有部分要点遗漏
- 30-49分：回答不够完整，遗漏较多要点
- 0-29分：回答很不完整，遗漏大量要点

请只返回分数（0-100的整数）""",
            
            "clarity_prompt": """请评估以下回答的清晰性（0-100分）：

问题：{question}
回答：{answer}

评估标准：
- 90-100分：表达非常清晰，逻辑性强，结构良好
- 70-89分：表达清晰，逻辑较好
- 50-69分：表达基本清晰，逻辑一般
- 30-49分：表达不够清晰，逻辑混乱
- 0-29分：表达很不清晰，难以理解

请只返回分数（0-100的整数）""",
            
            "comparison_prompt": """请比较以下两个回答的质量：

问题：{question}

回答A：{answer_a}

回答B：{answer_b}

参考答案：{reference}

请从准确性、完整性、清晰性三个维度比较，并给出总体评价。
请按以下格式回答：

准确性：A/B更好，原因...
完整性：A/B更好，原因...
清晰性：A/B更好，原因...
总体评价：A/B更好""",
            
            "improvement_prompt": """请为以下回答提出改进建议：

问题：{question}
回答：{answer}
参考答案：{reference}

请从以下方面提出具体的改进建议：
1. 内容准确性
2. 完整性
3. 表达清晰度
4. 逻辑结构

改进建议：""",
            
            "category_specific_prompts": {
                "ai": """作为AI领域专家，请评估以下回答：

问题：{question}
回答：{answer}
参考答案：{reference}

请特别关注：
- 技术概念是否准确
- 算法原理是否正确
- 应用场景是否合适
- 前沿发展是否跟上

评分（0-100）：""",
                
                "programming": """作为编程专家，请评估以下回答：

问题：{question}
回答：{answer}
参考答案：{reference}

请特别关注：
- 代码示例是否正确
- 编程概念是否准确
- 最佳实践是否遵循
- 性能考虑是否充分

评分（0-100）：""",
                
                "math": """作为数学专家，请评估以下回答：

问题：{question}
回答：{answer}
参考答案：{reference}

请特别关注：
- 数学公式是否正确
- 推导过程是否严谨
- 概念定义是否准确
- 应用是否恰当

评分（0-100）："""
            }
        }
    
    def load_custom_prompts(self):
        """加载自定义提示词"""
        prompts_file = os.path.join(self.prompts_dir, "custom_prompts.json")
        
        if os.path.exists(prompts_file):
            try:
                with open(prompts_file, 'r', encoding='utf-8') as f:
                    custom_prompts = json.load(f)
                
                # 合并自定义提示词
                self.prompts.update(custom_prompts)
                print(f"成功加载自定义提示词: {len(custom_prompts)} 个")
                
            except Exception as e:
                print(f"加载自定义提示词失败: {e}")
    
    def get_prompt(self, prompt_type: str, **kwargs) -> str:
        """获取格式化的提示词"""
        if prompt_type not in self.prompts:
            raise ValueError(f"提示词类型 {prompt_type} 不存在")
        
        template = self.prompts[prompt_type]
        
        try:
            return template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"提示词模板缺少参数: {e}")
    
    def get_category_prompt(self, category: str, **kwargs) -> str:
        """获取分类特定的提示词"""
        category_prompts = self.prompts.get("category_specific_prompts", {})
        
        if category.lower() in category_prompts:
            template = category_prompts[category.lower()]
            return template.format(**kwargs)
        else:
            # 使用通用评估提示词
            return self.get_prompt("evaluation_prompt", **kwargs)
    
    def list_available_prompts(self) -> List[str]:
        """列出可用的提示词类型"""
        prompts = list(self.prompts.keys())
        
        # 添加分类特定提示词
        if "category_specific_prompts" in self.prompts:
            category_prompts = self.prompts["category_specific_prompts"]
            for category in category_prompts:
                prompts.append(f"category_{category}")
        
        return prompts
    
    def save_custom_prompt(self, prompt_type: str, template: str) -> bool:
        """保存自定义提示词"""
        prompts_file = os.path.join(self.prompts_dir, "custom_prompts.json")
        
        # 加载现有自定义提示词
        custom_prompts = {}
        if os.path.exists(prompts_file):
            try:
                with open(prompts_file, 'r', encoding='utf-8') as f:
                    custom_prompts = json.load(f)
            except:
                pass
        
        # 添加新提示词
        custom_prompts[prompt_type] = template
        
        try:
            with open(prompts_file, 'w', encoding='utf-8') as f:
                json.dump(custom_prompts, f, ensure_ascii=False, indent=2)
            
            # 更新内存中的提示词
            self.prompts[prompt_type] = template
            print(f"成功保存自定义提示词: {prompt_type}")
            return True
            
        except Exception as e:
            print(f"保存自定义提示词失败: {e}")
            return False
    
    def create_evaluation_prompt(self, question: str, answer: str, 
                               reference: str, evaluation_type: str = "general") -> str:
        """创建评估提示词"""
        if evaluation_type == "accuracy":
            return self.get_prompt("accuracy_prompt", 
                                 question=question, answer=answer, reference=reference)
        elif evaluation_type == "completeness":
            return self.get_prompt("completeness_prompt", 
                                 question=question, answer=answer, reference=reference)
        elif evaluation_type == "clarity":
            return self.get_prompt("clarity_prompt", 
                                 question=question, answer=answer)
        else:
            return self.get_prompt("evaluation_prompt", 
                                 question=question, answer=answer, reference=reference)
    
    def create_programming_evaluation_prompt(self, question_data: dict, model_answer: str, 
                                           standard_answer: str = None, question_type: str = "standard_answer") -> str:
        """创建编程类型的评估提示词"""
        # 首先尝试查找专门的评估提示文件
        prompt_file = self._find_evaluation_prompt_file(question_data)
        print(f"🔍 查找评估提示文件: {prompt_file}")
        print(f"📁 文件存在: {os.path.exists(prompt_file) if prompt_file else False}")
        
        if prompt_file and os.path.exists(prompt_file):
            try:
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    template = f.read()
                print(f"✅ 成功读取专门的评估模板: {os.path.basename(prompt_file)}")
                
                # 动态替换模板中的占位符
                prompt = template.replace("{model_answer}", model_answer)
                
                # 如果有标准答案，尝试替换标准答案占位符
                if standard_answer and standard_answer.strip():
                    # 查找模板中的标准答案部分并替换
                    if "{standard_answer}" in prompt:
                        prompt = prompt.replace("{standard_answer}", standard_answer)
                    elif "标准答案参考实现：" in prompt and "```python" in prompt:
                        # 替换代码块中的标准答案
                        import re
                        # 找到标准答案代码块的位置
                        pattern = r'标准答案参考实现：\s*```python\s*.*?```'
                        replacement = f'标准答案参考实现：\n```python\n{standard_answer}\n```'
                        prompt = re.sub(pattern, replacement, prompt, flags=re.DOTALL)
                    elif "标准答案预期输出：" in prompt:
                        # 替换预期输出部分
                        pattern = r'标准答案预期输出：\s*.*?(?=\n\n评估要求：)'
                        replacement = f'标准答案预期输出：\n{standard_answer}'
                        prompt = re.sub(pattern, replacement, prompt, flags=re.DOTALL)
                    else:
                        # 如果没有找到特定的标准答案位置，在模型回答后添加
                        prompt = prompt.replace(
                            "模型回答：\n{model_answer}",
                            f"模型回答：\n{model_answer}\n\n参考答案：\n{standard_answer}"
                        )
                
                print(f"🎯 成功使用专门的评估模板: {os.path.basename(prompt_file)}")
                return prompt
            except Exception as e:
                print(f"❌ 读取专门评估模板失败: {e}")
                # 继续使用默认逻辑
        else:
            print(f"⚠️ 未找到专门的评估模板，使用默认生成逻辑")
        
        # 如果没有找到专门的提示文件，使用默认生成逻辑
        print(f"📝 使用默认编程评估模板生成逻辑")
        # 获取问题信息
        question_text = question_data.get('question') or question_data.get('content', '')
        question_id = question_data.get('id', '')
        actual_question_type = question_data.get('type', '')
        
        # 根据实际的问题类型和是否有标准答案来决定评估方式
        has_standard_answer = standard_answer and standard_answer.strip()
        has_sub_questions = len(question_data.get('sub_questions', [])) > 0
        
        # 创建基础评估提示
        if has_sub_questions:
            # 有子问题的情况 - 使用结构化评估
            prompt = f"""请评估以下编程回答的正确性和质量：

问题：{question_text}

模型回答：
{model_answer}
"""
            if has_standard_answer:
                prompt += f"""
参考答案：
{standard_answer}
"""
            
            prompt += f"""
评估要求：
{question_data.get('evaluation_prompt', '请评估回答的正确性、完整性和清晰度')}

子问题评估：
"""
            for sub_q in question_data.get('sub_questions', []):
                prompt += f"- {sub_q.get('description', sub_q.get('content', ''))} (权重: {sub_q['weight']*100}%)\n"
            
            prompt += """
请对每个子问题进行评估：
1. 如果子问题完成，给出1分；如果未完成，给出0分
2. 对准确性、完整性、清晰度分别评分（0-100分）
3. 判断是否完成整体需求（True/False）

请按以下JSON格式返回评估结果，所有反馈必须使用中文：
{
    "sub_question_scores": [1, 0, 1],  // 每个子问题的完成情况
    "requirement_completed": true,     // 是否完成需求
    "accuracy": 85,                    // 准确性分数
    "completeness": 90,                // 完整性分数
    "clarity": 80,                     // 清晰度分数
    "feedback": "详细的中文评估反馈，请使用中文描述回答的优缺点和改进建议"
}"""
        else:
            # 没有子问题的情况 - 使用通用编程评估
            prompt = f"""请评估以下编程回答的质量：

问题：{question_text}

模型回答：
{model_answer}
"""
            if has_standard_answer:
                prompt += f"""
参考答案：
{standard_answer}

请对比模型回答与参考答案，评估回答的质量。
"""
            
            prompt += f"""
评估维度：
1. 准确性：回答是否正确解决了问题，逻辑是否正确
2. 完整性：是否包含了题目要求的所有内容
3. 清晰度：表达是否清楚，代码结构是否清晰（如适用）

请按以下JSON格式返回评估结果，所有反馈必须使用中文：
{{
    "requirement_completed": true,     // 是否完成需求（由评估模型判断）
    "accuracy": 85,                    // 准确性分数
    "completeness": 90,                // 完整性分数
    "clarity": 80,                     // 清晰度分数
    "feedback": "详细的中文评估反馈，请使用中文描述回答的优缺点和改进建议"
}}"""
        
        return prompt
    
    def _find_evaluation_prompt_file(self, question_data: dict) -> str:
        """根据问题数据查找对应的评估提示文件"""
        # 确定数据集类型
        dataset_type = self._determine_dataset_type(question_data)
        
        # 构建映射文件路径
        mapping_file = os.path.join("data/evaluation_prompts", dataset_type, "prompt_mapping.json")
        
        if not os.path.exists(mapping_file):
            # 如果没有映射文件，尝试使用传统的命名方式
            print(f"⚠️ 映射文件不存在: {mapping_file}")
            return os.path.join("data/evaluation_prompts", dataset_type, f"question_{question_data['id']}_evaluation.txt")
        
        try:
            with open(mapping_file, 'r', encoding='utf-8') as f:
                mapping_config = json.load(f)
            
            # 根据问题ID查找
            question_id = question_data.get('id')
            for mapping in mapping_config.get('question_mappings', []):
                if mapping.get('question_id') == question_id:
                    prompt_file = mapping.get('prompt_file')
                    return os.path.join("data/evaluation_prompts", dataset_type, prompt_file)
            
            # 如果没有找到精确匹配，尝试关键词匹配
            question_text = (question_data.get('question') or question_data.get('content', '')).lower()
            for mapping in mapping_config.get('question_mappings', []):
                keywords = mapping.get('question_keywords', [])
                if any(keyword.lower() in question_text for keyword in keywords):
                    prompt_file = mapping.get('prompt_file')
                    return os.path.join("data/evaluation_prompts", dataset_type, prompt_file)
            
        except Exception as e:
            print(f"读取评估提示映射文件失败: {e}")
        
        # 如果都没找到，返回默认路径
        print(f"⚠️ 未找到匹配的提示文件，使用默认路径")
        return os.path.join("data/evaluation_prompts", dataset_type, f"question_{question_data['id']}_evaluation.txt")
    
    def _determine_dataset_type(self, question_data: dict) -> str:
        """根据问题数据确定数据集类型"""
        question_type = question_data.get('type', '')
        category = question_data.get('category', '').lower()
        
        # 检查是否来自混合数据集
        if hasattr(self, '_current_dataset_file'):
            print(f"🔍 当前数据集文件: '{self._current_dataset_file}'")
            if 'mixed' in self._current_dataset_file.lower():
                print(f"✅ 识别为混合数据集: programming_mixed")
                return 'programming_mixed'
            else:
                print(f"❌ 未识别为混合数据集，文件名不包含'mixed'")
        else:
            print(f"⚠️ _current_dataset_file 未设置")
        
        if question_type == 'no_standard_answer' and category == '编程':
            return 'programming_no_standard'
        elif question_type == 'standard_answer' and category == '编程':
            return 'programming_standard'
        else:
            return 'general'
    
    def create_comparison_prompt(self, question: str, answer_a: str, 
                               answer_b: str, reference: str) -> str:
        """创建比较提示词"""
        return self.get_prompt("comparison_prompt",
                             question=question, answer_a=answer_a, 
                             answer_b=answer_b, reference=reference)
    
    def create_improvement_prompt(self, question: str, answer: str, reference: str) -> str:
        """创建改进建议提示词"""
        return self.get_prompt("improvement_prompt",
                             question=question, answer=answer, reference=reference)
    
    def get_prompt_template(self, prompt_type: str) -> str:
        """获取提示词模板（未格式化）"""
        return self.prompts.get(prompt_type, "")
    
    def create_model_prompt_with_answer_format(self, question_data: dict) -> str:
        """为待评估模型创建包含答案格式要求的提示"""
        question_text = question_data.get('question') or question_data.get('content', '')
        question_id = question_data.get('id')
        question_type = question_data.get('type', 'standard_answer')
        
        # 基础提示
        prompt = f"""请回答以下问题：

{question_text}

重要说明：
1. 请直接给出最终答案，不要包含思考过程或解释
2. 如果是编程题，请直接给出可执行的代码
3. 如果题目要求特定输出格式，请严格按照要求输出
4. 不要添加额外的说明文字

请将你的答案放在以下标签中：
<answer>
[在这里写你的答案]
</answer>"""
        
        # 根据问题ID添加特定的格式要求
        if question_id == "1":
            prompt += """

特别注意：
- 对于任务1，请输出完整的单词列表
- 对于任务2，请输出完整的网址列表  
- 对于任务3，请输出threat的出现次数和位置列表
- 确保输出结果可以直接用于比较"""
            
        elif question_id == "3":
            prompt += """

特别注意：
- 请实现一个名为quicksort的函数
- 函数应该接受一个列表参数并返回排序后的列表
- 确保代码可以直接运行"""
            
        elif question_id == "5":
            prompt += """

特别注意：
- 函数名必须为 calculate_vacation_dates
- 参数必须为 year 和 total_vacation_days
- 返回格式必须为 ['YYYY-MM-DD', ...] 的日期列表
- 确保测试用例 year=2023, total_vacation_days=10 的输出正确，把测试用例的结果输出在回答中"""
        
        return prompt 