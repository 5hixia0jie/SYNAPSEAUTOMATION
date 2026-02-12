"""
创意采集API路由
"""
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from fastapi_app.core.config import settings
from fastapi_app.core.logger import logger
from fastapi_app.schemas.common import Response
from fastapi_app.api.v1.creative_collection.services import CreativeCollectionService

router = APIRouter(prefix="/creative_collection", tags=["CreativeCollection"])


class CollectRequest(BaseModel):
    """采集请求模型"""
    video_url: str = Field(..., description="视频链接", example="https://www.douyin.com/video/1234567890")


class CollectResponse(BaseModel):
    """采集响应模型"""
    task_id: str = Field(..., description="任务ID")


class CreativeCollectionItem(BaseModel):
    """创意采集项目模型"""
    id: int = Field(..., description="ID")
    title: str = Field(..., description="标题")
    tags: List[str] = Field(..., description="标签")
    cover_url: str = Field(..., description="封面URL")
    video_url: str = Field(..., description="视频URL")
    script: str = Field(..., description="拍摄脚本")
    source_platform: str = Field(..., description="来源平台")
    status: str = Field(..., description="状态")
    error_message: Optional[str] = Field(None, description="错误信息")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")


class CrawlerResult(BaseModel):
    """爬虫结果模型"""
    title: str = Field(..., description="标题")
    tags: List[str] = Field(default_factory=list, description="标签")
    cover_url: str = Field(default="", description="封面URL")
    video_url: str = Field(..., description="视频URL")
    subtitle: str = Field(default="", description="字幕")


class ListResponse(BaseModel):
    """列表响应模型"""
    items: List[CreativeCollectionItem] = Field(..., description="项目列表")
    total: int = Field(..., description="总数")


class StatusResponse(BaseModel):
    """状态响应模型"""
    status: str = Field(..., description="状态")
    progress: int = Field(..., description="进度")
    data: Optional[CrawlerResult] = Field(None, description="数据")


@router.post("/collect", response_model=Response[CollectResponse])
async def collect_video(payload: CollectRequest):
    """
    提交视频采集任务
    
    - **video_url**: 视频链接，支持头条和抖音
    """
    try:
        service = CreativeCollectionService()
        task_id = await service.collect_video(payload.video_url)
        return Response(success=True, data=CollectResponse(task_id=task_id))
    except Exception as exc:
        logger.error(f"[CreativeCollection] Collect video failed: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/list", response_model=Response[ListResponse])
async def get_collection_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页大小"),
    status: Optional[str] = Query(None, description="状态筛选"),
    platform: Optional[str] = Query(None, description="平台筛选")
):
    """
    获取创意采集列表
    
    - **page**: 页码，默认1
    - **page_size**: 每页大小，默认10
    - **status**: 状态筛选，可选
    - **platform**: 平台筛选，可选
    """
    try:
        service = CreativeCollectionService()
        items, total = await service.get_collection_list(
            page=page,
            page_size=page_size,
            status=status,
            platform=platform
        )
        return Response(success=True, data=ListResponse(items=items, total=total))
    except Exception as exc:
        logger.error(f"[CreativeCollection] Get list failed: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/{id}", response_model=Response[CreativeCollectionItem])
async def get_collection_detail(id: int):
    """
    获取创意采集详情
    
    - **id**: 项目ID
    """
    try:
        service = CreativeCollectionService()
        item = await service.get_collection_detail(id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        return Response(success=True, data=item)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"[CreativeCollection] Get detail failed: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@router.delete("/{id}", response_model=Response[Dict[str, Any]])
async def delete_collection(id: int):
    """
    删除创意采集项目
    
    - **id**: 项目ID
    """
    try:
        service = CreativeCollectionService()
        await service.delete_collection(id)
        return Response(success=True, data={"message": "Deleted successfully"})
    except Exception as exc:
        logger.error(f"[CreativeCollection] Delete failed: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/status/{task_id}", response_model=Response[StatusResponse])
async def get_task_status(task_id: str):
    """
    获取采集任务状态
    
    - **task_id**: 任务ID
    """
    try:
        service = CreativeCollectionService()
        status, progress, data = await service.get_task_status(task_id)
        return Response(success=True, data=StatusResponse(
            status=status,
            progress=progress,
            data=data
        ))
    except Exception as exc:
        logger.error(f"[CreativeCollection] Get task status failed: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))
