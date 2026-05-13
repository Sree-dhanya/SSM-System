"""
Translation endpoint using Google Gemini API for all languages
Supports Malayalam, Hindi, Tamil, Telugu, Kannada, Bengali, Gujarati, Marathi, Punjabi, Odia
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.api.deps import get_current_user
from app.models.user import User
from app.core.config import settings
import logging
import time
import re

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize Gemini client (lazy-loaded)
_gemini_model = None


def _get_gemini_model():
    """Get or initialize the Gemini model client."""
    global _gemini_model
    
    if _gemini_model is None:
        try:
            import google.generativeai as genai
            
            if not settings.GEMINI_API_KEY:
                raise HTTPException(
                    status_code=503,
                    detail="GEMINI_API_KEY environment variable not set on server."
                )
            
            genai.configure(api_key=settings.GEMINI_API_KEY)
            _gemini_model = genai.GenerativeModel(settings.GEMINI_MODEL)
            logger.info(f"Gemini model '{settings.GEMINI_MODEL}' initialized successfully")
        except ImportError:
            raise HTTPException(
                status_code=503,
                detail="google-generativeai package not installed. Please install it with: pip install google-generativeai"
            )
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {e}")
            raise HTTPException(status_code=503, detail=f"Failed to initialize Gemini API: {str(e)}")
    
    return _gemini_model


# Standardized Malayalam terminology for clinical/therapy reporting
MALAYALAM_CLINICAL_TERM_MAP = {
    # Receptive Language
    "അനുഭവശേഷി": "ഗ്രഹണഭാഷാ കഴിവ്",
    "പതുക്കെ": "സാവധാനം",
    "സംസാരിക്കുന്ന ഭാഷ": "സംസാരഭാഷ",
    "മനസിലാക്കാൻ": "മനസ്സിലാക്കാൻ",
    "ഗ്രഹണ ഭാഷാ കഴിവ്": "ഗ്രഹണഭാഷാ കഴിവ്",
    "ഗ്രഹണ ഭാഷ": "ഗ്രഹണഭാഷ",
    "ഗ്രഹണ കഴിവ്": "ഗ്രഹണഭാഷാ കഴിവ്",
    "ധാരണ": "ഗ്രഹണശേഷി",
    
    # Visual cues
    "വിഷ്വൽ സൂചനകൾ": "ദൃശ്യ സൂചനകൾ",
    "വിഷ്വൽ സൂചന": "ദൃശ്യ സൂചന",
    "വിഷ്വല്‍ സൂചന": "ദൃശ്യ സൂചന",
    "വിഷ്വല്‍ സൂചനകൾ": "ദൃശ്യ സൂചനകൾ",
    "visual cues": "ദൃശ്യ സൂചനകൾ",
    
    # Repetition terminology
    "ആവർത്തിക്കേണ്ടിവന്നു": "ആവർത്തനം ആവശ്യമായി വന്നു",
    "കൂടുതൽ ആവർത്തിക്കലും": "കൂടുതൽ ആവർത്തനവും",
    
    # Comprehension variants
    "കമ്പ്രഹെൻഷൻ": "ഗ്രാഹ്യം",
    "comprehension": "ഗ്രാഹ്യം",
}


def _canonicalize_for_dedupe(text: str) -> str:
    """Create a loose canonical form so near-identical lines/sentences can be deduplicated."""
    lowered = text.lower().strip()
    lowered = re.sub(r"\s+", " ", lowered)
    lowered = re.sub(r"[\u200b\u200c\u200d]", "", lowered)
    lowered = re.sub(r"[^\w\u0d00-\u0d7f ]", "", lowered)
    return lowered.strip()


def _apply_malayalam_clinical_term_standardization(text: str) -> str:
    """Apply deterministic terminology replacement for consistent report wording."""
    normalized = text
    for source_term, target_term in sorted(MALAYALAM_CLINICAL_TERM_MAP.items(), key=lambda kv: len(kv[0]), reverse=True):
        normalized = normalized.replace(source_term, target_term)
    return normalized


def _validate_malayalam_translation(source_text: str, translated_text: str) -> str:
    """
    Validation layer only (no semantic rewriting):
    - Ensure non-empty output.
    - Remove exact duplicate lines.
    - Guard against excessive expansion beyond source scope.
    """
    if not translated_text:
        return translated_text

    cleaned = translated_text.strip()
    if not cleaned:
        return cleaned

    unique_lines = []
    seen_lines = set()
    for raw_line in cleaned.split("\n"):
        line = raw_line.strip()
        if not line:
            continue
        canonical = _canonicalize_for_dedupe(line)
        if canonical in seen_lines:
            continue
        seen_lines.add(canonical)
        unique_lines.append(line)

    validated = "\n".join(unique_lines).strip()

    source_sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", source_text.strip()) if s.strip()]
    translated_sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", validated.strip()) if s.strip()]

    if source_sentences:
        max_allowed = max(len(source_sentences) * 2, len(source_sentences) + 3)
        if len(translated_sentences) > max_allowed:
            validated = " ".join(translated_sentences[:max_allowed]).strip()

    return validated


def _postprocess_malayalam_clinical_text(source_text: str, translated_text: str) -> str:
    """
    Post-processing pipeline for Malayalam clinical text:
    1. Apply terminology standardization (locked glossary).
    2. Validate (deduplicate, scope check).
    """
    if not translated_text:
        return translated_text

    text = re.sub(r"[ \t]+", " ", translated_text)
    text = _apply_malayalam_clinical_term_standardization(text)
    return _validate_malayalam_translation(source_text, text)


# Translation request model
class TranslationRequest(BaseModel):
    text: str
    target_language: str
    source_language: str = "English"  # Default source is English

class TranslationResponse(BaseModel):
    translated_text: str
    source_language: str
    target_language: str


@router.post("/clear-translation-cache")
async def clear_translation_cache(current_user: User = Depends(get_current_user)):
    """Clear translation models cache - not needed for Gemini API but kept for compatibility"""
    global _gemini_model
    
    _gemini_model = None
    
    logger.info("Translation cache cleared")
    return {
        "status": "success",
        "message": "Translation models reinitialized. Using Gemini API for next request.",
        "model": settings.GEMINI_MODEL
    }


def _build_translation_prompt(text: str, target_language: str) -> str:
    """Build a precise prompt for Gemini to translate text."""
    language_names = {
        "mal_Mlym": "Malayalam",
        "hin_Deva": "Hindi",
        "tam_Tamil": "Tamil",
        "tel_Telu": "Telugu",
        "kan_Knda": "Kannada",
        "ben_Beng": "Bengali",
        "guj_Gujr": "Gujarati",
        "mar_Deva": "Marathi",
        "pan_Guru": "Punjabi",
        "ory_Orya": "Odia",
        "ml": "Malayalam",
        "hi": "Hindi",
        "ta": "Tamil",
        "te": "Telugu",
        "kn": "Kannada",
        "bn": "Bengali",
        "gu": "Gujarati",
        "mr": "Marathi",
        "pa": "Punjabi",
        "or": "Odia",
    }
    
    target_lang_name = language_names.get(target_language, target_language)
    
    # Special instructions for Malayalam clinical text
    if target_language in ["mal_Mlym", "ml"]:
        prompt = f"""Translate the following English text to {target_lang_name}. 

