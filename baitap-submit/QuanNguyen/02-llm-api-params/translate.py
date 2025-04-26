from groq import Groq

client = Groq(
    api_key=''
)

def translate_file(input_file, output_file, target_language):
    with open(input_file, 'r', encoding='utf-8') as file:
        content = file.read()
    
    chunks = [content[i:i+3000] for i in range(0, len(content), 3000)]
    translated_content = ""
    
    for chunk in chunks:
        prompt = f"Dịch đoạn văn sau sang {target_language}:\n{chunk}"
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}]
        )
        
        if response.choices and len(response.choices) > 0:
            translated_content += response.choices[0].message.content.strip() + "\n"
        else:
            translated_content += "Không thể dịch đoạn văn này.\n"
    
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(translated_content)
    print(f"Dịch xong! Nội dung đã được lưu vào {output_file}")

if __name__ == "__main__":
    translate_file("input.txt", "output.txt", "tiếng Anh")