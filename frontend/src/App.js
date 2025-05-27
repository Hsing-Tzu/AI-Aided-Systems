import { useState, useEffect } from "react";
import './App.css';

const WebSocketChat = () => {
  const [messages, setMessages] = useState([]);
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [ws, setWs] = useState(null);
  const [connected, setConnected] = useState(false);
  const [inputMessage, setInputMessage] = useState("");
  const [shortReview, setShortReview] = useState("");
  const [mode, setMode] = useState("upload");
  const [generating, setGenerating] = useState(false); // 控制再生成按鈕 loading

  useEffect(() => {
    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, [ws]);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) {
      alert("請選擇 CSV 檔案");
      return;
    }

    setLoading(true);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      });

      const result = await response.json();
      if (result.error) {
        console.error("上傳失敗:", result.error);
        alert("檔案上傳失敗：" + result.error);
        return;
      }

      console.log("上傳成功:", result.file_path);

      // 顯示統整後的完整標題和文章
      if (result.combined_title && result.combined_content) {
        setMessages((prev) => [
          ...prev,
          {
            title: result.combined_title,
            content: result.combined_content,
          },
        ]);
      } else {
        console.warn("未收到統整後的內容或標題");
        alert("未收到有效的統整內容或標題，請檢查後端日誌以獲取更多資訊。");
      }
    } catch (error) {
      console.error("上傳失敗", error);
      alert("檔案上傳失敗，請稍後再試");
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = () => {
    if (!inputMessage.trim()) {
      alert("請輸入訊息");
      return;
    }

    if (ws && connected) {
      ws.send(JSON.stringify({ message: inputMessage }));
      setInputMessage("");
    } else {
      alert("WebSocket 尚未連線");
    }
  };

  const handleGenerateReview = async () => {
    if (!shortReview.trim()) {
      alert("請輸入簡短的評價心得");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch("http://localhost:8000/generate_review", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ short_review: shortReview }),
      });

      const result = await response.json();
      if (result.error) {
        console.error("生成失敗:", result.error);
        alert("生成文章失敗：" + result.error);
        return;
      }

      console.log("生成的標題:", result.title);
      console.log("生成的內容:", result.content);

      const evaluationResponse = await fetch("http://localhost:8000/evaluate_review", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ generated_review: result.content }),
      });

      const evaluationResult = await evaluationResponse.json();
      if (evaluationResult.error) {
        console.error("評分失敗:", evaluationResult.error);
        alert("評分失敗：" + evaluationResult.error);
        return;
      }
      setMessages((prev) => [
        ...prev,
        {
          user_message: shortReview,
          title: result.title, // 新增標題
          content: result.content,
          evaluation: evaluationResult.evaluation,
        },
      ]);
      setShortReview("");
    } catch (error) {
      console.error("生成或評分失敗", error);
      alert("生成或評分失敗，請稍後再試");
    } finally {
      setLoading(false);
    }

  };

  const handleRefine = async (article, instruction) => {
    if (!instruction.trim()) {
      alert("請輸入指令");
      return;
    }
    setGenerating(true);
    try {
      const res = await fetch("http://localhost:8000/refine_review", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ article, instruction })
      });
      const data = await res.json();
      if (data.error) throw new Error(data.error);

      // 把新版本 push 進 messages
      setMessages(prev => [...prev, {
        title: data.title,
        content: data.content,
        instruction
      }]);
    } catch (err) {
      alert("再生成失敗：" + err.message);
    } finally {
      setGenerating(false);
    }
  };



  const handlePostToMedium = async () => {
    if (messages.length === 0) {
      alert("沒有可發佈的內容");
      return;
    }

    const latestMessage = messages[messages.length - 1];
    if (!latestMessage.title || !latestMessage.content) { // 修正這裡的鍵名
      alert("最新的訊息沒有標題或內容資訊");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch("http://localhost:8000/post_to_medium", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          title: latestMessage.title,
          content: latestMessage.content, // 修正這裡的鍵名
        }),
      });

      const result = await response.json();
      if (result.error) {
        console.error("發佈失敗:", result.error);
        alert("發佈到 Medium 失敗：" + result.error);
        return;
      }

      alert("成功發佈到 Medium！");
    } catch (error) {
      console.error("發佈失敗", error);
      alert("發佈到 Medium 失敗，請稍後再試");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>旅遊回顧分析</h2>

      <div style={{ marginBottom: "20px" }}>
        <button
          onClick={() => setMode("upload")}
          style={{
            padding: "10px",
            marginRight: "10px",
            backgroundColor: mode === "upload" ? "#007bff" : "#ccc",
            color: "#fff",
          }}
        >
          上傳 CSV
        </button>
        <button
          onClick={() => setMode("generate")}
          style={{
            padding: "10px",
            backgroundColor: mode === "generate" ? "#007bff" : "#ccc",
            color: "#fff",
          }}
        >
          即時生成
        </button>
      </div>

      {mode === "upload" && (
        <div>
          <input type="file" accept=".csv" onChange={handleFileChange} />
          <button onClick={handleUpload} disabled={loading}>
            {loading ? "上傳中..." : "上傳 CSV"}
          </button>
          {connected && (
            <div>
              <p style={{ color: "green" }}>WebSocket 連線中...</p>
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="輸入訊息..."
                style={{ width: "80%", padding: "10px", marginRight: "10px" }}
              />
              <button onClick={handleSendMessage} disabled={!connected}>
                傳送訊息
              </button>
            </div>
          )}
        </div>
      )}

      {mode === "generate" && (
        <div>
          <input
            type="text"
            value={shortReview}
            onChange={(e) => setShortReview(e.target.value)}
            placeholder="輸入簡短的評價心得..."
            style={{ width: "80%", padding: "10px", marginRight: "10px" }}
          />
          <button onClick={handleGenerateReview} disabled={loading}>
            {loading ? "生成中..." : "生成文章"}
          </button>
        </div>
      )}

      {/* 文章列表 + 再調整功能 */}
      <div
        style={{
          overflowY: "scroll",
          border: "1px solid #ddd",
          padding: "10px",
          marginTop: "20px",
          maxHeight: 400,
        }}
      >
        {messages.map((msg, idx) => (
          <div key={idx} style={{ marginBottom: 20 }}>
            {msg.title && <h3><strong>標題：</strong> {msg.title}</h3>}
            {msg.content && (
              <p style={{ whiteSpace: "pre-wrap" }}>
                <strong>內容：</strong> {msg.content}
              </p>
            )}

            {/* --- 評分表（若有） --- */}
            {msg.evaluation && (
              <div>
                <strong>評分結果：</strong>
                <table
                  style={{
                    borderCollapse: "collapse",
                    width: "100%",
                    marginTop: "10px",
                  }}
                >
                  <thead>
                    <tr>
                      <th style={{ border: "1px solid #ddd", padding: "8px" }}>
                        評分標準
                      </th>
                      <th style={{ border: "1px solid #ddd", padding: "8px" }}>
                        分數
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td style={{ border: "1px solid #ddd", padding: "8px" }}>
                        內容完整性
                      </td>
                      <td style={{ border: "1px solid #ddd", padding: "8px" }}>
                        {msg.evaluation.content_completeness}
                      </td>
                    </tr>
                    <tr>
                      <td style={{ border: "1px solid #ddd", padding: "8px" }}>
                        情感表達
                      </td>
                      <td style={{ border: "1px solid #ddd", padding: "8px" }}>
                        {msg.evaluation.emotional_expression}
                      </td>
                    </tr>
                    <tr>
                      <td style={{ border: "1px solid #ddd", padding: "8px" }}>
                        可讀性
                      </td>
                      <td style={{ border: "1px solid #ddd", padding: "8px" }}>
                        {msg.evaluation.readability}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            )}

            {/* --- 再調整區塊 --- */}
            <div style={{ marginTop: 12 }}>
              <input
                type="text"
                value={msg.refineText || ""}          /* 個別訊息自己的指令文字 */
                onChange={(e) => {
                  const t = e.target.value;
                  setMessages((prev) =>
                    prev.map((m, i) =>
                      i === idx ? { ...m, refineText: t } : m
                    )
                  );
                }}
                placeholder="輸入修改指令，如：改成更幽默"
                style={{ width: "70%", padding: 8, marginRight: 8 }}
              />
              <button
                onClick={() =>
                  handleRefine(
                    `${msg.title}\n\n${msg.content}`,
                    msg.refineText || ""
                  )
                }
                disabled={generating}
              >
                {generating ? "再生成中..." : "再生成"}
              </button>
            </div>
          </div>
        ))}
      </div>


      <button
        onClick={handlePostToMedium}
        disabled={loading || messages.length === 0}
        style={{
          marginTop: "20px",
          padding: "10px",
          backgroundColor: "#28a745",
          color: "#fff",
          border: "none",
          cursor: "pointer",
        }}
      >
        {loading ? "發佈中..." : "發佈到 Medium"}
      </button>
    </div>
  );
};

export default WebSocketChat;