import { useState, useEffect } from "react";
import Groq from "groq-sdk";

const client = new Groq({
  apiKey: "",
  dangerouslyAllowBrowser: true,
});

// Kiểm tra xem tin nhắn có phải là của bot không
function isBotMessage(chatMessage) {
  return chatMessage.role === "assistant";
}

function App() {
  const [message, setMessage] = useState("");
  const [chatHistory, setChatHistory] = useState(() => {
    const savedHistory = localStorage.getItem("chatHistory");
    return savedHistory ? JSON.parse(savedHistory) : [];
  });

  // Gọi hàm này khi người dùng bấm enter, gửi tin nhắn
  const submitForm = async (e) => {
    e.preventDefault();

    // Clear message ban đầu
    setMessage("");

    // Thêm tin nhắn người dùng và tin nhắn của bot vào danh sách
    const userMessage = { role: "user", content: message };
    setChatHistory((prev) => {
      const updatedHistory = [...prev, userMessage];
      localStorage.setItem("chatHistory", JSON.stringify(updatedHistory));
      return updatedHistory;
    });

    const waitingBotMessage = { role: "assistant", content: "" };
    setChatHistory((prev) => [...prev, waitingBotMessage]);

    // Gọi API để lấy kết quả
    const stream = await client.chat.completions.create({
      messages: [...chatHistory, userMessage],
      model: "llama3-8b-8192",
      stream: true,
    });

    let botResponse = "";
    for await (const chunk of stream) {
      const content = chunk.choices[0]?.delta?.content || "";
      botResponse += content;
      setChatHistory((prev) => {
        const updatedHistory = prev.map((msg, index) =>
          index === prev.length - 1 ? { ...msg, content: botResponse } : msg
        );
        localStorage.setItem("chatHistory", JSON.stringify(updatedHistory));
        return updatedHistory;
      });
    }
  };

  useEffect(() => {
    if (!client.apiKey) {
      const savedKey = localStorage.getItem("apiKey");
      if (savedKey) {
        client.apiKey = savedKey;
      } else {
        const promptKey = window.prompt(
          "Để sử dụng ứng dụng này, bạn cần có một key Groq. Sau khi có key, hãy nhập vào ô bên dưới."
        );
        if (promptKey) {
          client.apiKey = promptKey;
          localStorage.setItem("apiKey", promptKey);
        }
      }
    }
  }, []);

  const clearChatHistory = () => {
    setChatHistory([]);
    localStorage.removeItem("chatHistory");
  };

  return (
    <div className="bg-gray-100 h-screen flex flex-col">
      <div className="container mx-auto p-4 flex flex-col h-full max-w-2xl">
        <h1 className="text-2xl font-bold mb-4">ChatUI với React + Groq</h1>

        <button
          onClick={clearChatHistory}
          className="mb-4 bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
        >
          Xóa lịch sử chat
        </button>

        <form className="flex" onSubmit={submitForm}>
          <input
            type="text"
            placeholder="Tin nhắn của bạn..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            className="flex-grow p-2 rounded-l border border-gray-300"
          />
          <button
            type="submit"
            className="bg-blue-500 text-white px-4 py-2 rounded-r hover:bg-blue-600"
          >
            Gửi tin nhắn
          </button>
        </form>

        <div className="flex-grow overflow-y-auto mt-4 bg-white rounded shadow p-4">
          {chatHistory.map((chatMessage, i) => (
            <div
              key={i}
              className={`mb-2 ${
                isBotMessage(chatMessage) ? "text-right" : ""
              }`}
            >
              <p className="text-gray-600 text-sm">
                {isBotMessage(chatMessage) ? "Bot" : "User"}
              </p>
              <p
                className={`p-2 rounded-lg inline-block ${
                  isBotMessage(chatMessage) ? "bg-green-100" : "bg-blue-100"
                }`}
              >
                {chatMessage.content}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default App;
