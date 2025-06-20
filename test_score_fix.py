#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试分数计算修复
"""

from core.evaluation.score_calculator import ScoreCalculator
import json

# 加载问题数据
with open('data/questions/programming_questions_mixed.json', 'r', encoding='utf-8') as f:
    questions = json.load(f)

calculator = ScoreCalculator()

# 测试问题1的情况（有标准答案，但没有sub_question_scores）
question1 = questions[0]  # 问题1
eval_result1 = {
    'requirement_completed': True,
    'accuracy': 85,
    'completeness': 90,
    'clarity': 80,
    'sub_question_scores': []  # 空数组
}

print('=== 问题1测试 ===')
score1 = calculator.calculate_programming_score(question1, eval_result1)
print(f'问题1最终分数: {score1}')
print()

# 测试问题5的情况（有标准答案，有sub_question_scores，但requirement_completed=False）
question5 = questions[4]  # 问题5
eval_result5 = {
    'requirement_completed': False,
    'accuracy': 75,
    'completeness': 75,
    'clarity': 75,
    'sub_question_scores': [100, 100, 50, 100]
}

print('=== 问题5测试 ===')
score5 = calculator.calculate_programming_score(question5, eval_result5)
print(f'问题5最终分数: {score5}')
print()

# 测试问题2的情况（无标准答案，requirement_completed=True）
question2 = questions[1]  # 问题2
eval_result2 = {
    'requirement_completed': True,
    'accuracy': 95,
    'completeness': 90,
    'clarity': 85,
    'sub_question_scores': []
}

print('=== 问题2测试 ===')
score2 = calculator.calculate_programming_score(question2, eval_result2)
print(f'问题2最终分数: {score2}')
print()

# 测试问题4的情况（无标准答案，requirement_completed=True）
question4 = questions[3]  # 问题4
eval_result4 = {
    'requirement_completed': True,
    'accuracy': 85,
    'completeness': 90,
    'clarity': 80,
    'sub_question_scores': []
}

print('=== 问题4测试 ===')
score4 = calculator.calculate_programming_score(question4, eval_result4)
print(f'问题4最终分数: {score4}') 