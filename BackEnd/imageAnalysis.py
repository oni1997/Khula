import os
import google.generativeai as genai
from PIL import Image

# Configure the API key
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
print(GOOGLE_API_KEY)
genai.configure(api_key=GOOGLE_API_KEY)

def process_image_with_gemini(image_path):
    """
    Processes an image using Google's Gemini Vision model.
    
    Args:
        image_path (str): Path to the image file
    """
    try:
        # Load the Gemini Pro Vision model
        model = genai.GenerativeModel('gemini-1.5-pro-002')
        
        # Open and prepare the image using PIL
        image = Image.open(image_path)
        
        # Generate content from the image
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

# Use the function
image_path = "../Test/istockphoto-1323415950-1024x1024.jpg"
result = process_image_with_gemini(image_path)

if result:
    print("\nAnalysis Results:")
    print("-----------------")
    print(result)