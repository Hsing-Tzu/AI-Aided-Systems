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

      // 建立 WebSocket 連線
      const socket = new WebSocket("ws://localhost:8000/ws");

      socket.onopen = () => {
        console.log("WebSocket 連線成功");
        setConnected(true);
        socket.send(JSON.stringify({ message: "開始處理 CSV 文件" }));
      };

      socket.onmessage = async (event) => {
        try {
          const newMessage = JSON.parse(event.data);

          if (newMessage.content) {
            const evaluationResponse = await fetch("http://localhost:8000/evaluate_review", {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
              },
              body: JSON.stringify({ generated_review: newMessage.content }),
            });

            const evaluationResult = await evaluationResponse.json();
            if (evaluationResult.error) {
              console.error("評分失敗:", evaluationResult.error);
              alert("評分失敗：" + evaluationResult.error);
              return;
            }

            newMessage.evaluation = evaluationResult.evaluation;
          }

          setMessages((prev) => [...prev, newMessage]);
        } catch (error) {
          console.error("解析 WebSocket 訊息時發生錯誤", error);
        }
      };

      socket.onerror = (error) => {
        console.error("WebSocket 發生錯誤", error);
        alert("WebSocket 連線錯誤");
      };

      socket.onclose = () => {
        console.log("WebSocket 連線已關閉");
        setConnected(false);
      };

      setWs(socket);
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
          response: result.content,
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

  const handlePostToMedium = async () => {
    if (messages.length === 0) {
      alert("沒有可發佈的內容");
      return;
    }

    const latestMessage = messages[messages.length - 1];
    if (!latestMessage.title || !latestMessage.response) {
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
          content: latestMessage.response,
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

      <div
        style={{
          maxHeight: "400px",
          overflowY: "scroll",
          border: "1px solid #ddd",
          padding: "10px",
          marginTop: "20px",
        }}
      >
        {messages.map((msg, index) => (
          <div key={index} style={{ marginBottom: "10px" }}>
            {msg.user_message && (
              <p>
                <strong>使用者輸入：</strong> {msg.user_message}
              </p>
            )}
            {msg.title && (
              <p>
                <strong>生成的標題：</strong> {msg.title}
              </p>
            )}
            {msg.response && (
              <p>
                <strong>生成的內容：</strong> {msg.response}
              </p>
            )}
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
            {msg.search_results && Array.isArray(msg.search_results) && (
              <div>
                <strong>延伸閱讀：</strong>
                <ul>
                  {msg.search_results.map((result, idx) => (
                    <li key={idx}>
                      <a href={result.link} target="_blank" rel="noopener noreferrer">
                        {result.title}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            )}
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