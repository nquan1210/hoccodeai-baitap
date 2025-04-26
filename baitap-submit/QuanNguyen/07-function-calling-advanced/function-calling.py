from pprint import pprint
import json
from groq import Groq
import inspect
from pydantic import TypeAdapter
import requests

# Implement 3 hàm


def get_current_weather(location: str, unit: str):
    """Get the current weather in a given location"""
    # Hardcoded response for demo purposes
    return "Trời rét vãi nôi, 7 độ C"


def get_stock_price(symbol: str):
    # Không làm gì cả, để hàm trống
    pass


# Bài 2: Implement hàm `view_website`, sử dụng `requests` và JinaAI để đọc markdown từ URL
def view_website(url: str):
    """View a website and convert it to markdown using JinaAI"""
    # Sử dụng JinaAI để đọc markdown từ URL
    jina_url = f'https://r.jina.ai/https://{url}'
    headers = {
        'Authorization': 'Bearer jina_68d9645b3fb2f41ddbb50ec58a665bc13392SbLmxlVjCRTQowOjxML_OW51KC'
    }
    
    response = requests.get(url=jina_url, headers=headers)
    return response.text


# Bài 1: Thay vì tự viết object `tools`, hãy xem lại bài trước, sửa code và dùng `inspect` và `TypeAdapter` để define `tools`
def function_to_tool(func):
    """Chuyển đổi một hàm thành tool theo định dạng API của OpenAI"""
    signature = inspect.signature(func)
    parameters = {}
    required = []
    
    for name, param in signature.parameters.items():
        param_type = param.annotation
        if param_type is inspect.Parameter.empty:
            param_type = "string"
        else:
            param_type = str(param_type).replace("<class '", "").replace("'>", "")
            
        if param_type == "str":
            param_type = "string"
        elif param_type == "int" or param_type == "float":
            param_type = "number"
        elif param_type == "bool":
            param_type = "boolean"
        
        parameters[name] = {
            "type": param_type
        }
        
        if param.default is inspect.Parameter.empty:
            required.append(name)
    
    return {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": func.__doc__ or f"Call the function {func.__name__}",
            "parameters": {
                "type": "object",
                "properties": parameters,
                "required": required
            }
        }
    }

tools = [
    function_to_tool(get_current_weather),
    function_to_tool(get_stock_price),
    function_to_tool(view_website)
]

# https://console.groq.com/apis
client = Groq(
    api_key='',
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

if tool_call.function.name == 'get_current_weather':
    weather_result = get_current_weather(
        arguments.get('location'), arguments.get('unit'))
    # Hoặc code này cũng tương tự
    # weather_result = get_current_weather(**arguments)
    print(f"Kết quả bước 4: {weather_result}")

    print("Bước 5: Gửi kết quả lên cho LLM")
    messages.append(response.choices[0].message)
    messages.append({
        "role": "tool",
        "content": weather_result,
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
