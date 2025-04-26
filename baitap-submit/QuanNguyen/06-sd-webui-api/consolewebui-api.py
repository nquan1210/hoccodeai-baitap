import requests
import base64
import json
import os
import time
from PIL import Image
import io

URL = "http://127.0.0.1:7860"

def base64_to_image(base64_string):
    image_data = base64.b64decode(base64_string)
    image = Image.open(io.BytesIO(image_data))
    return image

def save_image(image, folder="output"):
    os.makedirs(folder, exist_ok=True)
    timestamp = int(time.time())
    filename = f"{folder}/image_{timestamp}.png"
    image.save(filename)
    return filename

def generate_image(prompt, negative_prompt="", width=512, height=512, steps=30, guidance_scale=7.5, seed=-1):
    try:
        print("Đang tạo hình ảnh...")
        
        payload = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "steps": steps,
            "cfg_scale": guidance_scale,
            "width": width,
            "height": height,
            "seed": seed
        }
        
        # Gửi yêu cầu đến API
        response = requests.post(f"{URL}/sdapi/v1/txt2img", json=payload)
        
        if response.status_code != 200:
            print(f"Lỗi: API trả về mã trạng thái {response.status_code}")
            return None
            
        # Xử lý phản hồi từ API
        resp_json = response.json()
        
        if not resp_json['images']:
            print("Không có hình ảnh được tạo")
            return None
            
        # Chuyển đổi chuỗi base64 thành hình ảnh
        image = base64_to_image(resp_json['images'][0])
        
        # Lấy seed đã sử dụng (quan trọng nếu sử dụng seed ngẫu nhiên)
        used_seed = seed
        info = resp_json.get("info", "")
        if isinstance(info, str) and info:
            try:
                info_dict = json.loads(info)
                used_seed = info_dict.get("seed", seed)
            except:
                pass
                
        print(f"Hình ảnh đã được tạo với seed: {used_seed}")
        return image
        
    except Exception as e:
        print(f"Lỗi khi tạo hình ảnh: {str(e)}")
        return None

def check_api_connection():
    try:
        requests.get(URL, timeout=2)
        return True
    except:
        return False

def main():
    print("=" * 50)
    print("STABLE DIFFUSION WEBUI API - ỨNG DỤNG CONSOLE")
    print("=" * 50)
    
    if not check_api_connection():
        print(f"Lỗi: Không thể kết nối đến WebUI API tại {URL}")
        print("Đảm bảo Stable Diffusion WebUI đang chạy với tham số --api")
        return
    
    prompt = input("Nhập prompt của bạn: ")
    if not prompt:
        print("Prompt không được để trống!")
        return
    
    image = generate_image(prompt)
    
    if image:
        saved_path = save_image(image)
        print(f"Hình ảnh đã được lưu tại: {saved_path}")

if __name__ == "__main__":
    main()