IMPORTANT INSTRUCTIONS:
1. Preserve all formatting (line breaks, bullet points, markdown syntax)
2. Use professional, clinical terminology appropriate for medical/therapy reports
3. Maintain the original meaning and structure
4. Keep technical terms consistent across the translation
5. Do not add explanations or commentary
6. Output ONLY the translated text, nothing else

TEXT TO TRANSLATE:
{text}

TRANSLATED TEXT IN {target_lang_name.upper()}:"""
    else:
        prompt = f"""Translate the following English text to {target_lang_name}.

IMPORTANT INSTRUCTIONS:
1. Preserve all formatting (line breaks, bullet points, markdown syntax)
2. Maintain the original meaning and structure
3. Output ONLY the translated text, nothing else

TEXT TO TRANSLATE:
{text}

TRANSLATED TEXT IN {target_lang_name.upper()}:"""
    
    return prompt


@router.post("/translate", response_model=TranslationResponse)
async def translate_text(
    request: TranslationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Translate text from English to Indian languages using Google Gemini API
    
    Supported language codes:
    - mal_Mlym or ml: Malayalam
    - hin_Deva or hi: Hindi
    - tam_Tamil or ta: Tamil
    - tel_Telu or te: Telugu
    - kan_Knda or kn: Kannada
    - ben_Beng or bn: Bengali
    - guj_Gujr or gu: Gujarati
    - mar_Deva or mr: Marathi
    - pan_Guru or pa: Punjabi
    - ory_Orya or or: Odia
    """
    try:
        start_time = time.time()
        logger.info(f"Translation request from user {current_user.username} to {request.target_language}")
        logger.info(f"Text length: {len(request.text)} characters")
        
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        # Validate text length
        if len(request.text) > 10000:
            logger.warning(f"Large text received: {len(request.text)} chars, truncating...")
            request.text = request.text[:10000]
        
        # Get Gemini model
        model = _get_gemini_model()
        
        # Build translation prompt
        prompt = _build_translation_prompt(request.text, request.target_language)
        
        # Call Gemini API
        logger.info(f"Calling Gemini API ({settings.GEMINI_MODEL}) for {request.target_language}")
        response = model.generate_content(
            prompt,
            generation_config={
                "max_output_tokens": 2000,
                "temperature": 0.3,  # Lower temperature for more consistent translations
            }
        )
        
        translated_text = response.text.strip()
        
        # Post-process Malayalam translations
        if request.target_language in ["mal_Mlym", "ml"]:
            translated_text = _postprocess_malayalam_clinical_text(request.text, translated_text)
        
        elapsed = time.time() - start_time
        logger.info(f"Translation completed in {elapsed:.2f}s")
        logger.info(f"Translated text preview: {translated_text[:100]}...")
        
        return TranslationResponse(
            translated_text=translated_text,
            source_language=request.source_language,
            target_language=request.target_language
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Translation error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Translation failed: {str(e)}"
        )
