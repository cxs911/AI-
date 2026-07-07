"""Boss直聘 Selenium自动化客户端 - 岗位检索与投递
风控规则:
- 可视化Chrome，禁止无头模式
- 随机鼠标轨迹
- 页面随机停留3-12s
- 每日投递上限25个
- 投递间隔15-40s随机
- 仅工作日9:00-18:00运行
- 人机验证自动暂停
"""
import time
import random
import json
import logging
from datetime import datetime, date
from typing import Optional, List, Dict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, WebDriverException
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from app.config import settings

logger = logging.getLogger(__name__)


class BossSeleniumClient:
    """Boss直聘Selenium操作客户端"""

    BASE_URL = "https://www.zhipin.com"
    LOGIN_URL = "https://www.zhipin.com/web/chat/"
    SEARCH_URL = "https://www.zhipin.com/web/geek/job"

    def __init__(self):
        self.driver: Optional[webdriver.Chrome] = None
        self.is_paused = False
        self.today_deliveries = 0
        self.current_date = date.today().isoformat()

    def _random_sleep(self, min_s: float = 3, max_s: float = 12):
        """随机等待，模拟人类操作"""
        time.sleep(random.uniform(min_s, max_s))

    def _random_mouse_move(self, element=None):
        """随机鼠标移动轨迹"""
        if not self.driver:
            return
        action = ActionChains(self.driver)
        if element:
            # 移动到目标元素附近随机偏移
            x_offset = random.randint(-10, 10)
            y_offset = random.randint(-10, 10)
            action.move_to_element_with_offset(element, x_offset, y_offset)
        else:
            # 随机移动到页面某处
            width = self.driver.execute_script("return window.innerWidth")
            height = self.driver.execute_script("return window.innerHeight")
            target_x = random.randint(100, width - 100)
            target_y = random.randint(100, height - 100)
            action.move_by_offset(target_x, target_y)
        action.perform()
        time.sleep(random.uniform(0.5, 1.5))

    def _check_work_time(self) -> bool:
        """检查是否在允许的工作时间内"""
        now = datetime.now()
        # 检查工作日
        work_days = [int(d.strip()) for d in settings.BOSS_WORK_DAYS.split(",")]
        if now.isoweekday() not in work_days:
            logger.warning(f"今日不是工作日(设置的工作日: {work_days})")
            return False
        # 检查工作时间
        start_h, start_m = settings.BOSS_WORK_START.split(":")
        end_h, end_m = settings.BOSS_WORK_END.split(":")
        work_start = now.replace(hour=int(start_h), minute=int(start_m), second=0)
        work_end = now.replace(hour=int(end_h), minute=int(end_m), second=0)
        if not (work_start <= now <= work_end):
            logger.warning(f"当前不在工作时间({settings.BOSS_WORK_START}-{settings.BOSS_WORK_END})")
            return False
        return True

    def _check_delivery_limit(self) -> bool:
        """检查每日投递上限"""
        # 如果日期变了，重置计数
        today = date.today().isoformat()
        if self.current_date != today:
            self.today_deliveries = 0
            self.current_date = today
        if self.today_deliveries >= settings.BOSS_DELIVERY_LIMIT:
            logger.warning(f"已达每日投递上限({settings.BOSS_DELIVERY_LIMIT}个)")
            return False
        return True

    def start_driver(self):
        """启动Chrome浏览器（可视化模式，禁止无头）"""
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--window-size=1366,768")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)

        # 加载用户数据目录以保持登录状态
        chrome_options.add_argument("--user-data-dir=./data/chrome_profile")

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

        # 隐藏webdriver特征
        self.driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
                """
            }
        )

        self.driver.get(self.LOGIN_URL)
        self._random_sleep(3, 6)
        logger.info("Chrome浏览器已启动，请扫码登录Boss直聘")

    def check_login(self) -> bool:
        """检查是否已登录"""
        try:
            wait = WebDriverWait(self.driver, 10)
            wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='chat']"))
            )
            return True
        except TimeoutException:
            return False

    def wait_for_login(self, timeout: int = 120):
        """等待用户扫码登录"""
        logger.info("等待扫码登录...")
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".chat-container, [class*='message']"))
            )
            logger.info("登录成功")
            self._random_sleep()
            return True
        except TimeoutException:
            logger.error("登录超时")
            return False

    def search_jobs(self, keyword: str, city: str = "北京",
                    page: int = 1, salary_min: int = 0, salary_max: int = 100) -> List[Dict]:
        """搜索岗位并提取信息"""
        if not self.driver:
            raise Exception("浏览器未启动")

        search_url = f"{self.SEARCH_URL}?query={keyword}&city={city}&page={page}"
        if salary_min or salary_max:
            search_url += f"&salary={salary_min}_{salary_max}"

        self.driver.get(search_url)
        self._random_sleep(4, 8)
        self._random_mouse_move()

        jobs = []
        try:
            # 等待职位列表加载
            wait = WebDriverWait(self.driver, 15)
            job_cards = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".job-card-wrapper, [class*='job-list'] li"))
            )

            for card in job_cards[:50]:  # 每页最多取50个
                try:
                    self._random_mouse_move(card)
                    job_info = self._extract_job_info(card)
                    if job_info:
                        jobs.append(job_info)
                except Exception as e:
                    logger.warning(f"提取岗位信息失败: {e}")
                    continue

            logger.info(f"搜索到 {len(jobs)} 个岗位")
        except TimeoutException:
            logger.warning("岗位列表加载超时")

        return jobs

    def _extract_job_info(self, card) -> Optional[Dict]:
        """从卡片元素提取岗位信息"""
        try:
            title_el = card.find_element(By.CSS_SELECTOR, "[class*='job-name'], .job-title")
            title = title_el.text.strip()

            company_el = card.find_element(By.CSS_SELECTOR, "[class*='company-name'], .company-name")
            company = company_el.text.strip()

            salary_el = card.find_element(By.CSS_SELECTOR, "[class*='salary'], .job-salary")
            salary = salary_el.text.strip()

            # 解析薪资
            salary_min, salary_max = 0, 0
            if "K" in salary or "k" in salary:
                parts = salary.replace("K", "").replace("k", "").split("-")
                if len(parts) == 2:
                    salary_min = int(parts[0].strip())
                    salary_max = int(parts[1].strip())

            # 提取标签
            tags = []
            tag_els = card.find_elements(By.CSS_SELECTOR, "[class*='tag'], .job-tag")
            for tag_el in tag_els:
                tags.append(tag_el.text.strip())

            # 获取详情链接
            link_el = card.find_element(By.CSS_SELECTOR, "a")
            url = link_el.get_attribute("href") or ""

            # 获取Boss信息
            boss_name = ""
            boss_title = ""
            try:
                boss_el = card.find_element(By.CSS_SELECTOR, "[class*='boss-name']")
                boss_name = boss_el.text.strip()
            except NoSuchElementException:
                pass

            # 获取job_id
            import re
            job_id = ""
            if url:
                match = re.search(r'job_detail/(\w+)\.html', url)
                if match:
                    job_id = match.group(1)
                else:
                    match = re.search(r'jobid=(\w+)', url)
                    if match:
                        job_id = match.group(1)

            return {
                "job_id": job_id,
                "title": title,
                "company": company,
                "salary": salary,
                "salary_min": salary_min,
                "salary_max": salary_max,
                "tags": tags,
                "url": url,
                "boss_name": boss_name,
                "boss_title": boss_title,
            }
        except Exception as e:
            logger.error(f"解析岗位卡片失败: {e}")
            return None

    def get_job_detail(self, url: str) -> Optional[str]:
        """获取岗位详情JD文本"""
        if not self.driver:
            return None
        try:
            self.driver.get(url)
            self._random_sleep(4, 8)
            self._random_mouse_move()
            # 获取JD描述
            jd_el = self.driver.find_element(
                By.CSS_SELECTOR, "[class*='job-detail'], [class*='job-sec-text']"
            )
            return jd_el.text.strip()
        except Exception as e:
            logger.error(f"获取JD详情失败: {e}")
            return None

    def deliver_job(self, job_url: str, greeting: str = "") -> bool:
        """投递单个岗位"""
        if not self._check_work_time():
            logger.warning("当前不在工作时间，跳过投递")
            return False

        if not self._check_delivery_limit():
            logger.warning("已达每日投递上限")
            return False

        if not self.driver:
            raise Exception("浏览器未启动")

        try:
            # 检查是否是人机验证
            if self._is_captcha_shown():
                logger.error("检测到人机验证，自动暂停投递")
                self.is_paused = True
                return False

            self.driver.get(job_url)
            self._random_sleep(4, 8)
            self._random_mouse_move()

            # 找投递按钮
            try:
                deliver_btn = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, "[class*='btn-deliver'], .btn-start-chat, [class*='deliver']")
                    )
                )
                self._random_mouse_move(deliver_btn)
                self._random_sleep(1, 3)
                deliver_btn.click()

                # 如果有招呼语，填入
                if greeting:
                    self._random_sleep(2, 4)
                    try:
                        input_box = self.driver.find_element(
                            By.CSS_SELECTOR, "[class*='input'], [class*='chat-input'], textarea"
                        )
                        input_box.clear()
                        # 模拟人类打字
                        for char in greeting:
                            input_box.send_keys(char)
                            time.sleep(random.uniform(0.02, 0.08))
                        self._random_sleep(1, 2)
                    except NoSuchElementException:
                        pass

                # 点击发送/确认
                try:
                    send_btn = self.driver.find_element(
                        By.CSS_SELECTOR, "[class*='submit'], [class*='send'], .btn-primary"
                    )
                    self._random_mouse_move(send_btn)
                    send_btn.click()
                except NoSuchElementException:
                    pass

                self.today_deliveries += 1
                logger.info(f"投递成功! 今日已投递: {self.today_deliveries}")

                # 随机间隔
                self._random_sleep(settings.BOSS_MIN_INTERVAL, settings.BOSS_MAX_INTERVAL)
                return True

            except TimeoutException:
                logger.warning("未找到投递按钮")
                return False

        except Exception as e:
            logger.error(f"投递失败: {e}")
            # 检查是否触发验证
            if self._is_captcha_shown():
                self.is_paused = True
            return False

    def _is_captcha_shown(self) -> bool:
        """检测是否出现人机验证"""
        try:
            captcha_selectors = [
                "iframe[src*='captcha']",
                "[class*='captcha']",
                "[class*='verify']",
                "[id*='captcha']",
                "[class*='slider']"
            ]
            for selector in captcha_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    return True
            return False
        except Exception:
            return False

    def quit(self):
        """关闭浏览器"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None
