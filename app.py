from flask import Flask, render_template, request, jsonify
import requests
import json
import os

app = Flask(__name__)

# IMPORTANT: For security, load your API key from an environment variable in production.
LLM_API_KEY = "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"
# Replace with the actual endpoint provided by your LLM vendor.
LLM_API_URL = "https://api.groq.com/openai/v1/chat/completions"  # <-- UPDATE THIS URL

@app.route('/')
def index():
    return render_template('index.html')

def generate_recipe(ingredients, cook_time, cuisine, dietary):
    """
    Connects to the llama-3.3-70b-versatile LLM to generate a recipe.
    Constructs a prompt based on user inputs and expects the LLM to return a JSON-formatted recipe.
    """
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
        # Return an error message if the LLM API fails
        return {"error": "LLM API error", "details": response.text}
    
    result = response.json()
    generated_text = result.get("generated_text", "")
    
    try:
        # Attempt to parse the generated text as JSON
        recipe_data = json.loads(generated_text)
        return recipe_data
    except Exception as e:
        # If parsing fails, fall back to returning the raw text as instructions
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

@app.route('/generate-recipe', methods=['POST'])
def generate_recipe_api():
    data = request.get_json()
    ingredients = data.get('ingredients', '')
    cook_time = data.get('cook_time', '')
    cuisine = data.get('cuisine', '')
    dietary = data.get('dietary', [])  # Expects a list of dietary restrictions

    recipe = generate_recipe(ingredients, cook_time, cuisine, dietary)
    return jsonify(recipe)

if __name__ == '__main__':
    app.run(debug=True)
