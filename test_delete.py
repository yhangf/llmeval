#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试删除模型功能
"""

import requests
import json

def test_delete_function():
    """测试删除功能"""
    base_url = "http://127.0.0.1:8000"
    
    print("=== 删除功能测试 ===\n")
    
    # 1. 获取当前模型列表
    print("1. 获取当前模型列表...")
    try:
        response = requests.get(f"{base_url}/api/models")
        if response.status_code == 200:
            data = response.json()
            models = data.get('data', [])
            print(f"   当前模型数量: {len(models)}")
            for i, model in enumerate(models):
                print(f"   {i+1}. {model['name']} ({model['type']})")
        else:
            print(f"   获取失败: {response.status_code}")
            return
    except Exception as e:
        print(f"   连接失败: {e}")
        return
    
    if not models:
        print("   没有模型可以测试删除功能")
        return
    
    print()
    
    # 2. 添加一个测试模型用于删除
    print("2. 添加测试模型...")
    test_model = {
        "name": "delete-test-model",
        "provider": "custom",
        "model_id": "test-delete",
        "api_key": "test-key",
        "base_url": "http://test.com",
        "max_tokens": 4000,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(f"{base_url}/api/models", json=test_model)
        if response.status_code == 200:
            print("   ✅ 测试模型添加成功")
        else:
            print(f"   ❌ 添加失败: {response.status_code}")
            print(f"   响应: {response.text}")
            return
    except Exception as e:
        print(f"   添加失败: {e}")
        return
    
    print()
    
    # 3. 尝试删除测试模型
    print("3. 删除测试模型...")
    try:
        response = requests.delete(f"{base_url}/api/models/delete-test-model")
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   响应: {data}")
            if data.get('success'):
                print("   ✅ 删除成功！")
            else:
                print("   ❌ 删除失败")
        else:
            try:
                error_data = response.json()
                print(f"   错误响应: {error_data}")
            except:
                print(f"   错误文本: {response.text}")
                
    except Exception as e:
        print(f"   删除请求失败: {e}")
    
    print()
    
    # 4. 验证模型是否被删除
    print("4. 验证模型是否被删除...")
    try:
        response = requests.get(f"{base_url}/api/models")
        if response.status_code == 200:
            data = response.json()
            current_models = data.get('data', [])
            test_model_exists = any(m['name'] == 'delete-test-model' for m in current_models)
            
            if not test_model_exists:
                print("   ✅ 测试模型已成功删除")
            else:
                print("   ❌ 测试模型仍然存在")
                
            print(f"   当前模型数量: {len(current_models)}")
        else:
            print(f"   验证失败: {response.status_code}")
    except Exception as e:
        print(f"   验证失败: {e}")
    
    print()
    print("=== 测试完成 ===")

if __name__ == "__main__":
    test_delete_function() 