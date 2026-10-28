import re
from typing import Tuple, Optional, Dict, Any


def validate_and_normalize_phone(raw_phone: Optional[str]) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Validate and normalize phone numbers for Hawlwadaag School communications.
    Supports Somali mobile operators (Hormuud, Telesom, Golis, Somtel) and general international formats.

    Returns:
        (is_valid, normalized_phone_or_original, error_reason)
    """
    if not raw_phone or not raw_phone.strip():
        return False, None, "MISSING_CONTACT"

    cleaned = raw_phone.strip()
    # Remove spaces, hyphens, parenthesis, dots
    digits_only = re.sub(r"[\s\-\.\(\)]+", "", cleaned)

    # If starts with '+', keep '+' and strip other non-digit chars
    if digits_only.startswith("+"):
        clean_format = "+" + re.sub(r"\D", "", digits_only[1:])
    else:
        clean_format = re.sub(r"\D", "", digits_only)

    # Somali phone normalization:
    # Formats: 061XXXXXXX, 062XXXXXXX, 063XXXXXXX, 065XXXXXXX, 068XXXXXXX, 090XXXXXXX (9 digits)
    # Formats: 61XXXXXXX, 62XXXXXXX, 63XXXXXXX, 65XXXXXXX, 68XXXXXXX, 90XXXXXXX (8 digits)
    # Formats: 25261XXXXXXX (11 digits) or +25261XXXXXXX (12 chars)

    # Handle +252 prefix
    if clean_format.startswith("+252"):
        national = clean_format[4:]
        if len(national) in [8, 9] and national.isdigit():
            if national.startswith("0"):
                national = national[1:]
            return True, f"+252{national}", None

    # Handle 252 prefix without '+'
    if clean_format.startswith("252") and len(clean_format) in [11, 12]:
        national = clean_format[3:]
        if national.startswith("0"):
            national = national[1:]
        if len(national) in [7, 8, 9] and national.isdigit():
            return True, f"+252{national}", None

    # Handle local 06X / 090
    if clean_format.startswith("0") and len(clean_format) in [9, 10]:
        national = clean_format[1:]
        if len(national) in [7, 8, 9] and national.isdigit():
            return True, f"+252{national}", None

    # Handle local 61X, 62X, 63X, 65X, 68X, 90X (8 digits)
    if len(clean_format) == 8 and clean_format[0] in ["6", "9"] and clean_format.isdigit():
        return True, f"+252{clean_format}", None

    # Handle general international numbers with '+' (7 to 15 digits according to E.164)
    if clean_format.startswith("+"):
        num_part = clean_format[1:]
        if 7 <= len(num_part) <= 15 and num_part.isdigit():
            return True, clean_format, None

    # If numeric between 7 and 15 digits, accept with warning or prepend '+'
    if 7 <= len(clean_format) <= 15 and clean_format.isdigit():
        return True, f"+{clean_format}", None

    return False, raw_phone, "INVALID_CONTACT"


def calculate_sms_segments(message: str) -> Dict[str, Any]:
    """
    Calculate SMS length, character set, and required SMS segment count.
    GSM 7-bit: 160 chars per segment (153 for multi-segment).
    Unicode (UCS-2): 70 chars per segment (67 for multi-segment).
    """
    if not message:
        return {
            "char_count": 0,
            "encoding": "GSM-7",
            "segments": 1,
            "max_per_segment": 160
        }

    # Check for non-GSM characters (e.g., special unicode symbols, non-latin)
    # Standard GSM 7-bit basic character set
    gsm_chars = (
        "@£$¥èéùìòÇ\nØø\rÅåΔ_ΦΓΛΩΠΨΣΘΞ\x1bÆæßÉ !\"#¤%&'()*+,-./0123456789:;<=>?"
        "¡ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÑÜ`¿abcdefghijklmnopqrstuvwxyzäöñüà"
    )
    is_unicode = any(c not in gsm_chars for c in message)

    char_count = len(message)

    if not is_unicode:
        encoding = "GSM-7"
        if char_count <= 160:
            segments = 1
        else:
            segments = (char_count + 152) // 153
        max_per_segment = 160 if segments == 1 else 153
    else:
        encoding = "UCS-2 (Unicode)"
        if char_count <= 70:
            segments = 1
        else:
            segments = (char_count + 66) // 67
        max_per_segment = 70 if segments == 1 else 67

    return {
        "char_count": char_count,
        "encoding": encoding,
        "segments": segments,
        "max_per_segment": max_per_segment
    }
