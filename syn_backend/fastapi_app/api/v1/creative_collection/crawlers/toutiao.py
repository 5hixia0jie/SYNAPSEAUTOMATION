"""
头条爬虫
"""
import re
import asyncio
import sys
import os
import time
import subprocess
from typing import Dict, Any, Optional
from playwright.sync_api import sync_playwright
from pathlib import Path

from fastapi_app.core.logger import logger
from fastapi_app.core.config import settings
from fastapi_app.api.v1.creative_collection.crawlers.base import BaseCrawler


class ToutiaoCrawler(BaseCrawler):
    """头条爬虫"""
    
    def __init__(self):
        """初始化"""
        self.browser: Optional[Browser] = None
    
    async def crawl(self, url: str) -> Dict[str, Any]:
        """爬取头条视频信息
        
        Args:
            url: 头条视频链接
            
        Returns:
            包含视频信息的字典
        """
        if not self._validate_url(url):
            raise ValueError("无效的头条视频链接")
        
        logger.info(f"开始爬取头条视频: {url}")
        
        try:
            # 使用同步方式运行 Playwright，避免异步事件循环问题
            import threading
            result = []
            error = []
            
            def run_sync():
                try:
                    with sync_playwright() as p:
                        # 启动浏览器，尝试使用系统 Chrome 或 Playwright 内置浏览器
                        try:
                            # 尝试使用系统中的 Chrome 浏览器
                            chrome_path = None
                            # 检查常见的 Chrome 安装路径
                            chrome_paths = [
                                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                                os.environ.get("LOCALAPPDATA", "") + r"\Google\Chrome\Application\chrome.exe"
                            ]
                            for path in chrome_paths:
                                if os.path.exists(path):
                                    chrome_path = path
                                    break
                            
                            if chrome_path:
                                # 使用系统 Chrome
                                browser = p.chromium.launch(
                                    executable_path=chrome_path,
                                    headless=True,
                                    args=[
                                        "--no-sandbox",
                                        "--disable-setuid-sandbox",
                                        "--disable-dev-shm-usage",
                                        "--disable-accelerated-2d-canvas",
                                        "--no-first-run",
                                        "--no-zygote",
                                        "--disable-gpu"
                                    ]
                                )
                            else:
                                # 使用 Playwright 内置浏览器
                                browser = p.chromium.launch(
                                    headless=True,
                                    args=[
                                        "--no-sandbox",
                                        "--disable-setuid-sandbox",
                                        "--disable-dev-shm-usage",
                                        "--disable-accelerated-2d-canvas",
                                        "--no-first-run",
                                        "--no-zygote",
                                        "--disable-gpu"
                                    ]
                                )
                        except Exception as e:
                            # 如果失败，尝试不带 executable_path 启动
                            browser = p.chromium.launch(
                                headless=True,
                                args=[
                                    "--no-sandbox",
                                    "--disable-setuid-sandbox",
                                    "--disable-dev-shm-usage",
                                    "--disable-accelerated-2d-canvas",
                                    "--no-first-run",
                                    "--no-zygote",
                                    "--disable-gpu"
                                ]
                            )
                        
                        # 创建页面
                        page = browser.new_page(
                            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                        )
                        
                        # 设置超时
                        page.set_default_timeout(60000)  # 增加超时时间到60秒
                        
                        try:
                            # 访问页面，使用更宽松的等待策略
                            page.goto(url, wait_until="domcontentloaded")  # 使用domcontentloaded代替networkidle
                            
                            # 等待页面加载完成
                            page.wait_for_selector("body", timeout=40000)  # 增加等待时间到40秒
                            
                            # 等待额外的时间确保页面完全加载
                            page.wait_for_timeout(2000)  # 等待2秒
                            
                            logger.info(f"头条视频页面加载完成: {page.url}")

                            true_url = page.url

                            # 提取视频信息
                            title = self._extract_title_sync(page)
                            tags = self._extract_tags_sync(page)
                            video_url = self._extract_video_url_sync(page)
                            subtitle = self._extract_subtitle_sync(page)
                            
                            # 下载视频并截取首帧作为封面
                            cover_url = ""
                            if video_url:
                                try:
                                    video_path, cover_path = self._download_video_and_extract_cover(video_url, title)
                                    if cover_path:
                                        # 生成封面的相对路径或URL
                                        cover_url = self._get_cover_url(cover_path)
                                except Exception as e:
                                    logger.warning(f"视频下载失败，尝试从页面提取封面: {e}")
                                    # 备用方案：从页面提取封面图片
                                    cover_image_url = self._extract_cover_sync(page)
                                    if cover_image_url:
                                        cover_url = cover_image_url
                            
                            # 构建返回数据
                            data = {
                                "title": title,
                                "tags": tags,
                                "cover_url": cover_url,
                                "video_url": true_url,
                                "subtitle": subtitle
                            }
                            
                            logger.info(f"头条视频爬取成功: {data.get('title')}")
                            result.append(data)
                        finally:
                            page.close()
                            browser.close()
                except Exception as e:
                    error.append(e)
            
            # 创建并启动线程
            thread = threading.Thread(target=run_sync)
            thread.start()
            thread.join()
            
            # 检查是否有错误
            if error:
                raise error[0]
            
            # 返回结果
            if result:
                return result[0]
            else:
                raise Exception("爬取失败，未返回数据")
                
        except Exception as e:
            logger.error(f"头条视频爬取失败: {e}")
            raise
    
    def _download_video_and_extract_cover(self, video_url: str, title: str) -> tuple:
        """下载视频并使用ffmpeg截取首帧作为封面
        
        Args:
            video_url: 视频URL
            title: 视频标题
            
        Returns:
            (视频路径, 封面路径) 元组
        """
        try:
            # 修复视频URL，确保有协议前缀
            if video_url.startswith("//"):
                video_url = "https:" + video_url
            elif not video_url.startswith("http"):
                # 如果没有协议前缀，尝试添加https://
                video_url = "https://" + video_url
            
            # 创建保存目录
            video_dir = Path(settings.VIDEO_FILES_DIR) / "creative_collection"
            video_dir.mkdir(parents=True, exist_ok=True)
            
            # 生成文件名
            safe_title = "".join([c for c in title if c.isalnum() or c in "-_ "]).strip()[:50]
            if not safe_title:
                safe_title = f"video_{int(time.time())}"
            
            video_filename = f"{safe_title}.mp4"
            cover_filename = f"{safe_title}.jpg"
            
            video_path = video_dir / video_filename
            cover_path = video_dir / cover_filename
            
            # 下载视频（添加适当的请求头以避免403错误）
            logger.info(f"开始下载视频: {video_url}")
            import requests
            
            # 添加浏览器请求头，模拟真实用户请求
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Referer": "https://www.toutiao.com/",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
                "Connection": "keep-alive"
            }
            
            response = requests.get(video_url, stream=True, timeout=60, headers=headers)
            response.raise_for_status()
            
            with open(video_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            logger.info(f"视频下载成功: {video_path}")
            
            # 使用文件服务的方法截取首帧
            try:
                from utils.video_frames import extract_first_frame
                logger.info(f"开始截取视频首帧: {cover_path}")
                extract_first_frame(str(video_path), str(cover_path), overwrite=True)
                logger.info(f"首帧截取成功: {cover_path}")
            except Exception as e:
                logger.warning(f"截取视频首帧失败: {e}")
                # 备用方案：创建一个简单的封面图片
                try:
                    from PIL import Image, ImageDraw, ImageFont
                    # 创建一个简单的封面图片
                    img = Image.new('RGB', (640, 480), color=(30, 30, 30))
                    d = ImageDraw.Draw(img)
                    # 尝试添加标题文本
                    try:
                        # 尝试使用系统字体
                        font = ImageFont.truetype('arial.ttf', 24)
                    except:
                        # 如果没有找到字体，使用默认字体
                        font = ImageFont.load_default()
                    # 绘制标题
                    title_text = title[:50] + '...' if len(title) > 50 else title
                    d.text((20, 200), title_text, fill=(255, 255, 255), font=font)
                    # 保存图片
                    img.save(cover_path)
                    logger.info(f"创建默认封面成功: {cover_path}")
                except Exception as fallback_error:
                    logger.warning(f"创建默认封面失败: {fallback_error}")
            
            return str(video_path), str(cover_path) if cover_path.exists() else ""
            
        except Exception as e:
            logger.error(f"下载视频或截取首帧失败: {e}")
            return "", ""
    
    def _get_cover_url(self, cover_path: str) -> str:
        """获取封面的URL
        
        Args:
            cover_path: 封面文件路径
            
        Returns:
            str: 封面URL
        """
        try:
            # 生成相对路径
            video_dir = Path(settings.VIDEO_FILES_DIR)
            relative_path = Path(cover_path).relative_to(video_dir)
            # 构建URL，使用getFile接口，确保使用正斜杠
            relative_path_str = str(relative_path).replace('\\', '/')
            return f"/getFile?filename={relative_path_str}"
        except Exception as e:
            logger.error(f"生成封面URL失败: {e}")
            return cover_path
    
    def _extract_title_sync(self, page):
        """同步提取标题
        
        Args:
            page: Playwright页面对象
            
        Returns:
            标题
        """
        try:
            # 尝试从不同位置提取标题
            selectors = [
                ".article-title",
                "h1",
                ".title",
                ".video-title"
            ]
            
            for selector in selectors:
                try:
                    element = page.query_selector(selector)
                    if element:
                        text = element.inner_text()
                        if text.strip():
                            return text.strip()
                except:
                    continue
            
            # 尝试从meta标签提取
            title = page.title()
            if title and "头条" not in title:
                return title.strip()
            
            return ""
            
        except Exception as e:
            logger.error(f"提取标题失败: {e}")
            return ""
    
    def _extract_tags_sync(self, page):
        """同步提取标签
        
        Args:
            page: Playwright页面对象
            
        Returns:
            标签列表
        """
        try:
            tags = []
            
            # 尝试从不同位置提取标签
            selectors = [
                ".tags",
                ".tag",
                ".keywords",
                "a[href*='/tag/']"
            ]
            
            for selector in selectors:
                try:
                    elements = page.query_selector_all(selector)
                    for element in elements:
                        text = element.inner_text()
                        if text.strip() and text.strip() not in tags:
                            tags.append(text.strip())
                except:
                    continue
            
            return tags
            
        except Exception as e:
            logger.error(f"提取标签失败: {e}")
            return []
    
    def _extract_cover_sync(self, page):
        """同步提取封面
        
        Args:
            page: Playwright页面对象
            
        Returns:
            封面URL
        """
        try:
            # 尝试从不同位置提取封面
            selectors = [
                ".video-cover img",
                "img[class*='cover']",
                "meta[property='og:image']",
                ".article-cover img"
            ]
            
            for selector in selectors:
                try:
                    if selector.startswith("meta"):
                        # 从meta标签提取
                        content = page.evaluate(
                            f"document.querySelector('{selector}')?.getAttribute('content')"
                        )
                        if content:
                            return content
                    else:
                        # 从img标签提取
                        element = page.query_selector(selector)
                        if element:
                            src = element.get_attribute("src")
                            if src:
                                return src
                except:
                    continue
            
            return ""
            
        except Exception as e:
            logger.error(f"提取封面失败: {e}")
            return ""
    
    def _extract_video_url_sync(self, page):
        """同步提取视频URL
        
        Args:
            page: Playwright页面对象
            
        Returns:
            视频URL
        """
        try:
            # 尝试从不同位置提取视频URL
            selectors = [
                "video source",
                "video",
                ".video-player video"
            ]
            
            for selector in selectors:
                try:
                    element = page.query_selector(selector)
                    if element:
                        if selector == "video source":
                            src = element.get_attribute("src")
                            if src:
                                return src
                        else:
                            src = element.get_attribute("src")
                            if src:
                                return src
                except:
                    continue
            
            # 尝试从当前URL获取
            current_url = page.url
            return current_url
            
        except Exception as e:
            logger.error(f"提取视频URL失败: {e}")
            return page.url
    
    def _extract_subtitle_sync(self, page):
        """同步提取字幕
        
        Args:
            page: Playwright页面对象
            
        Returns:
            字幕文本
        """
        try:
            # 尝试提取字幕
            selectors = [
                ".subtitle",
                ".captions",
                ".video-subtitle"
            ]
            
            subtitles = []
            for selector in selectors:
                try:
                    elements = page.query_selector_all(selector)
                    for element in elements:
                        text = element.inner_text()
                        if text.strip():
                            subtitles.append(text.strip())
                except:
                    continue
            
            return "\n".join(subtitles)
            
        except Exception as e:
            logger.error(f"提取字幕失败: {e}")
            return ""
    
    def _validate_url(self, url: str) -> bool:
        """验证头条URL
        
        Args:
            url: 视频链接
            
        Returns:
            是否有效
        """
        return "toutiao.com" in url or "ixigua.com" in url
    
    def _extract_video_id(self, url: str) -> Optional[str]:
        """从URL中提取视频ID
        
        Args:
            url: 视频链接
            
        Returns:
            视频ID
        """
        try:
            # 匹配头条视频ID
            pattern = r"video/(\d+)"
            match = re.search(pattern, url)
            if match:
                return match.group(1)
            return None
        except:
            return None
