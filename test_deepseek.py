#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DeepSeek API 连接测试脚本
用于验证 API Key 和网络连接是否正常
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

# 加载环境变量
load_dotenv()

def test_deepseek_api():
    """测试 DeepSeek API 连接"""
    
    # 读取配置
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    base_url = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    
    print("=" * 60)
    print("DeepSeek API 连接测试")
    print("=" * 60)
    
    # 1. 检查 API Key
    print(f"\n1. API Key 检查:")
    if not api_key:
        print("   ❌ 错误: API Key 未配置")
        print("   请在 .env 文件中设置 DEEPSEEK_API_KEY")
        return False
    
    print(f"   ✓ API Key 已配置")
    print(f"   ✓ Key 长度: {len(api_key)} 字符")
    print(f"   ✓ Key 前缀: {api_key[:10]}...")
    
    # 2. 检查 Base URL
    print(f"\n2. Base URL 检查:")
    print(f"   ✓ Base URL: {base_url}")
    
    # 3. 测试 API 连接
    print(f"\n3. API 连接测试:")
    print(f"   正在连接到 {base_url}...")
    
    try:
        # 初始化客户端
        client = OpenAI(api_key=api_key, base_url=base_url)
        
        # 发送测试请求
        print("   发送测试消息...")
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "user", "content": "你好，请回复'测试成功'"}
            ],
            max_tokens=50
        )
        
        # 检查响应
        if response.choices and len(response.choices) > 0:
            content = response.choices[0].message.content
            print(f"   ✓ 连接成功!")
            print(f"   ✓ AI 回复: {content}")
            print(f"\n" + "=" * 60)
            print("✅ 所有测试通过！DeepSeek API 配置正确。")
            print("=" * 60)
            return True
        else:
            print("   ❌ 响应格式异常")
            return False
            
    except Exception as e:
        print(f"   ❌ 连接失败!")
        print(f"   错误类型: {type(e).__name__}")
        print(f"   错误信息: {str(e)}")
        print(f"\n" + "=" * 60)
        print("❌ 测试失败，请检查以下几点:")
        print("=" * 60)
        print("1. API Key 是否正确（在 DeepSeek 平台获取）")
        print("2. 网络连接是否正常（可能需要代理）")
        print("3. Base URL 是否正确")
        print("4. API Key 是否有效（未过期）")
        return False

if __name__ == "__main__":
    success = test_deepseek_api()
    exit(0 if success else 1)
