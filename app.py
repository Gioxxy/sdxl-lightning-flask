from flask import Flask, request, send_file, jsonify
import io
import torch
from diffusers import StableDiffusionXLPipeline, UNet2DConditionModel, EulerDiscreteScheduler
from huggingface_hub import hf_hub_download
from safetensors.torch import load_file

base = "stabilityai/stable-diffusion-xl-base-1.0"
repo = "ByteDance/SDXL-Lightning"
ckpt = "sdxl_lightning_4step_unet.safetensors" # Use the correct ckpt for your step setting!

app = Flask(__name__)

# Load model.
unet = UNet2DConditionModel.from_config(base, subfolder="unet").to("cuda", torch.float16)
unet.load_state_dict(load_file(hf_hub_download(repo, ckpt), device="cuda"))
pipe = StableDiffusionXLPipeline.from_pretrained(base, unet=unet, torch_dtype=torch.float16, variant="fp16").to("cuda")
# Ensure sampler uses "trailing" timesteps.
pipe.scheduler = EulerDiscreteScheduler.from_config(pipe.scheduler.config, timestep_spacing="trailing")

@app.route('/generate', methods=['POST'])
def generate_image():
    # Get the text prompt from the request
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"error": "Missing 'text' field in the request body"}), 400
    text_prompt = data['text']
    
    # Ensure using the same inference steps as the loaded model and CFG set to 0.
    image_byte_stream = io.BytesIO()
    pipe(text_prompt, num_inference_steps=4, guidance_scale=0).images[0].save(image_byte_stream, format='PNG')
    image_byte_stream.seek(0)
    
    # Return the image as a response
    return send_file(image_byte_stream, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)