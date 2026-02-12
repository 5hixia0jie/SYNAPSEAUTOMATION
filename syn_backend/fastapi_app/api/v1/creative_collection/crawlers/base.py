"""
基础爬虫类
"""
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from fastapi_app.core.logger import logger


class BaseCrawler(ABC):
    """基础爬虫抽象类"""
    
    @abstractmethod
    async def crawl(self, url: str) -> Dict[str, Any]:
        """执行爬取
        
        Args:
            url: 视频链接
            
        Returns:
            包含视频信息的字典
        """
        pass
    
    async def _sleep(self, seconds: float):
        """睡眠
        
        Args:
            seconds: 睡眠时间
        """
        await asyncio.sleep(seconds)
    
    def _extract_video_id(self, url: str) -> Optional[str]:
        """从URL中提取视频ID
        
        Args:
            url: 视频链接
            
        Returns:
            视频ID
        """
        return None
    
    def _validate_url(self, url: str) -> bool:
        """验证URL是否有效
        
        Args:
            url: 视频链接
            
        Returns:
            是否有效
        """
        return True
