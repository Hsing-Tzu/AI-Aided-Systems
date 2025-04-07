import asyncio
import json
import os
import pandas as pd
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import httpx
from bs4 import BeautifulSoup
import io
from google import genai  # 新增 genai 客戶端
from fastapi import HTTPException
from playwright.async_api import async_playwright

STORAGE_STATE_PATH = "medium_login_state.json"

# 設定 Windows asyncio 事件迴圈 (避免 WindowsProactorEventLoopPolicy 錯誤)
if os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# 讀取環境變數
load_dotenv()

# 初始化 FastAPI 應用程式
app = FastAPI()
# 設定 CORS，允許前端訪問 API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 允許 React 端存取
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 設定 Google Gemini API Key
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("請檢查 .env 檔案中的 GEMINI_API_KEY")

# Google Gemini API 客戶端
class GeminiClient:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)

    async def generate_response(self, messages):
        # 使用 genai 客戶端生成內容
        response = self.client.models.generate_content(
            model="gemini-2.0-flash",  # 假設模型名稱為 gemini-2.0-flash
            contents=messages
        )
        return response.text

# 初始化 Gemini 客戶端
gemini_client = GeminiClient(api_key=gemini_api_key)

# 自定義 WebSurferAgent
class WebSurferAgent:
    async def search(self, query):
        """模擬搜尋並回傳結果"""
        url = f"https://www.google.com/search?q={query}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                results = []
                for g in soup.find_all("div", class_="tF2Cxc"):
                    title = g.find("h3").text
                    link = g.find("a")["href"]
                    results.append({"title": title, "link": link})
                return results
            else:
                return {"error": "無法抓取資料"}

# 自定義 AssistantAgent
class AssistantAgent:
    async def generate_review(self, messages):
        """使用 Gemini 模型生成回顧"""
        # 將 messages 轉換為單純的字符串
        if isinstance(messages, list):
            messages = [msg["content"] for msg in messages if "content" in msg]
        elif isinstance(messages, dict) and "content" in messages:
            messages = [messages["content"]]

        return await gemini_client.generate_response(messages)

# 初始化 Agents
web_surfer_agent = WebSurferAgent()
assistant_agent = AssistantAgent()

# 處理 CSV 批次數據
async def process_chunk(chunk, start_idx, total_records, websocket: WebSocket, conversation_history: list):
    """
    處理 CSV 文件的每個批次數據，並通過 WebSocket 發送結果。
    """
    chunk_data = chunk.to_dict(orient="records")
    prompt = (
        f"目前正在處理第 {start_idx} 至 {start_idx + len(chunk) - 1} 筆資料（共 {total_records} 筆）。\n"
        f"以下為該批次旅遊回顧資料:\n{chunk_data}\n\n"
        "請根據以上旅遊回顧，生成完整的旅遊心得，並包括以下要點：\n"
        "  1. 整理並撰寫流暢的旅遊回顧。\n"
        "  2. 使用 WebSurferAgent 搜尋相關景點、美食、文化背景的資訊，並整理成「延伸閱讀」段落。\n"
        "  3. 讓內容自然流暢，確保資訊準確且易於閱讀。\n"
    )

    # 記錄使用者的批次請求到對話歷史
    conversation_history.append({"role": "user", "content": prompt})

    # 使用 AssistantAgent 生成回顧
    review = await assistant_agent.generate_review(conversation_history)

    # 記錄 Assistant 的回覆到對話歷史
    conversation_history.append({"role": "assistant", "content": review})

    # 使用 WebSurferAgent 搜尋延伸閱讀
    search_results = await web_surfer_agent.search("旅遊景點")

    # 構建回傳的訊息
    message_data = {
        "batch_start": start_idx,
        "batch_end": start_idx + len(chunk) - 1,
        "content": review,
        "search_results": search_results,
    }

    # 通過 WebSocket 發送結果
    await websocket.send_text(json.dumps(message_data))
