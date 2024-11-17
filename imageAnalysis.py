import os
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image

load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

genai.configure(api_key=GOOGLE_API_KEY)

def process_image_with_gemini(image_path):
    """
    Processes an image using Google's Gemini Vision model.
    
    Args:
        image_path (str): Path to the image file
    """
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        image = Image.open(image_path)
        
        response = model.generate_content(
            contents=[
                "Please analyze this image and describe what you see in detail, including:\n"
                "1. The main objects and features\n"
                "2. Advice on how to care for this crop\n"
                "3. If this is a soil sample, describe its properties",
                image
            ]
        )
        
        print("Image processed successfully!")
        return response.text
        
    except Exception as e:
        print(f"Error processing the image: {e}")
        return None
