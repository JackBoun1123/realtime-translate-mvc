import ctranslate2

# Load một lần khi khởi server
translator = None

def get_translator():
    global translator
    if translator is None:
        translator = ctranslate2.Translator(
            "ctranslate2_models/opus-mt-en-vi-int8",
            device="cpu",                # hoặc "cuda" nếu có GPU
            compute_type="int8"          # đảm bảo chạy quantized
        )
    return translator

async def translate(text: str, target_lang: str) -> str:
    # Validate input text
    if not isinstance(text, str) or not text.strip():
        return ""
    if len(text) > 1000:  # Example limit for excessively long text
        raise ValueError("Input text is too long to process.")
    """
    Args:
        text (str): The text to be translated.
        target_lang (str): The target language code (e.g., 'vi' for Vietnamese).

    Returns:
        str: The translated text.
    """
    # Bỏ qua khi không có gì để dịch
    if not text.strip():
        return ""

    # Đóng gói thành List[List[str]]
    translator_instance = get_translator()
    results = translator_instance.translate_batch(
        [[text]],
        max_batch_size=1,
        beam_size=1,
    )
    if results and results[0].hypotheses:
        return results[0].hypotheses[0]
    else:
        return ""

