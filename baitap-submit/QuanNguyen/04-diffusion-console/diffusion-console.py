from diffusers import DiffusionPipeline
import torch


def main():
    prompt = input("Nhập prompt: ")
    width = int(input("Nhập chiều ngang của ảnh: "))
    height = int(input("Nhập chiều cao của ảnh: "))
    device = 'cpu'

    pipeline = DiffusionPipeline.from_pretrained(
        "lykon/dreamshaper-8",
        use_safetensors=True,
        safety_checker=None,
        requires_safety_checker=False
    )
    pipeline.to(device)

    print("Đang tạo hình ảnh...")
    image = pipeline(prompt, height=height, width=width,num_inference_steps=20).images[0]
    
    pipeline.unet = torch.compile(
    pipeline.unet, mode="reduce-overhead", fullgraph=True)
    
    output_path = "output_image.png"
    image.save(output_path)

if __name__ == "__main__":
    main()