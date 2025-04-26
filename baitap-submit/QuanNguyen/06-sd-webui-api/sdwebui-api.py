import gradio as gr
import base64
import requests
import os
import time
import json
from PIL import Image
import io

# WebUI API URL
URL = "http://127.0.0.1:7860"

def base64_to_image(base64_string):
    """Convert a base64 string to a PIL Image"""
    image_data = base64.b64decode(base64_string)
    image = Image.open(io.BytesIO(image_data))
    return image

def base64_to_file(base64_string, save_path):
    """Save a base64 string to a file"""
    with open(save_path, 'wb') as f:
        f.write(base64.b64decode(base64_string))
    return save_path

os.makedirs("generated_images", exist_ok=True)

def generate(prompt, negative_prompt, guidance_scale, num_steps, seed):
    """Generate an image using the WebUI API and return it"""
    if not prompt:
        return None, "Please provide a prompt"
    
    try:
        print("Starting Inference")
        payload = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "steps": int(num_steps),
            "cfg_scale": float(guidance_scale),
            "width": 512,
            "height": 512,
            "seed": int(seed) if seed != -1 else -1,
        }
        
        response = requests.post(f"{URL}/sdapi/v1/txt2img", json=payload)
        
        if response.status_code != 200:
            return None, f"Error: API returned status code {response.status_code}"
            
        resp_json = response.json()
        
        if not resp_json['images']:
            return None, "No image generated"
            
        image = base64_to_image(resp_json['images'][0])
        
        used_seed = None
        info = resp_json.get("info", "")
        if isinstance(info, str) and info:
            try:
                info_dict = json.loads(info)
                used_seed = info_dict.get("seed")
            except:
                used_seed = seed
                
        return image, f"Image generated with seed: {used_seed if used_seed is not None else seed}"
        
    except Exception as e:
        print(f"Error generating image: {str(e)}")
        return None, f"Error: {str(e)}"

def save_image(img):
    """Save the generated image to disk"""
    if img is None:
        return "No image to save"
    
    timestamp = int(time.time())
    filename = f"generated_images/image_{timestamp}.png"
    img.save(filename)
    return f"Image saved to {filename}"

with gr.Blocks(title="Diffusion Image Generator") as app:
    gr.Markdown("# 🎨 Diffusion Image Generator")
    gr.Markdown("Generate images using Stable Diffusion WebUI API")
    
    with gr.Row():
        with gr.Column(scale=3):
            prompt = gr.Textbox(
                label="Prompt",
                placeholder="A beautiful sunset over mountains, trending on artstation, highly detailed",
                lines=3
            )
            negative_prompt = gr.Textbox(
                label="Negative Prompt",
                placeholder="blurry, bad quality, distorted, deformed",
                lines=2
            )
            
            with gr.Row():
                guidance_scale = gr.Slider(
                    label="Guidance Scale",
                    minimum=1.0,
                    maximum=20.0,
                    value=7.5,
                    step=0.5
                )
                num_steps = gr.Slider(
                    label="Number of Steps",
                    minimum=10,
                    maximum=100,
                    value=30,
                    step=1
                )
                seed = gr.Number(
                    label="Seed (-1 for random)",
                    value=-1
                )
            
            generate_btn = gr.Button("Generate Image", variant="primary")
            
        with gr.Column(scale=4):
            output_image = gr.Image(label="Generated Image", type="pil")
            output_message = gr.Textbox(label="Message")
            save_btn = gr.Button("Save Image")
    
    generate_btn.click(
        fn=generate,
        inputs=[prompt, negative_prompt, guidance_scale, num_steps, seed],
        outputs=[output_image, output_message]
    )
    
    save_btn.click(
        fn=save_image,
        inputs=[output_image],
        outputs=[output_message]
    )
    
    gr.Examples(
        [
            ["A beautiful mountain landscape with a lake, highly detailed, trending on artstation", 
             "blurry, bad quality, low resolution", 7.5, 30, -1],
            ["A futuristic cityscape at night with neon lights, cyberpunk style", 
             "blurry, bad quality, distorted", 8.0, 40, -1],
            ["Portrait of a dragon, fantasy art, detailed scales, majestic", 
             "blurry, bad anatomy, distorted", 7.0, 50, -1],
        ],
        inputs=[prompt, negative_prompt, guidance_scale, num_steps, seed]
    )
    
    gr.Markdown("""
    ### Note: 
    This application requires the Stable Diffusion WebUI to be running with API enabled.
    Launch your WebUI with the `--api` parameter.
    """)

if __name__ == "__main__":
    try:
        # Try to connect to the API
        requests.get(URL, timeout=2)
        app.launch(share=True)
    except:
        print(f"Error: Could not connect to the WebUI API at {URL}")
        print("Make sure the Stable Diffusion WebUI is running with the --api flag")