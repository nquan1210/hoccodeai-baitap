from pprint import pprint
import json
from groq import Groq
import inspect
from pydantic import TypeAdapter
import requests
import os

# Implement 3 hàm


def get_current_weather(location: str, unit: str):
    """Get the current weather in a given location"""
    # Hardcoded response for demo purposes
    return "Trời rét vãi nôi, 7 độ C"


def get_stock_price(symbol: str):
    """Get the current stock price for a given symbol"""
    # Không làm gì cả, để hàm trống
    pass


# Bài 2: Implement hàm `view_website`, sử dụng `requests` và JinaAI để đọc markdown từ URL
def view_website(url: str):
    """View a website and convert it to markdown using JinaAI"""
    # Sử dụng JinaAI để đọc markdown từ URL
    jina_url = f'https://r.jina.ai/https://{url}'
    headers = {
        'Authorization': os.getenv('JINA_API_KEY', '')
    }
    
    response = requests.get(url=jina_url, headers=headers)
    return response.text


# Bài 1: Thay vì tự viết object `tools`, hãy xem lại bài trước, sửa code và dùng `inspect` và `TypeAdapter` để define `tools`
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": inspect.getdoc(get_current_weather),
            "parameters": TypeAdapter(get_current_weather).json_schema(),
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_stock_price",
            "description": inspect.getdoc(get_stock_price),
            "parameters": TypeAdapter(get_stock_price).json_schema(),
        },
    },
    {
        "type": "function",
        "function": {
            "name": "view_website",
            "description": inspect.getdoc(view_website),
            "parameters": TypeAdapter(view_website).json_schema(),
        },
    },
]

# https://console.groq.com/apis
client = Groq(
    api_key=os.getenv('GROQ_API_KEY', ''),
)
COMPLETION_MODEL = "llama3-70b-8192"

messages = [{"role": "user", "content": "Thời tiết ở Hà Nội hôm nay thế nào?"}]

print("Bước 1: Gửi message lên cho LLM")
pprint(messages)

response = client.chat.completions.create(
    model=COMPLETION_MODEL,
    messages=messages,
    tools=tools
)

print("Bước 2: LLM đọc và phân tích ngữ cảnh LLM")
pprint(response)

print("Bước 3: Lấy kết quả từ LLM")
tool_call = response.choices[0].message.tool_calls[0]

pprint(tool_call)
arguments = json.loads(tool_call.function.arguments)

print("Bước 4: Chạy function get_current_weather ở máy mình")

FUNCTION_MAP = {
    "get_current_weather": get_current_weather,
    "get_stock_price": get_stock_price,
    "view_website": view_website
}

# Dynamically call the function based on tool_call.function.name

tool_function = FUNCTION_MAP[tool_call.function.name]
result = tool_function(**arguments)
print(f"Kết quả bước 4: {result}")

print("Bước 5: Gửi kết quả lên cho LLM")
messages.append(response.choices[0].message)
messages.append({
    "role": "tool",
    "content": result,
    "tool_call_id": tool_call.id
})
pprint(messages)
final_response = client.chat.completions.create(
    model=COMPLETION_MODEL,
    messages=messages
    # Ở đây không có tools cũng không sao, vì ta không cần gọi nữa
)
print(
    f"Kết quả cuối cùng từ LLM: {final_response.choices[0].message.content}.")
