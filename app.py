from flask import Flask, render_template, request, jsonify
import requests
import json
import os
from flask_cors import CORS, cross_origin

app = Flask(__name__)
# Allow CORS for all routes with specified methods.
CORS(app, resources={r"/*": {"origins": "*"}}, methods=["GET", "POST", "OPTIONS"])

LLM_API_KEY = "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"
LLM_API_URL = "https://api.groq.com/openai/v1/chat/completions"  # Update this URL if needed

@app.route('/')
def index():
    return render_template('index.html')

def generate_recipe(ingredients, cook_time, cuisine, dietary):
    dietary_str = ", ".join(dietary) if dietary else "none"
    prompt = (
        f"Generate a detailed recipe based on the following input:\n"
        f"Ingredients: {ingredients}\n"
        f"Cooking Time: {cook_time} minutes\n"
        f"Preferred Cuisine: {cuisine if cuisine else 'Any'}\n"
        f"Dietary Restrictions: {dietary_str}\n\n"
        f"Please provide the recipe in JSON format with these keys:\n"
        f"- title\n"
        f"- prep_time\n"
        f"- cook_time\n"
        f"- total_time\n"
        f"- servings\n"
        f"- ingredients (as a list)\n"
        f"- instructions (as a list)\n"
        f"- tags (an object with keys 'cuisine' and 'dietary')"
    )
    
    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "prompt": prompt,
        "max_tokens": 1024,
        "temperature": 0.7
    }
    
    response = requests.post(LLM_API_URL, headers=headers, json=payload)
    if response.status_code != 200:
        return {"error": "LLM API error", "details": response.text}
    
    result = response.json()
    generated_text = result.get("generated_text", "")
    
    try:
        recipe_data = json.loads(generated_text)
        return recipe_data
    except Exception as e:
        return {
            "title": "Generated Recipe",
            "prep_time": "Unknown",
            "cook_time": cook_time,
            "total_time": "Unknown",
            "servings": "Unknown",
            "ingredients": [],
            "instructions": [generated_text],
            "tags": {"cuisine": cuisine, "dietary": dietary}
        }

@app.route('/generate-recipe', methods=['POST', 'OPTIONS'])
@cross_origin()  # Explicitly allow CORS on this route
def generate_recipe_api():
    data = request.get_json()
    ingredients = data.get('ingredients', '')
    cook_time = data.get('cook_time', '')
    cuisine = data.get('cuisine', '')
    dietary = data.get('dietary', [])
    recipe = generate_recipe(ingredients, cook_time, cuisine, dietary)
    return jsonify(recipe)

if __name__ == '__main__':
    app.run(debug=True, port=3000)