async def process_chunk(chunk, start_idx, total_records, websocket: WebSocket, conversation_history: list):
    """
    處理 CSV 文件的每個批次數據，並通過 WebSocket 發送結果。
    """
    chunk_data = chunk.to_dict(orient="records")
    prompt = (
        f"目前正在處理第 {start_idx + 1} 至 {start_idx + len(chunk)} 筆資料（共 {total_records} 筆）。\n"
        f"以下為該批次旅遊回顧資料:\n{chunk_data}\n\n"
        "請根據以上旅遊回顧，生成完整的旅遊心得，並包括以下要點：\n"
        "  1. 整理並撰寫流暢的旅遊回顧。\n"
        "  2. 使用 WebSurferAgent 搜尋相關景點、美食、文化背景的資訊，並整理成「延伸閱讀」段落。\n"
        "  3. 讓內容自然流暢，確保資訊準確且易於閱讀。\n"
    )

    # 記錄使用者的批次請求到對話歷史
    conversation_history.append({"role": "user", "content": prompt})

    # 使用 AssistantAgent 生成回顧
    review = await assistant_agent.generate_review(conversation_history)

    # 記錄 Assistant 的回覆到對話歷史
    conversation_history.append({"role": "assistant", "content": review})

    # 使用 WebSurferAgent 搜尋延伸閱讀
    search_results = await web_surfer_agent.search("旅遊景點")

    # 構建回傳的訊息
    message_data = {
        "batch_start": start_idx + 1,
        "batch_end": start_idx + len(chunk),
        "content": review,
        "search_results": search_results,
    }

    # 通過 WebSocket 發送結果
    if websocket:
        await websocket.send_text(json.dumps(message_data))

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), websocket: WebSocket = None):
    """
    處理文件上傳，並將文件分塊處理後傳遞給模型。
    """
    try:
        # 讀取文件內容
        contents = await file.read()
        # 將文件內容轉換為 DataFrame
        df = pd.read_csv(io.StringIO(contents.decode("utf-8")))

        # 確保臨時目錄存在
        os.makedirs("./temp", exist_ok=True)

        # 保存文件到臨時目錄
        file_path = f"./temp/{file.filename}"
        df.to_csv(file_path, index=False)

        # 分塊處理數據
        chunk_size = 10  # 每次處理 10 條數據
        total_records = len(df)
        conversation_history = []  # 用於存儲對話歷史記錄

        for start_idx in range(0, total_records, chunk_size):
            chunk = df.iloc[start_idx:start_idx + chunk_size]
            await process_chunk(chunk, start_idx, total_records, websocket, conversation_history)

        return {"filename": file.filename, "file_path": file_path}
    except Exception as e:
        return {"error": f"文件上傳失敗: {str(e)}"}

# WebSocket 端點
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    conversation_history = []  # 用於存儲對話歷史記錄
    try:
        while True:
            data = await websocket.receive_text()
            request = json.loads(data)

            # 如果包含 "message"，則處理使用者的訊息
            if "message" in request:
                user_message = request["message"]
                
                # 記錄使用者訊息到對話歷史
                conversation_history.append({"role": "user", "content": user_message})

                # 將對話歷史傳遞給 AssistantAgent，生成回覆
                response = await assistant_agent.generate_review(conversation_history)

                # 使用 WebSurferAgent 搜尋相關資訊
                search_results = await web_surfer_agent.search("旅遊景點 美食 文化背景")

                # 格式化為 Markdown 格式
                markdown_content = f"# {user_message}\n\n{response}"

                # 整理搜尋結果
                formatted_search_results = [
                    {"title": result["title"], "link": result["link"]}
                    for result in search_results
                ]

                # 回傳訊息給前端
                await websocket.send_text(json.dumps({
                    "user_message": user_message,
                    "response": markdown_content,
                    "search_results": formatted_search_results
                }))
    except WebSocketDisconnect:
        print("WebSocket 連線已中斷")

