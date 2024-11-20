from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import torch
import os

class ImageCaptioning:
    def __init__(self):
        # Load pre-trained processor and model for image captioning
        self.processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        self.model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
        self.supported_extensions = (".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff")

    def load_image(self, image_path):
        # Check if the file exists and has a supported extension
        if not os.path.exists(image_path):
            print("File does not exist. Please provide a valid file path.")
            return None
        
        if not image_path.lower().endswith(self.supported_extensions):
            print("Unsupported file type. Please provide an image with a supported extension.")
            return None

        try:
            # Open the image file
            image = Image.open(image_path)
            return image
        except Exception as e:
            print(f"Error loading image: {e}")
            return None

    def generate_caption(self, image_path):
        # Load the image
        image = self.load_image(image_path)
        if image is None:
            return None

        # Convert the image to RGB mode if it's not already
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Preprocess the image for the BLIP model
        inputs = self.processor(image, return_tensors="pt")

        # Perform inference (Image Captioning)
        with torch.no_grad():
            generated_ids = self.model.generate(**inputs)

        # Decode the generated caption
        generated_caption = self.processor.decode(generated_ids[0], skip_special_tokens=True)

        return generated_caption
