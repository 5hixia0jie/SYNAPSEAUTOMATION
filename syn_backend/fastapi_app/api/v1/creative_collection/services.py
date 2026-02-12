"""
创意采集服务
"""
import asyncio
import json
import os
import time
import uuid
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from pathlib import Path

from fastapi_app.core.config import settings
from fastapi_app.core.logger import logger
from fastapi_app.api.v1.creative_collection.crawlers import DouyinCrawler, ToutiaoCrawler
from fastapi_app.api.v1.creative_collection.ai_service import AIService


class CreativeCollectionService:
    """创意采集服务"""
    
    def __init__(self):
        """初始化服务"""
        self.db_path = Path(settings.DATA_DIR) / "creative_collection"
        self.db_path.mkdir(parents=True, exist_ok=True)
        self.db_file = self.db_path / "collections.json"
        self.tasks_file = self.db_path / "tasks.json"
        
        # 初始化数据库文件
        self._init_db()
        
        # 初始化爬虫
        self.douyin_crawler = DouyinCrawler()
        self.toutiao_crawler = ToutiaoCrawler()
        
        # 初始化AI服务
        self.ai_service = AIService()
    
    def _init_db(self):
        """初始化数据库文件"""
        if not self.db_file.exists():
            self.db_file.write_text(json.dumps([], ensure_ascii=False, indent=2), encoding="utf-8")
        
        if not self.tasks_file.exists():
            self.tasks_file.write_text(json.dumps({}, ensure_ascii=False, indent=2), encoding="utf-8")
    
    def _load_collections(self) -> List[Dict[str, Any]]:
        """加载采集数据"""
        try:
            with open(self.db_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载采集数据失败: {e}")
            return []
    
    def _save_collections(self, collections: List[Dict[str, Any]]):
        """保存采集数据"""
        try:
            with open(self.db_file, "w", encoding="utf-8") as f:
                json.dump(collections, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存采集数据失败: {e}")
    
    def _load_tasks(self) -> Dict[str, Any]:
        """加载任务数据"""
        try:
            with open(self.tasks_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载任务数据失败: {e}")
            return {}
    
    def _save_tasks(self, tasks: Dict[str, Any]):
        """保存任务数据"""
        try:
            with open(self.tasks_file, "w", encoding="utf-8") as f:
                json.dump(tasks, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存任务数据失败: {e}")
    
    def _get_next_id(self) -> int:
        """获取下一个ID"""
        collections = self._load_collections()
        if not collections:
            return 1
        return max(item.get("id", 0) for item in collections) + 1
    
    def _detect_platform(self, video_url: str) -> Optional[str]:
        """检测视频平台"""
        if "douyin.com" in video_url:
            return "douyin"
        elif "toutiao.com" in video_url:
            return "toutiao"
        return None
    
    async def collect_video(self, video_url: str) -> str:
        """采集视频信息"""
        # 生成任务ID
        task_id = str(uuid.uuid4())
        
        # 保存任务状态
        tasks = self._load_tasks()
        tasks[task_id] = {
            "status": "pending",
            "progress": 0,
            "video_url": video_url,
            "created_at": datetime.now().isoformat()
        }
        self._save_tasks(tasks)
        
        # 异步执行采集任务
        asyncio.create_task(self._process_collect(task_id, video_url))
        
        return task_id
    
    async def _process_collect(self, task_id: str, video_url: str):
        """处理采集任务"""
        tasks = self._load_tasks()
        task = tasks.get(task_id)
        
        if not task:
            return
        
        try:
            # 更新任务状态为处理中
            task["status"] = "processing"
            task["progress"] = 10
            self._save_tasks(tasks)
            
            # 检测平台
            platform = self._detect_platform(video_url)
            if not platform:
                raise ValueError("不支持的视频平台，仅支持抖音和头条")
            
            # 更新进度
            task["progress"] = 20
            self._save_tasks(tasks)
            
            # 执行采集
            if platform == "douyin":
                data = await self.douyin_crawler.crawl(video_url)
            else:
                data = await self.toutiao_crawler.crawl(video_url)
            
            # 更新进度
            task["progress"] = 80
            self._save_tasks(tasks)
            
            # 保存采集记录
            collection = {
                "id": self._get_next_id(),
                "title": data.get("title", ""),
                "tags": data.get("tags", []),
                "cover_url": data.get("cover_url", ""),
                "video_url": data.get("video_url", video_url),
                "script": "",  # 不再生成拍摄脚本
                "source_platform": "抖音" if platform == "douyin" else "头条",
                "status": "success",
                "error_message": None,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            collections = self._load_collections()
            collections.append(collection)
            self._save_collections(collections)
            
            # 更新任务状态为完成
            task["status"] = "completed"
            task["progress"] = 100
            task["data"] = data
            self._save_tasks(tasks)
            
        except Exception as e:
            logger.error(f"采集任务失败: {e}")
            
            # 保存失败记录
            collection = {
                "id": self._get_next_id(),
                "title": "",
                "tags": [],
                "cover_url": "",
                "video_url": video_url,
                "script": "",
                "source_platform": "抖音" if platform == "douyin" else "头条" if platform else "未知",
                "status": "failed",
                "error_message": str(e),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            collections = self._load_collections()
            collections.append(collection)
            self._save_collections(collections)
            
            # 更新任务状态为失败
            task["status"] = "failed"
            task["progress"] = 100
            task["error"] = str(e)
            self._save_tasks(tasks)
    
    async def get_collection_list(
        self, 
        page: int = 1, 
        page_size: int = 10, 
        status: Optional[str] = None, 
        platform: Optional[str] = None
    ) -> Tuple[List[Dict[str, Any]], int]:
        """获取采集列表"""
        collections = self._load_collections()
        
        # 筛选
        filtered = []
        for item in collections:
            if status and item.get("status") != status:
                continue
            if platform and item.get("source_platform") != platform:
                continue
            filtered.append(item)
        
        # 排序（按创建时间倒序）
        filtered.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        # 分页
        total = len(filtered)
        start = (page - 1) * page_size
        end = start + page_size
        items = filtered[start:end]
        
        return items, total
    
    async def get_collection_detail(self, item_id: int) -> Optional[Dict[str, Any]]:
        """获取采集详情"""
        collections = self._load_collections()
        for item in collections:
            if item.get("id") == item_id:
                return item
        return None
    
    async def delete_collection(self, item_id: int):
        """删除采集项目"""
        collections = self._load_collections()
        
        # 找到要删除的项目
        item_to_delete = None
        for item in collections:
            if item.get("id") == item_id:
                item_to_delete = item
                break
        
        # 删除对应的文件
        if item_to_delete:
            try:
                # 提取封面文件路径
                cover_url = item_to_delete.get("cover_url", "")
                if cover_url:
                    # 从 cover_url 中提取 filename 参数
                    import urllib.parse
                    parsed = urllib.parse.urlparse(cover_url)
                    if parsed.path == "/getFile":
                        params = urllib.parse.parse_qs(parsed.query)
                        if "filename" in params:
                            filename = params["filename"][0]
                            # 构建完整的文件路径
                            cover_path = Path(settings.VIDEO_FILES_DIR) / filename
                            # 删除封面文件
                            if cover_path.exists():
                                cover_path.unlink()
                                logger.info(f"删除封面文件成功: {cover_path}")
                            
                            # 构建视频文件路径（与封面文件同名，但是扩展名为 .mp4）
                            video_path = cover_path.with_suffix(".mp4")
                            # 删除视频文件
                            if video_path.exists():
                                video_path.unlink()
                                logger.info(f"删除视频文件成功: {video_path}")
            except Exception as e:
                logger.error(f"删除文件失败: {e}")
        
        # 删除采集项目记录
        filtered = [item for item in collections if item.get("id") != item_id]
        self._save_collections(filtered)
    
    async def get_task_status(self, task_id: str) -> Tuple[str, int, Optional[Dict[str, Any]]]:
        """获取任务状态"""
        tasks = self._load_tasks()
        task = tasks.get(task_id)
        
        if not task:
            return "not_found", 0, None
        
        status = task.get("status", "unknown")
        progress = task.get("progress", 0)
        data = task.get("data", None)
        
        return status, progress, data
