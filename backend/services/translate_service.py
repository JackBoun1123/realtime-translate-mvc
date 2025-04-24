import os
import ctranslate2

# Load một lần khi khởi server
translator = None

def get_translator():
    global translator
    if translator is None:
        # Get absolute path to the model directory
        dir_base = os.path.dirname(os.path.dirname(__file__))
        model_path = os.path.join(dir_base, "ctranslate2_models", "opus-mt-en-vi-int8")
        
        print(f"Loading translation model from: {model_path}")
        if not os.path.isdir(model_path):
            print(f"WARNING: Translation model directory not found: {model_path}")
            print(f"Files in ctranslate2_models: {os.listdir(os.path.join(dir_base, 'ctranslate2_models'))}")
            return None
            
        try:
            translator = ctranslate2.Translator(
                model_path,
                device="cpu",
                compute_type="int8"
            )
            print("Translation model loaded successfully")
        except Exception as e:
            print(f"Error loading translation model: {e}")
            return None
    return translator

async def translate(text: str, target_lang: str) -> str:
    """
    Args:
        text (str): The text to be translated.
        target_lang (str): The target language code (e.g., 'vi' for Vietnamese).

    Returns:
        str: The translated text.
    """
    # Validate input text
    if not isinstance(text, str) or not text.strip():
        return ""
        
    print(f"Translating text: '{text}'")
    
    # Bỏ qua khi không có gì để dịch
    if not text.strip():
        return ""

    # Đóng gói thành List[List[str]]
    translator_instance = get_translator()
    if translator_instance is None:
        print("Warning: Translator not available")
        return f"[TRANSLATION ERROR: Model not loaded] {text}"
        
    try:
        results = translator_instance.translate_batch(
            [[text]],
            max_batch_size=1,
            beam_size=1,
        )
        if results and results[0].hypotheses:
            result = results[0].hypotheses[0]
            print(f"Translation result: '{result}'")
            return result
        else:
            print("No translation results returned")
            return ""
    except Exception as e:
        print(f"Translation error: {e}")
        return f"[ERROR: {str(e)}] {text}"