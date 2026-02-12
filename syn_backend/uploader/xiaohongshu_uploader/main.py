# -*- coding: utf-8 -*-
from datetime import datetime

from playwright.async_api import Playwright, async_playwright, Page
import os
import asyncio

from config.conf import LOCAL_CHROME_PATH
from utils.base_social_media import set_init_script, HEADLESS_FLAG
from myUtils.browser_context import build_context_options
from myUtils.close_guide import try_close_guide
from utils.log import xiaohongshu_logger

XHS_TOUR_CONTAINERS = [
    ".semi-modal",
    ".guide-modal",
    "[role='dialog']",
    ".semi-modal-content",
    ".semi-modal-body",
]

XHS_TOUR_BTNS = [
    'button:has-text("我知道了")',
    'button:has-text("知道了")',
    'button:has-text("关闭")',
    '[aria-label="关闭"]',
    '[aria-label="close"]',
]


async def dismiss_xhs_tour(page, max_attempts: int = 6):
    """尝试关闭小红书发布页/创作中心的新手引导弹窗。"""
    for _ in range(max_attempts):
        has_popup = False
        for sel in XHS_TOUR_CONTAINERS:
            loc = page.locator(sel)
            if await loc.count() > 0 and await loc.first.is_visible():
                has_popup = True
                break
        if not has_popup:
            return

        clicked = False
        for btn_sel in XHS_TOUR_BTNS:
            btn = page.locator(btn_sel)
            if await btn.count() > 0 and await btn.first.is_visible():
                try:
                    await btn.first.click()
                    clicked = True
                    await page.wait_for_timeout(300)
                    break
                except Exception:
                    continue
        if not clicked:
            break


XHS_TOUR_CONTAINERS = [
    '[role="dialog"]',
    '[aria-modal="true"]',
    '.modal-wrap',
    '.guide-dialog',
    '.tour-modal',
    '.xh-dialog',
    '.xh-guide',
    '.guide-container',
]

XHS_TOUR_BTNS = [
    'button:has-text("下一步")',
    'button:has-text("知道了")',
    'button:has-text("我知道了")',
    'button:has-text("跳过")',
    'button:has-text("完成")',
    '[aria-label="关闭"]',
]


async def dismiss_xhs_tour(page, max_attempts: int = 6):
    """尝试关闭小红书发布页的新手引导弹窗。"""
    for _ in range(max_attempts):
        has_popup = False
        for sel in XHS_TOUR_CONTAINERS:
            loc = page.locator(sel)
            if await loc.count() > 0 and await loc.first.is_visible():
                has_popup = True
                break
        if not has_popup:
            return

        clicked = False
        for btn_sel in XHS_TOUR_BTNS:
            btn = page.locator(btn_sel)
            if await btn.count() > 0 and await btn.first.is_visible():
                try:
                    await btn.first.click()
                    clicked = True
                    await page.wait_for_timeout(300)
                    break
                except Exception:
                    continue
        if not clicked:
            break


async def cookie_auth(account_file):
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=HEADLESS_FLAG)
        context = await browser.new_context(**build_context_options(storage_state=account_file))
        context = await set_init_script(context)
        # 创建一个新的页面
        page = await context.new_page()
        # 访问指定的 URL
        await page.goto("https://creator.xiaohongshu.com/creator-micro/content/upload")
        try:
            await try_close_guide(page, "xiaohongshu")
        except Exception:
            pass
        try:
            # 使用轮询方式替代wait_for_url
            url_match = False
            for _ in range(10):  # 最多尝试10次，每次0.5秒
                current_url = page.url
                if "https://creator.xiaohongshu.com/creator-micro/content/upload" in current_url:
                    url_match = True
                    break
                await asyncio.sleep(0.5)
            
            if not url_match:
                raise Exception("URL未匹配")
        except:
            print("[+] 等待5秒 cookie 失效")
            await context.close()
            await browser.close()
            return False
        # 2024.06.17 抖音创作者中心改版
        if await page.get_by_text('手机号登录').count() or await page.get_by_text('扫码登录').count():
            print("[+] 等待5秒 cookie 失效")
            return False
        else:
            print("[+] cookie 有效")
            return True


async def xiaohongshu_setup(account_file, handle=False):
    if not os.path.exists(account_file) or not await cookie_auth(account_file):
        if not handle:
            # Todo alert message
            return False
        xiaohongshu_logger.info('[+] cookie文件不存在或已失效，即将自动打开浏览器，请扫码登录，登陆后会自动生成cookie文件')
        await xiaohongshu_cookie_gen(account_file)
    return True


