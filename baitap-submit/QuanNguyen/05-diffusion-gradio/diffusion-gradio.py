import gradio as gr
import torch
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
import os
import time

device = "cpu"
print(f"Using device: {device}")

class DiffusionModel:
    def __init__(self):
        self.model_id = "runwayml/stable-diffusion-v1-5"
        self.pipeline = None
        self.load_model()
        
    def load_model(self):
        """Load the diffusion model"""
        print("Loading model...")
        
        self.pipeline = StableDiffusionPipeline.from_pretrained(
            self.model_id, 
            torch_dtype=torch.float16 if device == "cuda" else torch.float32
        )
        
        self.pipeline.scheduler = DPMSolverMultistepScheduler.from_config(
            self.pipeline.scheduler.config
        )
        
        self.pipeline = self.pipeline.to(device)
        
        self.pipeline.enable_attention_slicing()
        
        print("Model loaded successfully!")
    
    def generate_image(self, prompt, negative_prompt, guidance_scale, num_steps, seed):
        """Generate an image based on the provided parameters"""
        
        if seed == -1:
            seed = int(time.time())
        
        generator = torch.Generator(device=device).manual_seed(seed)
        
        # Generate the image
        result = self.pipeline(
            prompt=prompt,
            negative_prompt=negative_prompt,
            guidance_scale=guidance_scale,
            num_inference_steps=num_steps,
            generator=generator
        )
        
        image = result.images[0]
        return image, f"Image generated with seed: {seed}"

# Create a folder for saving generated images if it doesn't exist
os.makedirs("generated_images", exist_ok=True)

# Initialize the model
model = DiffusionModel()

def save_image(img):
    """Save the generated image to disk"""
    if img is None:
        return "No image to save"
    
    timestamp = int(time.time())
    filename = f"generated_images/image_{timestamp}.png"
    img.save(filename)
    return f"Image saved to {filename}"

def generate(prompt, negative_prompt, guidance_scale, num_steps, seed):
    """Generate an image and return it"""
    if not prompt:
        return None, "Please provide a prompt"
    
    try:
        image, message = model.generate_image(
            prompt=prompt, 
            negative_prompt=negative_prompt, 
            guidance_scale=float(guidance_scale), 
            num_steps=int(num_steps),
            seed=int(seed)
        )
        return image, message
    except Exception as e:
        return None, f"Error generating image: {str(e)}"

with gr.Blocks(title="Diffusion Image Generator") as app:
    gr.Markdown("# 🎨 Diffusion Image Generator")
    gr.Markdown("Generate images using Stable Diffusion model")
    
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

if __name__ == "__main__":
    app.launch(share=True) 