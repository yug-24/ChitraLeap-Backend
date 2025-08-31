import os
import json
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)

# Enable CORS to allow requests from any origin (necessary for Builder.io frontend)
CORS(app, origins="*")

# Set Flask secret key from environment variable
app.secret_key = os.environ.get("SESSION_SECRET", "fallback-secret-key")

# Initialize OpenAI client with API key from environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
if not OPENAI_API_KEY:
    logging.error("OPENAI_API_KEY not found in environment variables")

openai_client = OpenAI(api_key=OPENAI_API_KEY)

@app.route('/generate-ad', methods=['POST'])
def generate_ad():
    """
    Generate ad copy and images using OpenAI GPT-4 and DALL-E 3
    
    Expected JSON payload:
    {
        "product_description": "Handmade silk sarees from Jaipur",
        "target_audience": "Women aged 25-40 for the upcoming festival season",
        "offer": "20% off for Diwali",
        "language": "Hinglish"
    }
    
    Returns:
    {
        "ad_copy": [
            {"headline": "...", "body": "..."},
            {"headline": "...", "body": "..."},
            {"headline": "...", "body": "..."}
        ],
        "image_urls": ["url1", "url2", "url3"]
    }
    """
    
    try:
        # Step A: Receive and validate input
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Check if all required fields are present
        required_fields = ['product_description', 'target_audience', 'offer', 'language']
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        
        if missing_fields:
            return jsonify({
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400
        
        product_description = data['product_description']
        target_audience = data['target_audience']
        offer = data['offer']
        language = data['language']
        
        logging.info(f"Processing ad generation request for: {product_description}")
        
        # Step B: First OpenAI Call (GPT-4 for Text and Image Prompts)
        meta_prompt = f"""
        You are an expert advertising creative director specializing in the Indian market. Your task is to create compelling advertisements that resonate with Indian culture, festivals, and consumer behavior.

        Based on the following information, create advertising content:
        - Product/Service: {product_description}
        - Target Audience: {target_audience}
        - Special Offer: {offer}
        - Language: {language}

        Return a single, clean JSON object with exactly two keys:

        1. "ad_copy": An array of 3 different, compelling ad copy variations written in {language}. Each variation should be an object with "headline" and "body" keys. Make them culturally relevant, emotionally engaging, and suitable for the Indian market. Include festival references, family values, and local sentiments where appropriate.

        2. "image_prompts": An array of 3 highly descriptive, visually rich, and culturally specific prompts for DALL-E 3 image generation. These prompts should be in English and reflect Indian aesthetics, festivals, colors, and the target audience. Include details about lighting, settings, clothing, expressions, and cultural elements. For example, instead of "woman in a saree," use "A vibrant, festive scene in a traditional Indian setting during Diwali, featuring a smiling woman in her early 30s elegantly wearing a beautiful handmade silk saree with intricate gold borders, surrounded by warm golden lighting from diyas and marigold decorations, with a joyful expression showcasing the premium quality and cultural significance of the product."

        Respond with ONLY the JSON object, no additional text or explanation.
        """
        
        # Make API call to GPT-5
        # the newest OpenAI model is "gpt-5" which was released August 7, 2025.
        # do not change this unless explicitly requested by the user
        gpt_response = openai_client.chat.completions.create(
            model="gpt-5",
            messages=[{"role": "user", "content": meta_prompt}],
            response_format={"type": "json_object"},
            temperature=0.8,
            max_tokens=2000
        )
        
        # Parse GPT-4 response
        gpt_content = gpt_response.choices[0].message.content
        logging.debug(f"GPT-4 response: {gpt_content}")
        
        try:
            if not gpt_content:
                return jsonify({"error": "Empty response from GPT-4"}), 500
            gpt_data = json.loads(gpt_content)
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse GPT-4 JSON response: {e}")
            return jsonify({"error": "Invalid response format from GPT-4"}), 500
        
        # Validate GPT-4 response structure
        if 'ad_copy' not in gpt_data or 'image_prompts' not in gpt_data:
            return jsonify({"error": "Invalid response structure from GPT-4"}), 500
        
        ad_copy = gpt_data['ad_copy']
        image_prompts = gpt_data['image_prompts']
        
        if len(image_prompts) != 3:
            return jsonify({"error": "Expected 3 image prompts from GPT-4"}), 500
        
        # Step C: Second OpenAI Call (DALL-E 3 for Image Generation)
        image_urls = []
        
        # Loop through each image prompt and generate images
        for i, prompt in enumerate(image_prompts):
            try:
                logging.info(f"Generating image {i+1}/3 with DALL-E 3")
                
                # Make API call to DALL-E 3
                image_response = openai_client.images.generate(
                    model="dall-e-3",
                    prompt=prompt,
                    n=1,
                    size="1024x1024",
                    quality="standard"
                )
                
                # Extract image URL from response
                if not image_response.data or len(image_response.data) == 0:
                    raise Exception("No image data received from DALL-E 3")
                image_url = image_response.data[0].url
                image_urls.append(image_url)
                
                logging.debug(f"Generated image {i+1} URL: {image_url}")
                
            except Exception as dalle_error:
                logging.error(f"DALL-E 3 API error for image {i+1}: {dalle_error}")
                return jsonify({
                    "error": f"Failed to generate image {i+1}: {str(dalle_error)}"
                }), 500
        
        # Step D: Final Response
        final_response = {
            "ad_copy": ad_copy,
            "image_urls": image_urls
        }
        
        logging.info("Successfully generated ad copy and images")
        return jsonify(final_response), 200
        
    except Exception as e:
        logging.error(f"Unexpected error in generate_ad: {e}")
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"
        }), 500

@app.route('/', methods=['GET'])
def home():
    """Home endpoint"""
    return jsonify({
        "service": "ChitraLeap Backend",
        "status": "running",
        "endpoints": {
            "/generate-ad": "POST - Generate ad copy and images",
            "/health": "GET - Health check"
        }
    }), 200

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "ChitraLeap Backend"}), 200

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors"""
    return jsonify({"error": "Method not allowed"}), 405

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    # Run the Flask application
    # Listen on port 5000 as per flask_website guidelines
    app.run(host='0.0.0.0', port=5000, debug=True)