@app.post("/generate_review")
async def generate_review_endpoint(input_data: dict):
    """
    接收簡短的評價心得，生成完整的文章，並附加相關的延伸閱讀資訊。
    """
    try:
        short_review = input_data.get("short_review", "")
        if not short_review:
            return {"error": "請提供簡短的評價心得"}

        conversation_history = [
            {
                "role": "user",
                "content": (
                    f"以下是簡短的評價心得：\n{short_review}\n\n"
                    "請根據以下要求生成一篇完整的文章，並以 JSON 格式返回：\n"
                    "{\n"
                    '  "title": "生成的標題",\n'
                    '  "content": "生成的完整內文"\n'
                    "}\n"
                    "1. 生成一個吸引人的標題。\n"
                    "2. 生成一篇流暢且詳細的內文，描述相關的旅遊經歷、景點介紹、文化背景或美食推薦。\n"
                    "3. 確保文章內容自然流暢，並具有吸引力。\n"
                    "4. 回傳的內容必須是 JSON，請勿包含其他文字。\n"
                ),
            }
        ]

        gemini_response = await assistant_agent.generate_review(conversation_history)

        # 新增：移除 ```json 標記
        gemini_response = re.sub(r"```json\s*|\s*```", "", gemini_response)

        try:
            generated_data = json.loads(gemini_response)
            title = generated_data.get("title", "未能生成標題")
            content = generated_data.get("content", "未能生成內文")
        except json.JSONDecodeError:
            raise ValueError(f"模型輸出的 JSON 無法解析: {gemini_response}")

        search_query = f"{title} 旅遊景點 美食 文化背景"
        search_results = await web_surfer_agent.search(search_query)

        formatted_search_results = "\n".join(
            [f"- [{result['title']}]({result['link']})" for result in search_results if "title" in result and "link" in result]
        )

        final_content = f"{content}\n\n## 延伸閱讀\n{formatted_search_results if formatted_search_results else '無相關延伸閱讀建議。'}"

        return {
            "title": title,
            "content": final_content
        }

    except Exception as e:
        return {"error": f"生成文章失敗: {str(e)}"}
    
import re

@app.post("/evaluate_review")
async def evaluate_review_endpoint(input_data: dict):
    try:
        generated_review = input_data.get("generated_review", "")
        if not generated_review:
            return {"error": "請提供模型生成的回答"}

        evaluation_prompt = (
            f"以下是一篇模型生成的旅遊心得：\n{generated_review}\n\n"
            "請根據以下標準對文章進行評分（0-10 分）：\n"
            "1. 內容完整性：是否包含景點介紹、交通方式、推薦原因等資訊？\n"
            "2. 情感表達：是否有真實的個人感受？描述是否具感染力？\n"
            "3. 可讀性：文章是否流暢、語法是否正確？\n\n"
            "請僅返回以下格式的 JSON，其他內容請勿包含：\n"
            '{"content_completeness": , "emotional_expression": , "readability": 0}'
        )

        conversation_history = [{"role": "user", "content": evaluation_prompt}]
        evaluation_result = await assistant_agent.generate_review(conversation_history)
        print("模型回應:", evaluation_result)  # 調試用

        # 嘗試提取 JSON
        try:
            evaluation_data = json.loads(evaluation_result)
        except json.JSONDecodeError:
            # 使用正則表達式提取 JSON
            match = re.search(r"\{.*\}", evaluation_result, re.DOTALL)
            if match:
                evaluation_data = json.loads(match.group())
            else:
                return {"error": "評分結果解析失敗，請檢查模型回應格式", "raw_response": evaluation_result}

        return {
            "generated_review": generated_review,
            "evaluation": evaluation_data,
        }
    except Exception as e:
        return {"error": f"評分失敗: {str(e)}"}

import subprocess

@app.post("/post_to_medium")
async def post_to_medium(input_data: dict):
    """
    使用已生成的標題和內容發佈到 Medium。
    """
    try:
        # 從輸入中獲取標題和內容
        title = input_data.get("title", "")
        content = input_data.get("content", "")
        if not title or not content:
            raise HTTPException(status_code=400, detail="請提供標題和內容")

        # 確保臨時目錄存在
        os.makedirs("./temp", exist_ok=True)

        # 更新 medium_post.txt 文件
        medium_post_path = "./temp/medium_post.txt"
        with open(medium_post_path, "w", encoding="utf-8") as f:
            f.write(f"# {title}\n\n{content}")

        # 日誌輸出確認內容
        print(f"使用的標題: {title}")
        print(f"使用的內容: {content}")

        # 執行 postAI.py 腳本
        process = subprocess.run(
            [
                "cmd.exe", "/c", 
                "D:\\AI-Aided-Systems\\AAS-venv\\Scripts\\activate && python postAI.py"
            ],
            cwd="D:\\AI-Aided-Systems",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if process.returncode != 0:
            raise HTTPException(
                status_code=500,
                detail=f"執行 postAI.py 失敗: {process.stderr}"
            )

        return {"message": "文章已成功發佈到 Medium！", "output": process.stdout}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"發佈文章失敗: {str(e)}")