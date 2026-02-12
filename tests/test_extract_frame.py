#!/usr/bin/env python3
"""
测试修改后的 extract_first_frame 函数
"""

import sys
import os
import tempfile

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath('.'))

from syn_backend.utils.video_frames import extract_first_frame

def test_extract_first_frame():
    """测试提取首帧"""
    print("开始测试 extract_first_frame() 函数...")
    
    # 使用用户的视频文件
    video_path = "D:\traeProject\SYNAPSEAUTOMATION\syn_backend\videoFile\e16b2aba-6974-4428-b0c4-acff8f34b75c.mp4"
    
    # 创建临时输出文件
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        out_path = tmp.name
    
    try:
        print(f"测试视频文件: {video_path}")
        print(f"输出路径: {out_path}")
        
        # 测试提取首帧
        extract_first_frame(video_path, out_path, overwrite=True)
        
        # 检查输出文件是否存在
        if os.path.exists(out_path):
            size = os.path.getsize(out_path)
            print(f"✅ 成功生成首帧/占位符: {out_path}")
            print(f"✅ 文件大小: {size} bytes")
        else:
            print("❌ 未生成输出文件")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    finally:
        # 清理临时文件
        if os.path.exists(out_path):
            os.unlink(out_path)
            print(f"清理临时文件: {out_path}")

if __name__ == "__main__":
    test_extract_first_frame()
