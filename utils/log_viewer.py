#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志查看工具
提供简单的日志文件管理和查看功能
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.evaluation.logger import EvaluationLogger


def list_evaluation_logs():
    """列出所有评估日志文件"""
    print("📋 评估日志文件列表:")
    print("=" * 80)
    
    log_files = EvaluationLogger.list_log_files()
    
    if not log_files:
        print("📭 暂无日志文件")
        return
    
    for i, log_file in enumerate(log_files, 1):
        filename = log_file['filename']
        size_kb = log_file['size'] / 1024
        created_time = datetime.fromisoformat(log_file['created_time']).strftime("%Y-%m-%d %H:%M:%S")
        
        # 解析文件名获取信息
        parts = filename.replace('evaluation_', '').replace('.log', '').split('_')
        if len(parts) >= 3:
            date_time = f"{parts[0]}_{parts[1]}"
            model = parts[2] if len(parts) > 2 else "unknown"
            dataset = '_'.join(parts[3:]) if len(parts) > 3 else "unknown"
            
            print(f"{i:2d}. {filename}")
            print(f"    📅 时间: {created_time}")
            print(f"    🤖 模型: {model}")
            print(f"    📊 数据集: {dataset}")
            print(f"    📁 大小: {size_kb:.1f} KB")
            print(f"    📍 路径: {log_file['path']}")
            
            # 显示JSON文件信息
            if log_file.get('has_json'):
                json_size_kb = log_file['json_size'] / 1024
                print(f"    📄 JSON数据: {json_size_kb:.1f} KB ({log_file['json_file']})")
            else:
                print(f"    📄 JSON数据: 无")
            print()


def view_log_file(log_path: str, lines: int = 50):
    """查看日志文件内容"""
    if not os.path.exists(log_path):
        print(f"❌ 日志文件不存在: {log_path}")
        return
    
    print(f"📖 查看日志文件: {os.path.basename(log_path)}")
    print("=" * 80)
    
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            content = f.readlines()
        
        total_lines = len(content)
        print(f"📄 总行数: {total_lines}")
        
        if lines == -1:  # 显示全部
            lines_to_show = content
            print("📺 显示全部内容:")
        else:
            lines_to_show = content[-lines:] if total_lines > lines else content
            print(f"📺 显示最后 {len(lines_to_show)} 行:")
        
        print("-" * 80)
        for line in lines_to_show:
            print(line.rstrip())
            
    except Exception as e:
        print(f"❌ 读取日志文件失败: {e}")


