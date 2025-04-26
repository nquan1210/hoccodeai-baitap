import requests
from bs4 import BeautifulSoup
from groq import Groq

client = Groq(
    api_key=''
)

def summarize_website():
    url = input("Nhập URL website: ")
    response = requests.get(url)
    
    if response.status_code != 200:
        print("Không thể truy cập website. Vui lòng kiểm tra URL.")
        return
    
    soup = BeautifulSoup(response.text, 'html.parser')
    content_div = soup.find('div', id='main-detail')
    
    if content_div is None:
        print("Không tìm thấy nội dung trong website. Vui lòng kiểm tra cấu trúc HTML.")
        return
    
    content = content_div.get_text(strip=True)
    
    prompt = f"Tóm tắt nội dung sau:\n{content}"
    try:
        summary = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200
        )
        print("Tóm tắt:", summary.choices[0].message.content.strip())
    except Exception as e:
        print("Đã xảy ra lỗi khi gọi API:", str(e))

if __name__ == "__main__":
    summarize_website()