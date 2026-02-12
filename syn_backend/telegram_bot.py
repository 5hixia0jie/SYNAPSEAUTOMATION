#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram 机器人，用于接收视频链接并自动执行创意采集
"""

import os
import sys
import re
import logging
import asyncio
import urllib.parse
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# 导入必要的模块
import requests
from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from fastapi_app.core.config import settings
from fastapi_app.core.logger import logger
from fastapi_app.api.v1.creative_collection.services import CreativeCollectionService

# 配置日志
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Telegram 机器人令牌
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')

# 允许的用户 ID 列表（可选，用于限制访问）
ALLOWED_USER_IDS = os.getenv('ALLOWED_USER_IDS', '').split(',')
ALLOWED_USER_IDS = [int(user_id) for user_id in ALLOWED_USER_IDS if user_id]

# 创意采集 API 基础 URL
API_BASE_URL = f"http://localhost:{settings.PORT}/api/v1"

class TelegramBot:
    """Telegram 机器人类"""
    
    def __init__(self, token):
        """初始化机器人"""
        self.token = token
        self.application = Application.builder().token(token).build()
        self.service = CreativeCollectionService()
        self._register_handlers()
    
    def _register_handlers(self):
        """注册处理器"""
        # 命令处理器
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help))
        self.application.add_handler(CommandHandler("status", self.status))
        
        # 消息处理器
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /start 命令"""
        user = update.effective_user
        await update.message.reply_html(
            f"你好 {user.mention_html()}！\n\n" +
            "我是创意采集机器人，可以帮助你自动采集视频创意信息。\n\n" +
            "请直接发送视频链接，我会自动执行采集任务。\n\n" +
            "支持的平台：\n" +
            "- 抖音 (douyin.com)\n" +
            "- 头条 (toutiao.com)\n\n" +
            "示例：\n" +
            "https://www.douyin.com/video/1234567890\n" +
            "https://m.toutiao.com/is/yUQq2dpR7d0/\n\n" +
            "使用 /help 查看更多命令。",
            reply_markup=ForceReply(selective=True),
        )
    
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /help 命令"""
        await update.message.reply_text(
            "创意采集机器人帮助：\n\n" +
            "/start - 开始使用机器人\n" +
            "/help - 查看帮助信息\n" +
            "/status - 查看机器人状态\n\n" +
            "直接发送视频链接，我会自动执行采集任务。\n\n" +
            "支持的平台：\n" +
            "- 抖音 (douyin.com)\n" +
            "- 头条 (toutiao.com)\n\n" +
            "示例：\n" +
            "https://www.douyin.com/video/1234567890\n" +
            "https://m.toutiao.com/is/yUQq2dpR7d0/\n"
        )
    
    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /status 命令"""
        await update.message.reply_text(
            f"机器人状态：\n\n" +
            "状态：在线\n" +
            "版本：1.0.0\n" +
            f"服务端：{settings.PROJECT_NAME} v{settings.VERSION}\n" +
            f"API 地址：{API_BASE_URL}\n\n" +
            "支持的平台：\n" +
            "- 抖音 (douyin.com)\n" +
            "- 头条 (toutiao.com)\n"
        )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理消息"""
        user_id = update.effective_user.id
        
        # 检查用户是否被允许
        if ALLOWED_USER_IDS and user_id not in ALLOWED_USER_IDS:
            await update.message.reply_text("抱歉，你没有权限使用此机器人。")
            return
        
        message_text = update.message.text
        
        # 提取视频链接
        video_url = self._extract_video_url(message_text)
        
        if not video_url:
            await update.message.reply_text("请发送有效的视频链接。")
            return
        
        # 验证链接是否支持
        if not self._is_supported_platform(video_url):
            await update.message.reply_text("抱歉，目前只支持抖音和头条平台的视频链接。")
            return
        
        try:
            # 执行采集任务
            await update.message.reply_text(f"正在执行采集任务，请稍候...\n\n链接：{video_url}")
            
            # 调用创意采集服务
            task_id = await self.service.collect_video(video_url)
            
            # 等待任务完成
            await update.message.reply_text(f"采集任务已提交，任务 ID：{task_id}\n\n正在处理中，请稍候...")
            
            # 轮询任务状态
            status, progress, data = await self._wait_for_task_completion(task_id)
            
            if status == "completed" and data:
                # 任务完成
                title = data.get("title", "")
                tags = data.get("tags", [])
                cover_url = data.get("cover_url", "")
                
                # 构建回复消息
                reply_message = f"采集成功！\n\n标题：{title}\n"
                if tags:
                    reply_message += f"标签：{', '.join(tags)}\n"
                reply_message += f"封面链接：{cover_url}\n"
                reply_message += f"视频链接：{video_url}\n"
                
                await update.message.reply_text(reply_message)
            else:
                # 任务失败
                await update.message.reply_text(f"采集失败，请稍后重试。\n\n任务状态：{status}")
                
        except Exception as e:
            logger.error(f"处理消息失败: {e}")
            await update.message.reply_text(f"处理失败：{str(e)}")
    
    def _extract_video_url(self, text: str) -> str:
        """从文本中提取视频链接"""
        # 正则表达式匹配 URL
        url_regex = r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)'
        
        # 尝试匹配 URL
        match = re.search(url_regex, text)
        if match:
            # 返回完整的匹配结果
            return match.group(0)
        
        # 如果没有匹配到 URL，返回空字符串
        return ""
    
    def _is_supported_platform(self, url: str) -> bool:
        """检查链接是否来自支持的平台"""
        return "douyin.com" in url or "toutiao.com" in url
    
    async def _wait_for_task_completion(self, task_id: str, max_retries: int = 30, retry_interval: int = 2) -> tuple:
        """等待任务完成"""
        for _ in range(max_retries):
            status, progress, data = await self.service.get_task_status(task_id)
            
            if status in ["completed", "failed"]:
                return status, progress, data
            
            await asyncio.sleep(retry_interval)
        
        return "timeout", 0, None
    
    def run(self):
        """运行机器人"""
        logger.info("Telegram 机器人启动中...")
        logger.info(f"API 基础 URL: {API_BASE_URL}")
        logger.info(f"允许的用户 ID: {ALLOWED_USER_IDS}")
        
        try:
            # 启动机器人
            self.application.run_polling()
        except KeyboardInterrupt:
            logger.info("Telegram 机器人已停止")
        except Exception as e:
            logger.error(f"机器人运行失败: {e}")


if __name__ == "__main__":
    if not TELEGRAM_BOT_TOKEN:
        logger.error("请设置 TELEGRAM_BOT_TOKEN 环境变量")
        sys.exit(1)
    
    bot = TelegramBot(TELEGRAM_BOT_TOKEN)
    bot.run()
