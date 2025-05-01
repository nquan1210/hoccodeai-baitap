from groq import Groq
import os

client = Groq(
    api_key=os.getenv('GROQ_API_KEY', '')
)



def chat_with_memory():
    messages = []
    while True:
        user_input = input("Bạn: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Tạm biệt!")
            break
        messages.append({"role": "user", "content": user_input})
        try:
            response = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=messages
            )
            # Access the response content directly
            if response.choices and len(response.choices) > 0:
                bot_reply = response.choices[0].message.content
            else:
                bot_reply = "Bot không thể trả lời."
            
            print("Bot:", bot_reply)
            messages.append({"role": "assistant", "content": bot_reply})
        except Exception as e:
            print("Đã xảy ra lỗi:", str(e))

if __name__ == "__main__":
    chat_with_memory()