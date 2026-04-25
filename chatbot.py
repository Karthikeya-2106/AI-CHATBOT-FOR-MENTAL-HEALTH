import os
from dotenv import load_dotenv
from keywords import check_crisis, HELPLINE, get_specialist

load_dotenv()

SYSTEM_PROMPT = """You are a compassionate AI health and mental wellness assistant.
Rules:
- Always respond with empathy and warmth
- Never diagnose definitively — always say 'this may be' or 'consult a doctor'
- Keep responses clear and helpful (3-5 sentences)
- For mental health: ask one follow-up question
- For physical symptoms or disease images: describe what you observe, possible condition, and recommend the right specialist
- For medicine images or names: give usage, common dosage info, side effects, and warn to consult a doctor before use"""

# In-memory chat history (resets when server restarts)
conversation_history = []


def _get_client():
    """Create a Gemini client using the API key from .env."""
    from google import genai
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY missing in .env")
    return genai.Client(api_key=api_key)


def get_response(user_message, image_path=None):
    # Crisis keywords short-circuit and return helpline immediately
    if check_crisis(user_message):
        return HELPLINE

    try:
        from google.genai import types
        client = _get_client()

        if image_path:
            # ---- Vision: analyze disease or medicine image ----
            with open(image_path, "rb") as f:
                image_bytes = f.read()

            ext = image_path.rsplit(".", 1)[-1].lower()
            mime_map = {
                "png": "image/png",
                "jpg": "image/jpeg",
                "jpeg": "image/jpeg",
                "webp": "image/webp",
                "gif": "image/gif",
            }
            mime_type = mime_map.get(ext, "image/jpeg")

            prompt_text = user_message if user_message else (
                "Analyze this image. If it shows a disease or skin condition, "
                "describe what you observe and suggest the appropriate specialist. "
                "If it shows a medicine/tablet/packaging, give medicine name, usage, "
                "dosage info and side effects."
            )

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                    prompt_text,
                ],
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    max_output_tokens=400,
                ),
            )
            return response.text

        # ---- Text-only chat ----
        conversation_history.append({"role": "user", "content": user_message})

        # Convert history to Gemini's expected format
        # Gemini uses 'user' and 'model' roles (not 'assistant')
        contents = []
        for msg in conversation_history[-6:]:
            role = "model" if msg["role"] == "assistant" else "user"
            contents.append(
                types.Content(role=role, parts=[types.Part(text=msg["content"])])
            )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                max_output_tokens=300,
            ),
        )

        reply = response.text
        conversation_history.append({"role": "assistant", "content": reply})
        return reply

    except Exception as e:
        # Print real error to terminal so you can debug
        print(f"❌ Gemini API error: {e}")

        text = user_message.lower() if user_message else ""

        if image_path:
            return ("I couldn't analyze the image right now. Please make sure your "
                    "GEMINI_API_KEY is set correctly in the .env file. For now, "
                    "describe your symptoms in text and I'll help you.")

        # Offline keyword-based fallbacks
        if any(w in text for w in ["vomit", "nausea", "sick", "stomach", "pain", "headache", "fever"]):
            return "I understand you're feeling physically unwell. For physical symptoms like these, I'd recommend seeing a doctor soon. In the meantime, stay hydrated and rest. How long have you been experiencing this?"
        elif any(w in text for w in ["sleep", "sleepy", "tired", "exhausted", "insomnia", "fatigue"]):
            return "Poor sleep deeply affects both physical and mental health. Try maintaining a consistent sleep schedule and limit screen time before bed. Are you having trouble falling asleep or staying asleep?"
        elif any(w in text for w in ["sad", "depressed", "crying", "unhappy", "lonely", "empty"]):
            return "I hear you, and I'm really glad you shared that with me. Feeling sad is valid — you don't have to carry this alone. What's been weighing on you the most lately?"
        elif any(w in text for w in ["anxious", "anxiety", "panic", "worried", "scared", "stress", "overwhelmed"]):
            return "Anxiety can feel so overwhelming. Take a slow breath — you're safe right now. What's been triggering these feelings for you?"
        elif any(w in text for w in ["angry", "frustrated", "irritated", "mad", "rage"]):
            return "It sounds like you're dealing with a lot of frustration. That's completely valid. Would you like to talk about what's been making you feel this way?"
        elif any(w in text for w in ["medicine", "tablet", "drug", "pill", "dose", "paracetamol", "ibuprofen"]):
            return "For medicine information, please consult a licensed pharmacist or doctor. Never self-medicate without professional advice. Can you describe your symptoms instead so I can suggest the right specialist?"
        else:
            return "Thank you for sharing that with me. I'm here to listen without any judgment. Can you tell me a little more about how you've been feeling?"


def get_medicine_info(medicine_name):
    try:
        from google.genai import types
        client = _get_client()

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"Give me information about the medicine: {medicine_name}",
            config=types.GenerateContentConfig(
                system_instruction=(
                    "You are a medical information assistant. Give clear info about "
                    "medicines: what it's used for, typical dosage, common side effects, "
                    "and always end with 'Please consult a doctor before use.'"
                ),
                max_output_tokens=300,
            ),
        )
        return response.text

    except Exception as e:
        print(f"❌ Gemini API error: {e}")
        common = {
            "paracetamol": "Paracetamol is used to relieve mild to moderate pain and reduce fever. Typical adult dose: 500mg-1g every 4-6 hours (max 4g/day). Side effects: rare at normal doses, but overdose can cause liver damage. Please consult a doctor before use.",
            "ibuprofen": "Ibuprofen is an anti-inflammatory used for pain, fever, and inflammation. Typical adult dose: 200-400mg every 4-6 hours with food. Side effects: stomach irritation, avoid if you have kidney issues. Please consult a doctor before use.",
            "amoxicillin": "Amoxicillin is an antibiotic for bacterial infections. Dose varies by condition — typically 250-500mg every 8 hours. Side effects: nausea, rash, diarrhea. Never take antibiotics without a prescription. Please consult a doctor before use.",
        }
        for key, val in common.items():
            if key in medicine_name.lower():
                return val
        return f"I don't have offline info for '{medicine_name}'. Please consult a pharmacist or check your GEMINI_API_KEY in the .env file."