def view_json_data(json_path: str, section: str = "all"):
    """查看JSON格式的评估数据"""
    if not os.path.exists(json_path):
        print(f"❌ JSON文件不存在: {json_path}")
        return
    
    print(f"📄 查看JSON数据: {os.path.basename(json_path)}")
    print("=" * 80)
    
    try:
        data = EvaluationLogger.load_json_data(json_path)
        if not data:
            print("❌ 无法加载JSON数据")
            return
        
        if section == "info" or section == "all":
            print("📋 会话信息:")
            session_info = data.get('session_info', {})
            for key, value in session_info.items():
                print(f"  {key}: {value}")
            print()
        
        if section == "questions" or section == "all":
            questions = data.get('questions_and_answers', [])
            print(f"📝 问题和回答 ({len(questions)} 个):")
            
            for i, q in enumerate(questions, 1):
                print(f"\n{i}. 问题ID: {q.get('question_id')}")
                print(f"   问题内容: {q.get('question_content', '')[:100]}...")
                
                # 显示模型交互
                interactions = q.get('model_interactions', [])
                print(f"   模型交互: {len(interactions)} 次")
                
                for interaction in interactions:
                    if interaction['type'] == 'request':
                        print(f"     🔵 请求 -> {interaction['model_name']}")
                        print(f"        提示词长度: {interaction['prompt_length']} 字符")
                    elif interaction['type'] == 'response':
                        print(f"     🟢 响应 <- {interaction['model_name']}")
                        content = interaction.get('content', '')
                        print(f"        回答长度: {len(content)} 字符")
                        print(f"        Token使用: {interaction.get('tokens_used', 0)}")
                        if interaction.get('error'):
                            print(f"        ❌ 错误: {interaction['error']}")
                
                # 显示评估结果
                evaluation = q.get('evaluation_result', {})
                if evaluation:
                    scores = evaluation.get('scores', {})
                    print(f"   📊 评估结果:")
                    print(f"        总分: {scores.get('overall', 0):.1f}")
                    print(f"        准确性: {scores.get('accuracy', 0):.1f}")
                    print(f"        完整性: {scores.get('completeness', 0):.1f}")
                    print(f"        清晰度: {scores.get('clarity', 0):.1f}")
                    
                    if evaluation.get('feedback'):
                        print(f"        反馈: {evaluation['feedback'][:100]}...")
        
        if section == "summary" or section == "all":
            print("\n📈 会话总结:")
            summary = data.get('session_summary', {})
            for key, value in summary.items():
                if key == 'score_statistics':
                    print(f"  {key}:")
                    for metric, stats in value.items():
                        print(f"    {metric}: 平均{stats.get('mean', 0):.1f} 最高{stats.get('max', 0):.1f} 最低{stats.get('min', 0):.1f}")
                else:
                    print(f"  {key}: {value}")
        
        file_size = os.path.getsize(json_path) / 1024
        print(f"\n📁 文件大小: {file_size:.1f} KB")
        
    except Exception as e:
        print(f"❌ 读取JSON数据失败: {e}")


def export_qa_pairs(json_path: str, output_file: str = None):
    """导出问答对为简化的JSON格式"""
    if not os.path.exists(json_path):
        print(f"❌ JSON文件不存在: {json_path}")
        return
    
    try:
        data = EvaluationLogger.load_json_data(json_path)
        if not data:
            print("❌ 无法加载JSON数据")
            return
        
        # 提取问答对
        qa_pairs = []
        questions = data.get('questions_and_answers', [])
        
        for q in questions:
            # 获取问题
            question_data = {
                "question_id": q.get('question_id'),
                "question": q.get('question_content', ''),
                "full_question": q.get('full_question_data', {}),
                "model_responses": [],
                "evaluation": q.get('evaluation_result', {})
            }
            
            # 获取模型回答
            interactions = q.get('model_interactions', [])
            current_request = None
            
            for interaction in interactions:
                if interaction['type'] == 'request':
                    current_request = interaction
                elif interaction['type'] == 'response' and current_request:
                    response_data = {
                        "model_name": interaction['model_name'],
                        "request": {
                            "prompt": current_request.get('prompt', ''),
                            "config": current_request.get('config', {}),
                            "timestamp": current_request.get('timestamp', '')
                        },
                        "response": {
                            "content": interaction.get('content', ''),
                            "tokens_used": interaction.get('tokens_used', 0),
                            "timestamp": interaction.get('timestamp', ''),
                            "error": interaction.get('error')
                        }
                    }
                    question_data["model_responses"].append(response_data)
                    current_request = None
            
            qa_pairs.append(question_data)
        
        # 创建导出数据
        export_data = {
            "session_info": data.get('session_info', {}),
            "qa_pairs": qa_pairs,
            "summary": data.get('session_summary', {}),
            "export_time": datetime.now().isoformat()
        }
        
        # 确定输出文件名
        if not output_file:
            session_id = data.get('session_info', {}).get('session_id', 'unknown')
            output_file = f"qa_export_{session_id}.json"
        
        # 保存文件
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 问答对已导出到: {output_file}")
        print(f"📊 导出统计:")
        print(f"   问题数量: {len(qa_pairs)}")
        
        total_responses = sum(len(q['model_responses']) for q in qa_pairs)
        print(f"   回答数量: {total_responses}")
        
        file_size = os.path.getsize(output_file) / 1024
        print(f"   文件大小: {file_size:.1f} KB")
        
    except Exception as e:
        print(f"❌ 导出失败: {e}")


