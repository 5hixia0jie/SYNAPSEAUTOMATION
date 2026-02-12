"""
爬虫模块
"""
from fastapi_app.api.v1.creative_collection.crawlers.douyin import DouyinCrawler
from fastapi_app.api.v1.creative_collection.crawlers.toutiao import ToutiaoCrawler

__all__ = ["DouyinCrawler", "ToutiaoCrawler"]
