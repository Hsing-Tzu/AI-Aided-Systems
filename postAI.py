import asyncio
from playwright.async_api import async_playwright

# 存儲登入狀態的檔案
STORAGE_STATE_PATH = "medium_login_state.json"
MEDIUM_POST_PATH = "./temp/medium_post.txt"  # medium_post 文件路徑

async def save_login_state():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,  # 顯示瀏覽器讓你手動登入
            executable_path="C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",  # Edge 安裝路徑
            args=[
                "--no-sandbox",
                "--disable-gpu",
                "--disable-software-rasterizer",
                "--disable-extensions",
                "--disable-features=IsolateOrigins,site-per-process",
                "--disable-web-security",
                "--allow-running-insecure-content",
                "--disable-blink-features=AutomationControlled"
            ]
        )
        context = await browser.new_context()

        # 開啟 Medium 網站並等待手動登入
        page = await context.new_page()
        await page.goto("https://medium.com/")

        print("🚀 請手動登入 Medium，完成後請按 ENTER...")
        input()  # 等待手動登入
        await context.storage_state(path=STORAGE_STATE_PATH)  # 存儲登入狀態
        print(f"✅ 登入狀態已保存至 {STORAGE_STATE_PATH}")

        await browser.close()

async def post_on_medium():
    # 檢查 medium_post.txt 是否存在
    if not os.path.exists(MEDIUM_POST_PATH):
        print(f"❌ 找不到 {MEDIUM_POST_PATH} 文件，請先生成文章內容！")
        return

    # 讀取 medium_post.txt 的內容
    with open(MEDIUM_POST_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()
        if len(lines) < 2:
            print("❌ medium_post.txt 文件格式錯誤，請確保包含標題和內容！")
            return
        title = lines[0].strip("# ").strip()  # 第一行為標題，去掉 "#"
        content = "".join(lines[1:]).strip()  # 其餘行為內容

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            executable_path="C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
            args=["--no-sandbox", "--disable-gpu", "--disable-blink-features=AutomationControlled"]
        )
        context = await browser.new_context(storage_state=STORAGE_STATE_PATH)
        page = await context.new_page()

        # 打開 Medium 新文章頁面
        await page.goto("https://medium.com/new-story")

        # 等待標題輸入框加載完成
        await page.wait_for_selector("h3.graf--title", timeout=60000)
        await page.wait_for_timeout(5000)
        # 填寫文章標題
        await page.locator("h3.graf--title span.defaultValue").click()
        await page.keyboard.type(title, delay=10)
        await page.wait_for_timeout(5000)
        # 填寫文章內容
        await page.locator("p.graf--p span.defaultValue").click()
        await page.keyboard.type(content, delay=10)

        # 等待 5 秒，確保內容輸入完成
        await page.wait_for_timeout(5000)

        # 重新整理確保按鈕狀態
        await page.reload()
        await page.wait_for_timeout(5000)

        # 等待發佈按鈕可用
        publish_button = await page.wait_for_selector("button[data-action='show-prepublish']", timeout=100000)

        # 檢查按鈕是否啟用
        is_enabled = await page.evaluate("(btn) => !btn.disabled", publish_button)
        
        if not is_enabled:
            print("⚠️ Publish 按鈕仍不可用，嘗試手動點擊")
            await publish_button.click()
        else:
            print("✅ Publish 按鈕可用，進行發佈")
            await publish_button.click()

        # 確保 Publish now 按鈕可見
        await page.wait_for_timeout(5000)  # 等待 5 秒，確保按鈕載入
        publish_now_button = page.locator("button:has-text('Publish now')")

        if await publish_now_button.is_visible():
            await publish_now_button.click()
            print("✅ 成功點擊 'Publish now' 按鈕，等待發佈...")
            await page.wait_for_timeout(10000)  # 等待 10 秒，確保 Medium 完成發佈
            print("✅ 文章應該已成功發佈！")
        else:
            print("❌ 找不到 'Publish now' 按鈕，文章可能仍然是草稿！")


if __name__ == "__main__":
    import os
    if not os.path.exists(STORAGE_STATE_PATH):
        print("⚠️ 找不到登入狀態，請先登入 Medium！")
        asyncio.run(save_login_state())

    asyncio.run(post_on_medium())