def search_logs(keyword: str):
    """在日志文件中搜索关键词"""
    print(f"🔍 在所有日志文件中搜索关键词: '{keyword}'")
    print("=" * 80)
    
    log_files = EvaluationLogger.list_log_files()
    found_results = []
    
    for log_file in log_files:
        log_path = log_file['path']
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                if keyword.lower() in line.lower():
                    found_results.append({
                        'file': os.path.basename(log_path),
                        'line_num': line_num,
                        'content': line.strip()
                    })
        except Exception as e:
            print(f"❌ 搜索文件 {log_path} 时出错: {e}")
    
    if found_results:
        print(f"✅ 找到 {len(found_results)} 个匹配结果:")
        print()
        
        for result in found_results:
            print(f"📁 {result['file']} (第{result['line_num']}行)")
            print(f"   {result['content']}")
            print()
    else:
        print(f"❌ 未找到包含关键词 '{keyword}' 的日志条目")


def cleanup_old_logs(days: int = 7):
    """清理N天前的旧日志文件"""
    print(f"🧹 清理 {days} 天前的旧日志文件...")
    
    log_files = EvaluationLogger.list_log_files()
    current_time = datetime.now()
    deleted_count = 0
    
    for log_file in log_files:
        created_time = datetime.fromisoformat(log_file['created_time'])
        age_days = (current_time - created_time).days
        
        if age_days > days:
            try:
                os.remove(log_file['path'])
                print(f"🗑️  删除: {log_file['filename']} (创建于 {age_days} 天前)")
                deleted_count += 1
                
                # 删除对应的JSON文件
                if log_file.get('has_json'):
                    os.remove(log_file['json_file'])
                    print(f"🗑️  删除JSON: {os.path.basename(log_file['json_file'])}")
                    
            except Exception as e:
                print(f"❌ 删除失败: {log_file['filename']} - {e}")
    
    if deleted_count > 0:
        print(f"✅ 成功删除 {deleted_count} 个旧日志文件")
    else:
        print("📭 没有需要清理的旧日志文件")

def cleanup_old_task_logs(max_tasks: int = 5):
    """清理旧任务的日志文件，只保留最近N个任务的日志"""
    try:
        print(f"🧹 自动清理旧任务日志，保留最近 {max_tasks} 个任务的日志...")
        
        log_files = EvaluationLogger.list_log_files()
        
        if len(log_files) <= max_tasks:
            print("📭 日志文件数量未超过限制，无需清理")
            return
        
        # 按创建时间倒序排序
        log_files.sort(key=lambda x: x['created_time'], reverse=True)
        
        # 保留最近的max_tasks个日志，删除其余的
        logs_to_keep = log_files[:max_tasks]
        logs_to_delete = log_files[max_tasks:]
        
        deleted_count = 0
        for log_file in logs_to_delete:
            try:
                # 删除日志文件
                os.remove(log_file['path'])
                deleted_count += 1
                print(f"🗑️  删除旧日志: {log_file['filename']}")
                
                # 删除对应的JSON文件
                if log_file.get('has_json'):
                    os.remove(log_file['json_file'])
                    print(f"🗑️  删除对应JSON: {os.path.basename(log_file['json_file'])}")
                    
            except Exception as e:
                print(f"❌ 删除日志失败: {log_file['filename']} - {e}")
        
        if deleted_count > 0:
            print(f"✅ 自动清理完成，删除了 {deleted_count} 个旧任务日志，保留最近的 {max_tasks} 个任务日志")
        else:
            print("📭 没有需要清理的旧任务日志")
            
    except Exception as e:
        print(f"❌ 自动清理任务日志失败: {e}")


