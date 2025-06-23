#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文本分析器模块
负责文本质量分析和相似度计算
"""

import re
from typing import Dict, List, Set


class TextAnalyzer:
    """文本分析器"""
    
    def __init__(self):
        # 常见停用词
        self.stop_words = {'的', '是', '和', '与', '或', '但是', '因为', '所以', '在', '了', '有', '这', '那'}
    
    def calculate_keyword_match(self, text1: str, text2: str) -> float:
        """计算关键词匹配度"""
        keywords1 = self._extract_keywords(text1.lower())
        keywords2 = self._extract_keywords(text2.lower())
        
        if not keywords2:
            return 0.0
        
        intersection = keywords1.intersection(keywords2)
        return len(intersection) / len(keywords2) * 100
    
    def calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """计算语义相似度（简化版）"""
        if not text1 or not text2:
            return 0.0
        
        # 计算最长公共子序列
        lcs = self._lcs_length(text1, text2)
        max_len = max(len(text1), len(text2))
        
        return (lcs / max_len) * 100 if max_len > 0 else 0.0
    
    def evaluate_structure(self, text: str) -> float:
        """评估文本结构"""
        score = 0.0
        
        # 检查是否有段落结构
        paragraphs = text.split('\n\n')
        if len(paragraphs) > 1:
            score += 20
        
        # 检查是否有列表或编号
        if re.search(r'[1-9]\.|[1-9]、|[•\-\*]', text):
            score += 20
        
        # 检查是否有标题或小标题
        if re.search(r'[#\*]{1,3}|【.*?】', text):
            score += 15
        
        # 检查句子长度分布
        sentences = re.split(r'[。！？]', text)
        if sentences:
            avg_length = sum(len(s) for s in sentences) / len(sentences)
            if 10 <= avg_length <= 50:  # 合适的句子长度
                score += 15
        
        return min(70.0, score)
    
    def evaluate_coherence(self, text: str) -> float:
        """评估逻辑连贯性"""
        score = 30.0  # 基础分
        
        # 检查连接词使用
        connectors = ['因此', '所以', '但是', '然而', '另外', '同时', '首先', '其次', '最后', '总之']
        connector_count = sum(1 for conn in connectors if conn in text)
        score += min(20, connector_count * 4)
        
        # 检查是否有重复内容
        sentences = re.split(r'[。！？]', text)
        unique_sentences = set(sentences)
        if len(unique_sentences) == len(sentences):
            score += 10
        
        return min(70.0, score)
    
    def evaluate_professionalism(self, text: str) -> float:
        """评估专业度"""
        score = 40.0  # 基础分
        
        # 检查专业词汇使用
        professional_indicators = [
            len(re.findall(r'[A-Z]{2,}', text)),  # 缩写词
            len(re.findall(r'\d+%', text)),  # 百分比
            len(re.findall(r'\d+\.\d+', text)),  # 小数
        ]
        
        score += min(30, sum(professional_indicators) * 3)
        
        return min(70.0, score)
    
    def calculate_coverage(self, model_answer: str, reference: str) -> float:
        """计算内容覆盖度"""
        if not reference:
            return 1.0
        
        # 将参考答案分解为要点
        reference_points = self._extract_key_points(reference)
        covered_points = 0
        
        for point in reference_points:
            if any(keyword in model_answer for keyword in point.split()[:3]):
                covered_points += 1
        
        return covered_points / len(reference_points) if reference_points else 1.0
    
    def evaluate_domain_specific(self, answer: str, question: Dict) -> float:
        """评估领域特定内容"""
        category = question.get('category', '').lower()
        score = 50.0  # 基础分
        
        # 根据问题类别评估
        if 'ai' in category or 'machine learning' in category:
            ai_keywords = ['算法', '模型', '训练', '学习', '神经网络', '深度学习', 'AI', 'ML']
            keyword_count = sum(1 for keyword in ai_keywords if keyword in answer)
            score += min(30, keyword_count * 5)
        
        elif 'programming' in category or '编程' in category:
            prog_keywords = ['代码', '函数', '变量', '循环', '条件', '类', '对象', '方法']
            keyword_count = sum(1 for keyword in prog_keywords if keyword in answer)
            score += min(30, keyword_count * 4)
        
        return min(100.0, score)
    
    def _extract_keywords(self, text: str) -> Set[str]:
        """提取关键词"""
        # 移除标点符号，分词
        text = re.sub(r'[^\w\s]', ' ', text)
        words = text.split()
        # 过滤短词和停用词
        keywords = [w for w in words if len(w) > 2 and w not in self.stop_words]
        return set(keywords)
    
    def _lcs_length(self, s1: str, s2: str) -> int:
        """计算最长公共子序列长度"""
        m, n = len(s1), len(s2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if s1[i-1] == s2[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])
        
        return dp[m][n]
    
    def _extract_key_points(self, text: str) -> List[str]:
        """提取关键要点"""
        # 按句号分割，过滤短句
        sentences = [s.strip() for s in text.split('。') if len(s.strip()) > 10]
        return sentences[:5]  # 最多返回5个要点 