async def xiaohongshu_cookie_gen(account_file):
    async with async_playwright() as playwright:
        options = {
            'headless': HEADLESS_FLAG
        }
        # Make sure to run headed.
        browser = await playwright.chromium.launch(**options)
        # Setup context however you like.
        context = await browser.new_context(**build_context_options())  # Pass any options
        context = await set_init_script(context)
        # Pause the page, and start recording manually.
        page = await context.new_page()
        await page.goto("https://creator.xiaohongshu.com/")
        await page.pause()
        # 点击调试器的继续，保存cookie
        await context.storage_state(path=account_file)


class XiaoHongShuVideo(object):
    def __init__(self, title, file_path, tags, publish_date: datetime, account_file, thumbnail_path=None, proxy=None):
        self.title = title  # 视频标题
        self.file_path = file_path
        self.tags = tags
        self.publish_date = publish_date
        self.account_file = account_file
        self.date_format = '%Y年%m月%d日 %H:%M'
        self.local_executable_path = LOCAL_CHROME_PATH
        self.thumbnail_path = thumbnail_path
        self.proxy = proxy

    async def set_schedule_time_xiaohongshu(self, page, publish_date):
        print("  [-] 正在设置定时发布时间...")
        print(f"publish_date: {publish_date}")

        # 使用文本内容定位元素
        # element = await page.wait_for_selector(
        #     'label:has-text("定时发布")',
        #     timeout=5000  # 5秒超时时间
        # )
        # await element.click()

        # # 选择包含特定文本内容的 label 元素
        label_element = page.locator("label:has-text('定时发布')")
        # # 在选中的 label 元素下点击 checkbox
        await label_element.click()
        await asyncio.sleep(1)
        publish_date_hour = publish_date.strftime("%Y-%m-%d %H:%M")
        print(f"publish_date_hour: {publish_date_hour}")

        await asyncio.sleep(1)
        await page.locator('.el-input__inner[placeholder="选择日期和时间"]').click()
        await page.keyboard.press("Control+KeyA")
        await page.keyboard.type(str(publish_date_hour))
        await page.keyboard.press("Enter")

        await asyncio.sleep(1)

    async def handle_upload_error(self, page):
        xiaohongshu_logger.info('视频出错了，重新上传中')
        await page.locator('div.progress-div [class^="upload-btn-input"]').set_input_files(self.file_path)

    async def upload(self, playwright: Playwright) -> None:
        # 使用 Chromium 浏览器启动一个浏览器实例
        launch_kwargs = {
            "headless": HEADLESS_FLAG
        }
        if self.local_executable_path:
            launch_kwargs["executable_path"] = self.local_executable_path
        
        if self.proxy:
            launch_kwargs["proxy"] = self.proxy
            xiaohongshu_logger.info(f"Using Proxy: {self.proxy.get('server')}")

        browser = await playwright.chromium.launch(**launch_kwargs)
        # 创建一个浏览器上下文，使用指定的 cookie 文件
        context = await browser.new_context(
            **build_context_options(
                viewport={"width": 1600, "height": 900},
                storage_state=f"{self.account_file}"
            )
        )
        context = await set_init_script(context)

        # 创建一个新的页面
        page = await context.new_page()
        # 访问指定的 URL
        await page.goto("https://creator.xiaohongshu.com/publish/publish?from=homepage&target=video")
        await dismiss_xhs_tour(page)
        xiaohongshu_logger.info(f'[+]正在上传-------{self.title}.mp4')
        # 等待页面跳转到指定的 URL，没进入，则自动等待到超时
        xiaohongshu_logger.info(f'[-] 正在打开主页...')
        # 使用轮询方式替代wait_for_url
        url_match = False
        for _ in range(10):  # 最多尝试10次，每次0.5秒
            current_url = page.url
            if "https://creator.xiaohongshu.com/publish/publish?from=homepage&target=video" in current_url:
                url_match = True
                break
            await asyncio.sleep(0.5)
        
        if not url_match:
            xiaohongshu_logger.warning("[-] 主页URL匹配超时，继续执行")
        # 点击 "上传视频" 按钮
        await page.locator("div[class^='upload-content'] input[class='upload-input']").set_input_files(self.file_path)

        # 等待页面跳转到指定的 URL 2025.01.08修改在原有基础上兼容两种页面
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # 使用更可靠的轮询方式替代wait_for_selector
                upload_success = False
                
                for _ in range(10):  # 最多尝试10次
                    try:
                        # 直接查询元素，不使用wait_for_selector
                        upload_input = await page.query_selector('input.upload-input')
                        if upload_input:
                            # 获取下一个兄弟元素
                            preview_new = await upload_input.query_selector(
                                'xpath=following-sibling::div[contains(@class, "preview-new")]')
                            if preview_new:
                                # 在preview-new元素中查找包含"上传成功"的stage元素
                                stage_elements = await preview_new.query_selector_all('div.stage')
                                for stage in stage_elements:
                                    text_content = await page.evaluate('(element) => element.textContent', stage)
                                    if '上传成功' in text_content:
                                        upload_success = True
                                        break
                                if upload_success:
                                    xiaohongshu_logger.info("[+] 检测到上传成功标识!")
                                    break  # 成功检测到上传成功后跳出循环
                                else:
                                    print("  [-] 未找到上传成功标识，继续等待...")
                            else:
                                print("  [-] 未找到预览元素，继续等待...")
                        else:
                            print("  [-] 未找到上传输入元素，继续等待...")
                        await asyncio.sleep(1)
                    except Exception as inner_e:
                        print(f"  [-] 轮询过程出错: {str(inner_e)}，继续尝试...")
                        await asyncio.sleep(0.5)
                
                if upload_success:
                    break
                else:
                    print("  [-] 超时未检测到上传成功标识，继续等待...")
                    retry_count += 1
                    await asyncio.sleep(2)
                    
            except Exception as e:
                error_msg = str(e)
                print(f"  [-] 检测过程出错: {error_msg}，重新尝试...")
                
                # 检查是否是连接关闭错误
                if "Connection closed" in error_msg or "read ECONNRESET" in error_msg:
                    print("  [-] 浏览器连接已关闭，准备重新初始化...")
                    retry_count += 1
                    await asyncio.sleep(1)
                else:
                    await asyncio.sleep(0.5)  # 等待0.5秒后重新尝试

        # 填充标题和话题
        # 检查是否存在包含输入框的元素
        # 这里为了避免页面变化，故使用相对位置定位：作品标题父级右侧第一个元素的input子元素
        await asyncio.sleep(1)
        xiaohongshu_logger.info(f'  [-] 正在填充标题和话题...')

        # 尝试多种标题输入框定位方式
        title_filled = False
        title_selectors = [
            'div.plugin.title-container input.d-text',
            'input[placeholder*="填写标题"]',
            'input[placeholder*="请输入标题"]',
            '.title-container input',
            '.c-input_inner',
        ]

        for selector in title_selectors:
            try:
                title_container = page.locator(selector).first
                if await title_container.count() > 0 and await title_container.is_visible():
                    await title_container.fill(self.title[:30])
                    xiaohongshu_logger.info(f'  [+] 使用选择器 {selector} 成功填充标题')
                    title_filled = True
                    break
            except Exception as e:
                xiaohongshu_logger.debug(f'  [-] 选择器 {selector} 失败: {str(e)}')
                continue

        if not title_filled:
            xiaohongshu_logger.warning('  [-] 所有标题选择器失败，尝试备用方案')
            try:
                titlecontainer = page.locator(".notranslate").first
                await titlecontainer.click()
                await page.keyboard.press("Control+KeyA")
                await page.keyboard.press("Delete")
                await page.keyboard.type(self.title[:30])
                await page.keyboard.press("Enter")
                xiaohongshu_logger.info('  [+] 使用备用方案成功填充标题')
            except Exception as e:
                xiaohongshu_logger.error(f'  [-] 标题填充完全失败: {str(e)}')

        # 填写内容和标签 - 尝试多种定位方式
        await asyncio.sleep(1)
        content_filled = False
        content_selectors = [
            ".ql-editor",
            "div[contenteditable='true']",
            ".publish-editor .ql-editor",
            "div.ql-container .ql-editor",
            "[data-placeholder]",
        ]

        for selector in content_selectors:
            try:
                content_box = page.locator(selector).first
                if await content_box.count() > 0 and await content_box.is_visible():
                    # 点击激活编辑器
                    await content_box.click()
                    await asyncio.sleep(0.3)

                    # 填写标签 - 小红书标签流程：
                    # 1. 输入 #标签 → 触发 API 获取推荐
                    # 2. 等待下拉列表出现 (.suggestion)
                    # 3. 按 Enter 选中 → 转换为 <a class="tiptap-topic">
                    for index, tag in enumerate(self.tags, start=1):
                        xiaohongshu_logger.info(f'  [-] 正在添加标签 {index}/{len(self.tags)}: #{tag}')

                        # 输入标签
                        await page.type(selector, "#" + tag)
                        await asyncio.sleep(0.3)

                        # 等待下拉列表出现（小红书会请求 API 获取推荐标签）
                        try:
                            # 使用轮询方式替代wait_for_selector
                            suggestion_found = False
                            for _ in range(5):  # 最多尝试5次
                                suggestion_elements = await page.query_selector_all('.suggestion, [class*="suggestion"], [data-decoration-id]')
                                if suggestion_elements:
                                    # 检查是否有可见的建议元素
                                    for element in suggestion_elements:
                                        if await element.is_visible():
                                            suggestion_found = True
                                            break
                                    if suggestion_found:
                                        break
                                await asyncio.sleep(0.4)
                            
                            if suggestion_found:
                                await asyncio.sleep(0.2)
                                xiaohongshu_logger.debug(f'  [+] 标签 #{tag} 的推荐列表已出现')
                            else:
                                raise Exception("推荐列表未出现")
                        except Exception as e:
                            xiaohongshu_logger.warning(f'  [!] 标签 #{tag} 未找到推荐列表，直接确认: {str(e)[:50]}')

                        # 按 Enter 选择第一个推荐项（将 <span class="suggestion"> 转换为 <a class="tiptap-topic">）
                        await page.press(selector, "Enter")
                        await asyncio.sleep(0.3)

                        # 验证标签是否成功转换为链接
                        try:
                            topic_link = await page.locator('a.tiptap-topic').count()
                            if topic_link >= index:
                                xiaohongshu_logger.success(f'  [✓] 标签 #{tag} 已成功转换为话题链接')
                            else:
                                xiaohongshu_logger.warning(f'  [!] 标签 #{tag} 可能未正确转换')
                        except Exception:
                            pass

                    xiaohongshu_logger.info(f'  [+] 使用选择器 {selector} 成功添加{len(self.tags)}个话题')
                    content_filled = True
                    break
            except Exception as e:
                xiaohongshu_logger.debug(f'  [-] 内容选择器 {selector} 失败: {str(e)}')
                continue

        if not content_filled:
            xiaohongshu_logger.error('  [-] 所有内容选择器失败，标签未能添加')

        # while True:
        #     # 判断重新上传按钮是否存在，如果不存在，代表视频正在上传，则等待
        #     try:
        #         #  新版：定位重新上传
        #         number = await page.locator('[class^="long-card"] div:has-text("重新上传")').count()
        #         if number > 0:
        #             xiaohongshu_logger.success("  [-]视频上传完毕")
        #             break
        #         else:
        #             xiaohongshu_logger.info("  [-] 正在上传视频中...")
        #             await asyncio.sleep(2)

        #             if await page.locator('div.progress-div > div:has-text("上传失败")').count():
        #                 xiaohongshu_logger.error("  [-] 发现上传出错了... 准备重试")
        #                 await self.handle_upload_error(page)
        #     except:
        #         xiaohongshu_logger.info("  [-] 正在上传视频中...")
        #         await asyncio.sleep(2)
        
        # 上传视频封面
        await self.set_thumbnail(page, self.thumbnail_path)

        # 更换可见元素
        # await self.set_location(page, "青岛市")

        # # 頭條/西瓜
        # third_part_element = '[class^="info"] > [class^="first-part"] div div.semi-switch'
        # # 定位是否有第三方平台
        # if await page.locator(third_part_element).count():
        #     # 检测是否是已选中状态
        #     if 'semi-switch-checked' not in await page.eval_on_selector(third_part_element, 'div => div.className'):
        #         await page.locator(third_part_element).locator('input.semi-switch-native-control').click()

        if self.publish_date != 0:
            await self.set_schedule_time_xiaohongshu(page, self.publish_date)

        # 判断视频是否发布成功
        xiaohongshu_logger.info("  [-] 准备点击发布按钮...")
        await asyncio.sleep(1)  # 减少延迟：2秒 → 1秒

        # 尝试多种发布按钮定位方式
        publish_clicked = False
        if self.publish_date != 0:
            publish_button_selectors = [
                'button:has-text("定时发布")',
                'button.publish-btn:has-text("定时发布")',
                '.publish-footer button:has-text("定时发布")',
                'button[type="button"]:has-text("定时发布")',
            ]
        else:
            publish_button_selectors = [
                'button:has-text("发布")',
                'button.publish-btn:has-text("发布")',
                '.publish-footer button:has-text("发布")',
                'button[type="button"]:has-text("发布")',
                '.footer-btn button:has-text("发布")',
            ]

        for selector in publish_button_selectors:
            try:
                publish_btn = page.locator(selector).first
                if await publish_btn.count() > 0 and await publish_btn.is_visible():
                    # 检查按钮是否可点击（未被禁用）
                    is_disabled = await publish_btn.is_disabled()
                    if not is_disabled:
                        xiaohongshu_logger.info(f'  [+] 找到发布按钮，选择器: {selector}')
                        await publish_btn.click()
                        publish_clicked = True
                        xiaohongshu_logger.info('  [+] 已点击发布按钮')
                        break
                    else:
                        xiaohongshu_logger.debug(f'  [-] 按钮存在但被禁用: {selector}')
            except Exception as e:
                xiaohongshu_logger.debug(f'  [-] 发布按钮选择器 {selector} 失败: {str(e)}')
                continue

        if not publish_clicked:
            xiaohongshu_logger.error('  [-] 所有发布按钮选择器失败，尝试截图保存当前页面状态')
            await page.screenshot(path='logs/xhs_publish_fail.png', full_page=True)

        # 等待发布成功跳转
        max_wait_time = 60  # 最大等待时间60秒
        wait_start = datetime.now()
        
        while (datetime.now() - wait_start).total_seconds() < max_wait_time:
            try:
                # 使用轮询方式替代wait_for_url
                current_url = page.url
                if "https://creator.xiaohongshu.com/publish/success" in current_url:
                    xiaohongshu_logger.success("  [-]视频发布成功")
                    break
                
                # 检查是否有发布失败的提示
                error_elements = await page.query_selector_all('div:has-text("发布失败"), div:has-text("发布出错"), div:has-text("上传失败")')
                for element in error_elements:
                    if await element.is_visible():
                        xiaohongshu_logger.error("  [-]视频发布失败")
                        break
                
                xiaohongshu_logger.info("  [-] 等待发布完成中...")
                await asyncio.sleep(0.5)
            except Exception as e:
                error_msg = str(e)
                print(f"  [-] 等待发布完成时出错: {error_msg}")
                
                # 检查是否是连接关闭错误
                if "Connection closed" in error_msg or "read ECONNRESET" in error_msg:
                    print("  [-] 浏览器连接已关闭，但继续等待发布结果...")
                
                xiaohongshu_logger.info("  [-] 等待发布完成中...")
                await asyncio.sleep(0.5)

        await context.storage_state(path=self.account_file)  # 保存cookie
        xiaohongshu_logger.success('  [-]cookie更新完毕！')
        await asyncio.sleep(0.5)  # 减少延迟：2秒 → 0.5秒
        # 关闭浏览器上下文和浏览器实例
        await context.close()
        await browser.close()

    async def set_thumbnail(self, page: Page, thumbnail_path: str):
        if thumbnail_path:
            try:
                await page.click('text="选择封面"')
                
                # 使用轮询方式替代wait_for_selector
                for _ in range(5):
                    modal = await page.query_selector("div.semi-modal-content:visible")
                    if modal:
                        break
                    await asyncio.sleep(0.5)
                
                await page.click('text="设置竖封面"')
                await page.wait_for_timeout(1000)  # 减少延迟：2秒 → 1秒
                
                # 定位到上传区域并点击
                upload_input = await page.locator("div[class^='semi-upload upload'] >> input.semi-upload-hidden-input")
                if await upload_input.count() > 0:
                    await upload_input.set_input_files(thumbnail_path)
                    await page.wait_for_timeout(1000)  # 减少延迟：2秒 → 1秒
                    
                    # 等待完成按钮出现
                    for _ in range(5):
                        finish_btn = await page.locator("div[class^='extractFooter'] button:visible:has-text('完成')").first
                        if await finish_btn.count() > 0 and await finish_btn.is_visible():
                            await finish_btn.click()
                            break
                        await asyncio.sleep(0.5)
            except Exception as e:
                xiaohongshu_logger.warning(f"设置封面失败: {str(e)}")
                # 继续执行，不影响发布流程
            # finish_confirm_element = page.locator("div[class^='confirmBtn'] >> div:has-text('完成')")
            # if await finish_confirm_element.count():
            #     await finish_confirm_element.click()
            # await page.locator("div[class^='footer'] button:has-text('完成')").click()

    async def set_location(self, page: Page, location: str = "青岛市"):
        print(f"开始设置位置: {location}")
        
        try:
            # 点击地点输入框
            print("等待地点输入框加载...")
            # 使用轮询方式替代wait_for_selector
            loc_ele = None
            for _ in range(5):
                loc_ele = await page.query_selector('div.d-text.d-select-placeholder.d-text-ellipsis.d-text-nowrap')
                if loc_ele:
                    break
                await asyncio.sleep(0.5)
            
            if not loc_ele:
                print("未找到地点输入框，跳过位置设置")
                return False
            
            print(f"已定位到地点输入框: {loc_ele}")
            await loc_ele.click()
            print("点击地点输入框完成")
            
            # 输入位置名称
            print(f"等待1秒后输入位置名称: {location}")
            await page.wait_for_timeout(1000)
            await page.keyboard.type(location)
            print(f"位置名称输入完成: {location}")

            # 等待下拉列表加载
            print("等待下拉列表加载...")
            await page.wait_for_timeout(1000)  # 减少延迟：3秒 → 1秒
            
            # 尝试更灵活的XPath选择器
            print("尝试使用更灵活的XPath选择器...")
            flexible_xpath = (
                f'//div[contains(@class, "d-popover") and contains(@class, "d-dropdown")]'
                f'//div[contains(@class, "d-options-wrapper")]'
                f'//div[contains(@class, "d-grid") and contains(@class, "d-options")]'
                f'//div[contains(@class, "name") and contains(text(), "{location}")]'
            )
            await page.wait_for_timeout(500)  # 减少延迟：3秒 → 0.5秒
            
            # 尝试定位元素
            print(f"尝试定位包含'{location}'的选项...")
            location_option = None
            
            # 先尝试使用更灵活的选择器
            for _ in range(5):
                try:
                    location_option = await page.query_selector(flexible_xpath)
                    if location_option:
                        break
                    await asyncio.sleep(0.5)
                except Exception as inner_e:
                    print(f"  尝试定位失败: {inner_e}")
                    await asyncio.sleep(0.5)
            
            if not location_option:
                # 如果灵活选择器失败，再尝试其他选择器
                print("灵活选择器未找到元素，尝试其他选择器...")
                alternative_selectors = [
                    f'//div[contains(text(), "{location}")]',
                    f'//div[contains(@class, "option") and contains(text(), "{location}")]',
                    f'//div[contains(@class, "name") and contains(text(), "{location}")]'
                ]
                
                for selector in alternative_selectors:
                    for _ in range(3):
                        try:
                            location_option = await page.query_selector(selector)
                            if location_option:
                                break
                            await asyncio.sleep(0.3)
                        except:
                            pass
                    if location_option:
                        break
            
            if location_option:
                print(f"使用灵活选择器定位成功: {location_option}")
                
                # 滚动到元素并点击
                print("滚动到目标选项...")
                try:
                    await location_option.scroll_into_view_if_needed()
                    print("元素已滚动到视图内")
                    
                    # 增加元素可见性检查
                    is_visible = await location_option.is_visible()
                    print(f"目标选项是否可见: {is_visible}")
                    
                    # 点击元素
                    print("准备点击目标选项...")
                    await location_option.click()
                    print(f"成功选择位置: {location}")
                    return True
                except Exception as e:
                    print(f"点击位置失败: {e}")
                    return False
            else:
                print("未找到位置选项，跳过位置设置")
                return False
                
        except Exception as e:
            print(f"设置位置失败: {e}")
            
            # 打印更多调试信息
            try:
                print("尝试获取下拉列表中的所有选项...")
                all_options = await page.query_selector_all(
                    '//div[contains(@class, "d-popover") and contains(@class, "d-dropdown")]'
                    '//div[contains(@class, "d-options-wrapper")]'
                    '//div[contains(@class, "d-grid") and contains(@class, "d-options")]'
                    '/div'
                )
                if all_options:
                    print(f"找到 {len(all_options)} 个选项")
                    
                    # 打印前3个选项的文本内容
                    for i, option in enumerate(all_options[:3]):
                        try:
                            option_text = await option.inner_text()
                            print(f"选项 {i+1}: {option_text.strip()[:50]}...")
                        except:
                            pass
                else:
                    print("未找到任何选项")
                    
            except Exception as inner_e:
                print(f"获取选项列表失败: {inner_e}")
                
            # 截图保存（取消注释使用）
            # await page.screenshot(path=f"location_error_{location}.png")
            return False

    async def main(self):
        async with async_playwright() as playwright:
            await self.upload(playwright)
