from groq import Groq

client = Groq(
    api_key=''
)


def simple_chat():
    
    while True:
        user_input = input("Bạn: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Tạm biệt!")
            break
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": user_input}],
            stream=True
        )
        
        for chunk in response:
            print(chunk.choices[0].delta.content or "", end="")
   

if __name__ == "__main__":
    simple_chat()
    


