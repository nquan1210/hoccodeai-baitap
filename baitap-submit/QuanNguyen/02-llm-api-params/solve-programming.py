from groq import Groq

client = Groq(
    api_key=''
)


    # // Tạo một file Python từ một câu hỏi lập trình
def solve_programming_task():
    question = input("Nhập câu hỏi lập trình: ")
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": question}],
        max_tokens=300
    )
    code = response.choices[0].message.content.strip()
    print("Code được tạo:\n", code)
    
    with open("final.py", "w", encoding="utf-8") as file:
        file.write(code)
    print("Code đã được lưu vào file final.py")

if __name__ == "__main__":
    solve_programming_task()