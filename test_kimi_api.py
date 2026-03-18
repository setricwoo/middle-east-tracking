#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试Kimi API Key是否可用"""
import requests

# 你的API Key
API_KEY = "sk-kimi-sptXqine0oziJgZ083ojdkJTJLuRz7yRVjuem6UEjVLREi5QbHCCeuvcTV9tH2NS"
BASE_URL = "https://api.moonshot.cn/v1"
MODEL = "kimi-k2-5"  # 使用kimi k2.5模型

def test_api():
    """测试API Key"""
    print("="*60)
    print("测试Kimi API Key")
    print("="*60)
    
    # 测试1: 获取模型列表
    print("\n[测试1] 获取模型列表...")
    try:
        response = requests.get(
            f"{BASE_URL}/models",
            headers={"Authorization": f"Bearer {API_KEY}"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("[OK] API Key有效！")
            print("\n可用模型:")
            for model in data.get('data', []):
                print(f"  - {model.get('id')}")
        else:
            print(f"[FAIL] 请求失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"[FAIL] 请求异常: {e}")
        return False
    
    # 测试2: 简单对话测试
    print("\n[测试2] 简单对话测试...")
    print(f"使用模型: {MODEL}")
    try:
        response = requests.post(
            f"{BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": "你是一个助手"},
                    {"role": "user", "content": "你好，请用一句话确认API正常工作"}
                ],
                "max_tokens": 100
            },
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            content = data['choices'][0]['message']['content']
            print("[OK] 对话测试成功！")
            print(f"\nAI回复: {content}")
            
            # 显示用量
            usage = data.get('usage', {})
            print(f"\nToken用量:")
            print(f"  输入: {usage.get('prompt_tokens', 0)}")
            print(f"  输出: {usage.get('completion_tokens', 0)}")
            print(f"  总计: {usage.get('total_tokens', 0)}")
            
            return True
        else:
            print(f"[FAIL] 对话测试失败: {response.status_code}")
            print(f"错误: {response.text}")
            return False
            
    except Exception as e:
        print(f"[FAIL] 请求异常: {e}")
        return False

def main():
    success = test_api()
    
    print("\n" + "="*60)
    if success:
        print("[OK] API Key 测试通过，可以正常使用！")
        print("\n配置到GitHub Secrets:")
        print("  KIMI_API_KEY = 你的API Key")
        print("  KIMI_BASE_URL = https://api.moonshot.cn/v1")
        print(f"  KIMI_MODEL = {MODEL}")
    else:
        print("[FAIL] API Key 测试失败，请检查Key是否正确")
    print("="*60)

if __name__ == "__main__":
    main()