def show_log_stats():
    """显示日志统计信息"""
    print("📊 日志统计信息:")
    print("=" * 80)
    
    log_files = EvaluationLogger.list_log_files()
    
    if not log_files:
        print("📭 暂无日志文件")
        return
    
    total_files = len(log_files)
    total_size = sum(f['size'] for f in log_files)
    total_json_files = sum(1 for f in log_files if f.get('has_json'))
    total_json_size = sum(f.get('json_size', 0) for f in log_files if f.get('has_json'))
    
    # 按模型统计
    models = {}
    datasets = {}
    
    for log_file in log_files:
        filename = log_file['filename']
        parts = filename.replace('evaluation_', '').replace('.log', '').split('_')
        
        if len(parts) >= 3:
            model = parts[2]
            dataset = '_'.join(parts[3:]) if len(parts) > 3 else "unknown"
            
            models[model] = models.get(model, 0) + 1
            datasets[dataset] = datasets.get(dataset, 0) + 1
    
    print(f"📁 总日志文件: {total_files}")
    print(f"📄 JSON数据文件: {total_json_files}")
    print(f"💾 总大小: {(total_size + total_json_size) / 1024:.1f} KB")
    print(f"   日志: {total_size / 1024:.1f} KB")
    print(f"   JSON: {total_json_size / 1024:.1f} KB")
    print()
    
    print("🤖 按模型统计:")
    for model, count in sorted(models.items()):
        print(f"   {model}: {count} 次评估")
    
    print()
    print("📊 按数据集统计:")
    for dataset, count in sorted(datasets.items()):
        print(f"   {dataset}: {count} 次评估")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("📋 日志查看工具使用说明:")
        print("python utils/log_viewer.py <command> [options]")
        print()
        print("可用命令:")
        print("  list                        - 列出所有日志文件")
        print("  view <file_path> [n]        - 查看日志文件 (可选: 显示行数, -1表示全部)")
        print("  json <json_path> [section]  - 查看JSON数据 (section: info/questions/summary/all)")
        print("  export <json_path> [output] - 导出问答对为简化JSON格式")
        print("  search <keyword>            - 搜索关键词")
        print("  stats                       - 显示统计信息")
        print("  cleanup [days]              - 清理旧日志 (默认7天)")
        print()
        print("示例:")
        print("  python utils/log_viewer.py list")
        print("  python utils/log_viewer.py view logs/evaluation_xxx.log 100")
        print("  python utils/log_viewer.py json logs/evaluation_xxx.json questions")
        print("  python utils/log_viewer.py export logs/evaluation_xxx.json qa_output.json")
        print("  python utils/log_viewer.py search '错误'")
        print("  python utils/log_viewer.py cleanup 7")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'list':
        list_evaluation_logs()
    
    elif command == 'view':
        if len(sys.argv) < 3:
            print("❌ 请指定要查看的日志文件路径")
            return
        
        log_path = sys.argv[2]
        lines = int(sys.argv[3]) if len(sys.argv) > 3 else 50
        view_log_file(log_path, lines)
    
    elif command == 'json':
        if len(sys.argv) < 3:
            print("❌ 请指定要查看的JSON文件路径")
            return
        
        json_path = sys.argv[2]
        section = sys.argv[3] if len(sys.argv) > 3 else "all"
        view_json_data(json_path, section)
    
    elif command == 'export':
        if len(sys.argv) < 3:
            print("❌ 请指定要导出的JSON文件路径")
            return
        
        json_path = sys.argv[2]
        output_file = sys.argv[3] if len(sys.argv) > 3 else None
        export_qa_pairs(json_path, output_file)
    
    elif command == 'search':
        if len(sys.argv) < 3:
            print("❌ 请指定搜索关键词")
            return
        
        keyword = sys.argv[2]
        search_logs(keyword)
    
    elif command == 'stats':
        show_log_stats()
    
    elif command == 'cleanup':
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        cleanup_old_logs(days)
    
    else:
        print(f"❌ 未知命令: {command}")
        print("使用 'python utils/log_viewer.py' 查看帮助")


if __name__ == "__main__":
    main() 