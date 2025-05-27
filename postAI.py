import asyncio
from playwright.async_api import async_playwright

# 存儲登入狀態的檔案
STORAGE_STATE_PATH = "medium_login_state.json"
MEDIUM_POST_PATH = "./temp/medium_post.md"  # medium_post 文件路徑

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
        await page.keyboard.type("A", delay=10)  # 先輸入一個字母 A
        await page.keyboard.type(title[0], delay=10)  # 輸入標題的第一個字
        await page.keyboard.press("ArrowLeft")  # 將光標移到字母 A 的右側
        await page.keyboard.press("Backspace")  # 刪除第一個字母 A
        await page.keyboard.press("ArrowRight") 
        for char in title[1:]:  # 輸入標題的其餘部分
            await page.keyboard.type(char, delay=10)

        # 填寫文章內容
        await page.locator("p.graf--p span.defaultValue").click()
        await page.keyboard.type("A", delay=10)  # 先輸入一個字母 A
        await page.keyboard.type(content[0], delay=10)  # 輸入內容的第一個字
        await page.keyboard.press("ArrowLeft")  # 將光標移到字母 A 的右側
        await page.keyboard.press("Backspace")  # 刪除第一個字母 A
        await page.keyboard.press("ArrowRight") 
        for char in content[1:]:  # 輸入內容的其餘部分
            await page.keyboard.type(char, delay=10)
        # 等待 5 秒，確保內容輸入完成
        await page.wait_for_timeout(5000)

        # 重新整理確保按鈕狀態
        await page.reload()
        await page.wait_for_timeout(5000)

        # 等 Publish 按鈕真正可點
        await page.wait_for_selector('button[data-action="show-prepublish"]', timeout=60000)
        btn = await page.query_selector('button[data-action="show-prepublish"]')
        await page.wait_for_function("b => !b.disabled", arg=btn, timeout=60000)
        await btn.click()

        # 點 Publish now
        await page.wait_for_selector("button:has-text('Publish now')", timeout=60000)
        await page.click("button:has-text('Publish now')")
        await page.wait_for_timeout(5000)  
        await page.wait_for_load_state("networkidle")
        print(" Medium post finished")
        


if __name__ == "__main__":
    import os
    if not os.path.exists(STORAGE_STATE_PATH):
        print("⚠️ 找不到登入狀態，請先登入 Medium！")
        asyncio.run(save_login_state())

    asyncio.run(post_on_medium())