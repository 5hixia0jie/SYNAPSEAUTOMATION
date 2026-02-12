#!/usr/bin/env python3
"""
测试修改后的 find_ffmpeg() 函数是否能正确找到ffmpeg
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath('.'))

from syn_backend.utils.video_frames import find_ffmpeg

def test_find_ffmpeg():
    """测试找到ffmpeg"""
    print("开始测试 find_ffmpeg() 函数...")
    
    ffmpeg_path = find_ffmpeg()
    
    if ffmpeg_path:
        print(f"✅ 成功找到ffmpeg: {ffmpeg_path}")
        print(f"✅ 文件存在: {os.path.exists(ffmpeg_path)}")
        
        # 测试运行ffmpeg
        try:
            import subprocess
            result = subprocess.run(
                [ffmpeg_path, "-version"], 
                capture_output=True, 
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                print("✅ ffmpeg 运行正常!")
                print(f"   版本信息: {result.stdout.splitlines()[0]}")
            else:
                print(f"❌ ffmpeg 运行失败: {result.stderr}")
        except Exception as e:
            print(f"❌ 测试运行ffmpeg失败: {e}")
    else:
        print("❌ 未找到ffmpeg!")

if __name__ == "__main__":
    test_find_ffmpeg()
