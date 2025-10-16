import os
from google import genai
from google.generativeai.errors import APIError
from langdetect import detect
from PIL import Image
from openai import OpenAI

class AIPersonality:
    """
    Manages communication with AI models (Gemini or OpenAI) with personality and language detection.
    """
    def __init__(self, use_gemini: bool = True):
        self.use_gemini = use_gemini
        self.model_name = "gemini-2.5-flash" if use_gemini else "gpt-4o"
        
        if self.use_gemini:
            # Initialize Gemini client
            self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        else:
            # Initialize OpenAI client
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def _generate_gemini_reply(self, system_prompt, user_input, image_path=None):
        """Generates a reply using the Google Gemini model."""
        
        # Prepare content list
        content_parts = [user_input]
        
        if image_path:
            try:
                img = Image.open(image_path)
                content_parts.insert(0, img)
            except Exception as e:
                print(f"Error opening image: {e}")
                # Continue without image if there's an issue

        try:
            config = {
                "system_instruction": system_prompt
            }
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=content_parts,
                config=config
            )
            return response.text
        except APIError as e:
            print(f"Gemini API Error: {e}")
            return "Sorry, I encountered an API error while processing your request. Please try again."
        except Exception as e:
            print(f"An unexpected error occurred with Gemini: {e}")
            return "An unexpected error occurred."

    def _generate_openai_reply(self, system_prompt, user_input, image_path=None):
        """Generates a reply using the OpenAI model."""
        
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Prepare user content
        user_content = [{"type": "text", "text": user_input}]

        if image_path:
            # Note: For real-world deployment with OpenAI, you should use a public image URL, 
            # or base64 encode the image, as the local path won't work easily.
            try:
                # Placeholder for actual image handling (e.g., base64 encoding or URL)
                # This basic implementation assumes the client can handle local paths or will be adapted.
                print("Note: OpenAI vision models typically require a public URL or base64 encoding.")
                # Base64 encoding logic would go here
            except Exception as e:
                print(f"Error handling image for OpenAI: {e}")

        messages.append({"role": "user", "content": user_content})

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI Error: {e}")
            return "Sorry, I encountered an error while processing your request with OpenAI."

    def generate_ai_reply(self, user_input: str, personality: str, image_path: str = None):
        """
        Public method to generate the AI's reply.
        """
        # 1. Detect Language
        try:
            lang = detect(user_input)
        except:
            lang = "en"  # Default to English if detection fails

        # 2. Construct System Prompt
        system_prompt = (
            f"You are an AI with the personality of a {personality}. "
            f"Your response must be entirely in the language detected in the user's input, which is '{lang}'. "
            "Maintain your persona strictly. Be concise and helpful."
        )

        # 3. Generate Reply
        if self.use_gemini:
            return self._generate_gemini_reply(system_prompt, user_input, image_path)
        else:
            return self._generate_openai_reply(system_prompt, user_input, image_path)