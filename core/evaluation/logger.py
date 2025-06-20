#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
评估日志器模块
负责记录评估过程中的所有模型交互和结果
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path


class EvaluationLogger:
    """评估日志器"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.current_log_file = None
        self.current_json_file = None
        self.logger = None
        self.session_id = None
        self.session_data = {}  # 存储会话的结构化数据
        
    def start_evaluation_session(self, target_model: str, evaluator_model: str, 
                                dataset_name: str = "unknown") -> str:
        """开始新的评估会话，创建专门的日志文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_id = f"{timestamp}_{target_model}_{dataset_name}"
        
        # 创建日志文件名
        log_filename = f"evaluation_{self.session_id}.log"
        json_filename = f"evaluation_{self.session_id}.json"
        self.current_log_file = self.log_dir / log_filename
        self.current_json_file = self.log_dir / json_filename
        
        # 初始化会话数据
        self.session_data = {
            "session_info": {
                "session_id": self.session_id,
                "start_time": datetime.now().isoformat(),
                "target_model": target_model,
                "evaluator_model": evaluator_model,
                "dataset": dataset_name,
                "log_file": str(self.current_log_file),
                "json_file": str(self.current_json_file)
            },
            "questions_and_answers": [],
            "evaluations": [],
            "session_summary": {}
        }
        
        # 配置日志器
        self.logger = logging.getLogger(f"evaluation_{self.session_id}")
        self.logger.setLevel(logging.INFO)
        
        # 清除之前的处理器
        self.logger.handlers.clear()
        
        # 文件处理器
        file_handler = logging.FileHandler(self.current_log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        
        # 格式化器
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # 记录会话开始
        self.log_session_start(target_model, evaluator_model, dataset_name)
        
        return str(self.current_log_file)
    
    def log_session_start(self, target_model: str, evaluator_model: str, dataset_name: str):
        """记录评估会话开始信息"""
        session_info = {
            "session_id": self.session_id,
            "start_time": datetime.now().isoformat(),
            "target_model": target_model,
            "evaluator_model": evaluator_model,
            "dataset": dataset_name,
            "log_file": str(self.current_log_file)
        }
        
        self.logger.info("=" * 80)
        self.logger.info("🚀 评估会话开始")
        self.logger.info("=" * 80)
        self.logger.info(f"会话ID: {self.session_id}")
        self.logger.info(f"待评估模型: {target_model}")
        self.logger.info(f"评估模型: {evaluator_model}")
        self.logger.info(f"数据集: {dataset_name}")
        self.logger.info(f"日志文件: {self.current_log_file}")
        self.logger.info(f"JSON数据文件: {self.current_json_file}")
        self.logger.info("-" * 80)
    
    def log_question_start(self, question_id: Any, question_content: str, full_question_data: Dict[str, Any] = None):
        """记录问题开始处理"""
        self.logger.info(f"\n📝 开始处理问题 {question_id}")
        self.logger.info(f"问题内容: {question_content[:200]}{'...' if len(question_content) > 200 else ''}")
        
        # 保存完整问题数据到JSON结构
        question_entry = {
            "question_id": question_id,
            "timestamp": datetime.now().isoformat(),
            "question_content": question_content,
            "full_question_data": full_question_data or {},
            "model_interactions": [],
            "evaluation_result": {}
        }
        
        self.session_data["questions_and_answers"].append(question_entry)
    
    def log_model_request(self, model_name: str, prompt: str, config: Dict[str, Any] = None):
        """记录模型请求"""
        self.logger.info(f"🤖 向模型 {model_name} 发送请求")
        self.logger.info(f"提示词长度: {len(prompt)} 字符")
        if config:
            self.logger.info(f"配置参数: {json.dumps(config, ensure_ascii=False)}")
        
        # 记录完整提示词到详细日志
        self.logger.debug(f"完整提示词:\n{prompt}")
        
        # 保存到JSON结构
        if self.session_data["questions_and_answers"]:
            current_question = self.session_data["questions_and_answers"][-1]
            request_data = {
                "type": "request",
                "model_name": model_name,
                "timestamp": datetime.now().isoformat(),
                "prompt": prompt,
                "config": config or {},
                "prompt_length": len(prompt)
            }
            current_question["model_interactions"].append(request_data)
    
    def log_model_response(self, model_name: str, response: Dict[str, Any], 
                          response_type: str = "generation"):
        """记录模型回答"""
        content = response.get('content', '')
        tokens_used = response.get('tokens_used', 0)
        error = response.get('error')
        
        if error:
            self.logger.warning(f"❌ 模型 {model_name} 响应错误: {error}")
        else:
            self.logger.info(f"✅ 模型 {model_name} 响应成功")
            self.logger.info(f"回答长度: {len(content)} 字符")
            self.logger.info(f"使用Token: {tokens_used}")
        
        # 记录完整回答
        self.logger.info(f"--- {response_type.upper()} 开始 ---")
        self.logger.info(content)
        self.logger.info(f"--- {response_type.upper()} 结束 ---")
        
        if error:
            self.logger.info(f"错误详情: {error}")
        
        # 保存到JSON结构
        if self.session_data["questions_and_answers"]:
            current_question = self.session_data["questions_and_answers"][-1]
            response_data = {
                "type": "response",
                "model_name": model_name,
                "timestamp": datetime.now().isoformat(),
                "response_type": response_type,
                "content": content,
                "tokens_used": tokens_used,
                "content_length": len(content),
                "error": error,
                "full_response": response
            }
            current_question["model_interactions"].append(response_data)
    
    def log_evaluation_result(self, question_id: Any, evaluation: Dict[str, Any]):
        """记录评估结果"""
        scores = evaluation.get('scores', {})
        feedback = evaluation.get('feedback', '')
        requirement_completed = evaluation.get('requirement_completed')
        evaluation_type = evaluation.get('details', {}).get('evaluation_type', 'unknown')
        
        self.logger.info(f"📊 问题 {question_id} 评估完成 (类型: {evaluation_type})")
        self.logger.info(f"分数: 准确性={scores.get('accuracy', 0):.1f}, "
                        f"完整性={scores.get('completeness', 0):.1f}, "
                        f"清晰度={scores.get('clarity', 0):.1f}, "
                        f"总分={scores.get('overall', 0):.1f}")
        
        if requirement_completed is not None:
            self.logger.info(f"需求完成: {'✓ 已完成' if requirement_completed else '✗ 未完成'}")
        
        if feedback:
            self.logger.info(f"评估反馈: {feedback}")
        
        # 记录子问题分数
        sub_scores = evaluation.get('sub_question_scores', [])
        if sub_scores:
            self.logger.info(f"子问题分数: {sub_scores}")
        
        # 保存到JSON结构
        if self.session_data["questions_and_answers"]:
            current_question = self.session_data["questions_and_answers"][-1]
            evaluation_data = {
                "question_id": question_id,
                "timestamp": datetime.now().isoformat(),
                "evaluation_type": evaluation_type,
                "scores": scores,
                "feedback": feedback,
                "requirement_completed": requirement_completed,
                "sub_question_scores": sub_scores,
                "full_evaluation": evaluation
            }
            current_question["evaluation_result"] = evaluation_data
    
    def log_progress(self, current: int, total: int, stage: str = ""):
        """记录进度"""
        percentage = (current / total * 100) if total > 0 else 0
        
        # 根据阶段显示不同的emoji和描述
        stage_emoji = {
            "生成回答": "🤖",
            "评估回答": "📊", 
            "完成": "✅"
        }.get(stage, "⏳")
        
        # 显示更详细的进度信息
        if stage == "生成回答":
            self.logger.info(f"⏳ 问题 {current}/{total} - {stage_emoji} 生成回答中...")
            self.logger.info(f"   📝 正在请求待评估模型生成回答")
        elif stage == "评估回答":
            self.logger.info(f"⏳ 问题 {current}/{total} - {stage_emoji} 评估回答中...")
            self.logger.info(f"   🔍 正在使用评估模型分析回答质量")
        else:
            stage_info = f" {stage_emoji} {stage}" if stage else ""
            self.logger.info(f"⏳ 进度: {current}/{total} ({percentage:.1f}%){stage_info}")
        
        # 显示剩余问题数
        remaining = total - current
        if remaining > 0 and stage:
            self.logger.info(f"   📊 剩余问题: {remaining} 个")
    
    def log_session_summary(self, summary: Dict[str, Any]):
        """记录会话总结"""
        self.logger.info("\n" + "=" * 80)
        self.logger.info("📈 评估会话总结")
        self.logger.info("=" * 80)
        
        # 基本统计
        self.logger.info(f"总问题数: {summary.get('total_questions', 0)}")
        self.logger.info(f"总Token使用: {summary.get('total_tokens', 0)}")
        self.logger.info(f"估算成本: ${summary.get('total_cost', 0):.4f}")
        
        # 分数统计
        score_stats = summary.get('score_statistics', {})
        for metric, stats in score_stats.items():
            if stats:
                self.logger.info(f"{metric}分数 - 平均: {stats.get('mean', 0):.1f}, "
                               f"中位数: {stats.get('median', 0):.1f}, "
                               f"最高: {stats.get('max', 0):.1f}, "
                               f"最低: {stats.get('min', 0):.1f}")
        
        # 保存总结到JSON结构
        self.session_data["session_summary"] = {
            **summary,
            "end_time": datetime.now().isoformat()
        }
    
    def log_session_end(self):
        """记录评估会话结束"""
        end_time = datetime.now().isoformat()
        self.logger.info(f"\n🏁 评估会话结束: {end_time}")
        self.logger.info("=" * 80)
        
        # 保存JSON数据文件
        self._save_json_data()
        
        # 关闭日志处理器
        for handler in self.logger.handlers[:]:
            handler.close()
            self.logger.removeHandler(handler)
    
    def _save_json_data(self):
        """保存简化的JSON格式数据，只保留用户输入和模型输出"""
        if self.current_json_file and self.session_data:
            try:
                # 创建简化的数据结构
                simplified_data = {
                    "session_info": {
                        "session_id": self.session_data["session_info"]["session_id"],
                        "target_model": self.session_data["session_info"]["target_model"],
                        "dataset": self.session_data["session_info"]["dataset"],
                        "start_time": self.session_data["session_info"]["start_time"]
                    },
                    "conversations": []
                }
                
                # 处理每个问题的对话
                for question_data in self.session_data["questions_and_answers"]:
                    conversation = []
                    
                    # 添加用户输入（问题）
                    user_message = {
                        "role": "user",
                        "content": question_data["question_content"]
                    }
                    conversation.append(user_message)
                    
                    # 查找模型的生成回答（不是评估回答）
                    for interaction in question_data["model_interactions"]:
                        if (interaction["type"] == "response" and 
                            interaction.get("response_type") in ["generation", "待评估模型回答"] and
                            not interaction.get("error")):
                            
                            assistant_message = {
                                "role": "assistant", 
                                "content": interaction["content"]
                            }
                            conversation.append(assistant_message)
                            break  # 只取第一个有效的生成回答
                    
                    # 只有当对话包含用户和助手消息时才添加
                    if len(conversation) == 2:
                        simplified_data["conversations"].append({
                            "question_id": question_data["question_id"],
                            "messages": conversation
                        })
                
                # 保存简化的JSON文件
                with open(self.current_json_file, 'w', encoding='utf-8') as f:
                    json.dump(simplified_data, f, ensure_ascii=False, indent=2)
                
                self.logger.info(f"📄 简化JSON数据已保存: {self.current_json_file}")
                
                # 统计信息
                total_conversations = len(simplified_data["conversations"])
                self.logger.info(f"   对话数量: {total_conversations}")
                self.logger.info(f"   文件大小: {os.path.getsize(self.current_json_file) / 1024:.1f} KB")
                
            except Exception as e:
                self.logger.error(f"❌ 保存JSON数据失败: {e}")
                import traceback
                self.logger.error(f"堆栈跟踪:\n{traceback.format_exc()}")
    
    def log_error(self, error_message: str, exception: Exception = None):
        """记录错误"""
        self.logger.error(f"❌ 错误: {error_message}")
        if exception:
            self.logger.error(f"异常详情: {str(exception)}")
            import traceback
            self.logger.error(f"堆栈跟踪:\n{traceback.format_exc()}")
    
    def get_current_log_file(self) -> Optional[str]:
        """获取当前日志文件路径"""
        return str(self.current_log_file) if self.current_log_file else None
    
    def get_current_json_file(self) -> Optional[str]:
        """获取当前JSON文件路径"""
        return str(self.current_json_file) if self.current_json_file else None
    
    def get_session_id(self) -> Optional[str]:
        """获取当前会话ID"""
        return self.session_id
    
    def get_session_data(self) -> Dict[str, Any]:
        """获取当前会话的完整数据"""
        return self.session_data.copy()
    
    @staticmethod
    def list_log_files(log_dir: str = "logs") -> list:
        """列出所有日志文件"""
        log_path = Path(log_dir)
        if not log_path.exists():
            return []
        
        log_files = []
        for log_file in log_path.glob("evaluation_*.log"):
            stat = log_file.stat()
            
            # 检查是否有对应的JSON文件
            json_file = log_file.with_suffix('.json')
            has_json = json_file.exists()
            json_size = json_file.stat().st_size if has_json else 0
            
            log_files.append({
                "filename": log_file.name,
                "path": str(log_file),
                "size": stat.st_size,
                "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "has_json": has_json,
                "json_file": str(json_file) if has_json else None,
                "json_size": json_size
            })
        
        # 按创建时间降序排列
        log_files.sort(key=lambda x: x["created_time"], reverse=True)
        return log_files
    
    @staticmethod
    def load_json_data(json_file_path: str) -> Optional[Dict[str, Any]]:
        """加载JSON格式的评估数据"""
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ 加载JSON数据失败: {e}")
            return None 