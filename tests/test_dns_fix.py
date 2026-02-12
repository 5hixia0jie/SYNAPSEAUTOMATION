#!/usr/bin/env python3
"""
测试DNS解析修复是否有效
用于验证aiohttp客户端是否能正确解析B站上传服务器域名
"""

import asyncio
import aiohttp

async def test_dns_resolution():
    """测试DNS解析"""
    print("开始测试DNS解析...")
    
    # 测试域名
    test_domain = "upos-cs-upcdntx.bilivideo.com"
    
    try:
        # 使用默认DNS解析
        print(f"\n1. 测试默认DNS解析 {test_domain}:")
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://{test_domain}", timeout=10) as response:
                print(f"   连接成功! 状态码: {response.status}")
                print(f"   URL: {response.url}")
    except Exception as e:
        print(f"   连接失败: {e}")
    
    try:
        # 使用配置的DNS服务器解析（与修复中使用的相同）
        print(f"\n2. 测试配置DNS解析 {test_domain}:")
        resolver = aiohttp.AsyncResolver(nameservers=["223.5.5.5", "223.6.6.6"])
        connector = aiohttp.TCPConnector(resolver=resolver, limit_per_host=100)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(f"https://{test_domain}", timeout=10) as response:
                print(f"   连接成功! 状态码: {response.status}")
                print(f"   URL: {response.url}")
    except Exception as e:
        print(f"   连接失败: {e}")
    
    print("\nDNS解析测试完成!")

if __name__ == "__main__":
    asyncio.run(test_dns_resolution())
