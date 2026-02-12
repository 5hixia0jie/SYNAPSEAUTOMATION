"""
AI服务，用于生成拍摄脚本
"""
import json
from typing import Dict, Any, Optional

from fastapi_app.core.logger import logger


class AIService:
    """AI服务"""
    
    def __init__(self):
        """初始化"""
        # 暂时不使用AIClient，直接返回默认脚本
        # 后续可以根据需要集成完整的AI服务
        pass
    
    async def generate_script(self, video_data: Dict[str, Any]) -> str:
        """生成拍摄脚本
        
        Args:
            video_data: 视频数据，包含标题、标签、字幕等信息
            
        Returns:
            生成的拍摄脚本
        """
        try:
            # 暂时直接返回默认脚本
            # 后续可以根据需要集成完整的AI服务
            logger.info("使用默认脚本")
            return self._generate_default_script(video_data)
            
        except Exception as e:
            logger.error(f"生成拍摄脚本失败: {e}")
            # 生成默认脚本
            return self._generate_default_script(video_data)
    
    def _build_prompt(self, video_data: Dict[str, Any]) -> str:
        """构建提示词
        
        Args:
            video_data: 视频数据
            
        Returns:
            提示词
        """
        title = video_data.get("title", "")
        tags = video_data.get("tags", [])
        subtitle = video_data.get("subtitle", "")
        
        prompt = f"请根据以下视频信息生成一份详细的拍摄脚本：\n\n"
        
        if title:
            prompt += f"视频标题：{title}\n\n"
        
        if tags:
            prompt += f"视频标签：{', '.join(tags)}\n\n"
        
        if subtitle:
            prompt += f"视频字幕：\n{subtitle}\n\n"
        
        prompt += "请按照以下结构生成拍摄脚本：\n\n"
        prompt += "# 拍摄脚本\n\n"
        prompt += "## 基本信息\n"
        prompt += "- 标题：[视频标题]\n"
        prompt += "- 风格：[视频风格]\n"
        prompt += "- 时长：[预计时长]\n\n"
        prompt += "## 开场\n"
        prompt += "- 镜头：[镜头类型和构图]\n"
        prompt += "- 画面：[画面内容描述]\n"
        prompt += "- 台词：[人物台词]\n"
        prompt += "- BGM：[背景音乐类型]\n\n"
        prompt += "## 主体部分\n"
        prompt += "- 镜头1：[镜头类型和构图]\n"
        prompt += "- 画面：[画面内容描述]\n"
        prompt += "- 台词：[人物台词]\n"
        prompt += "- 时长：[镜头时长]\n\n"
        prompt += "[可根据需要添加多个镜头]\n\n"
        prompt += "## 结尾\n"
        prompt += "- 镜头：[镜头类型和构图]\n"
        prompt += "- 画面：[画面内容描述]\n"
        prompt += "- 台词：[人物台词]\n"
        prompt += "- BGM：[背景音乐类型]\n\n"
        prompt += "## 拍摄建议\n"
        prompt += "- [拍摄技巧建议]\n"
        prompt += "- [灯光建议]\n"
        prompt += "- [道具建议]\n"
        prompt += "- [其他建议]\n"
        
        return prompt
    
    def _generate_default_script(self, video_data: Dict[str, Any]) -> str:
        """生成默认脚本
        
        Args:
            video_data: 视频数据
            
        Returns:
            默认脚本
        """
        title = video_data.get("title", "视频拍摄")
        
        default_script = f"# 拍摄脚本\n\n"
        default_script += "## 基本信息\n"
        default_script += f"- 标题：{title}\n"
        default_script += "- 风格：现代\n"
        default_script += "- 时长：1-3分钟\n\n"
        default_script += "## 开场\n"
        default_script += "- 镜头：全景\n"
        default_script += "- 画面：展示主要场景\n"
        default_script += "- 台词：大家好，欢迎观看本期视频\n"
        default_script += "- BGM：轻快的背景音乐\n\n"
        default_script += "## 主体部分\n"
        default_script += "- 镜头1：中景\n"
        default_script += "- 画面：主要内容展示\n"
        default_script += "- 台词：[根据视频内容填写]\n"
        default_script += "- 时长：30秒\n\n"
        default_script += "- 镜头2：近景\n"
        default_script += "- 画面：细节展示\n"
        default_script += "- 台词：[根据视频内容填写]\n"
        default_script += "- 时长：30秒\n\n"
        default_script += "## 结尾\n"
        default_script += "- 镜头：全景\n"
        default_script += "- 画面：总结场景\n"
        default_script += "- 台词：感谢观看，我们下期再见\n"
        default_script += "- BGM：渐弱的背景音乐\n\n"
        default_script += "## 拍摄建议\n"
        default_script += "- 确保光线充足\n"
        default_script += "- 保持画面稳定\n"
        default_script += "- 注意声音清晰\n"
        default_script += "- 根据实际场景调整镜头"
        
        return default_script
