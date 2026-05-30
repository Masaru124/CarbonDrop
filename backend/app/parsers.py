from abc import ABC, abstractmethod
from typing import List, Dict, Any
import ast
import base64
import json
import os
from pathlib import Path
from urllib import request, error

from .ocr import extract_items_from_image, extract_order_summary_items_from_image, preprocess_image_bytes, _is_plausible_item_name
from .document_classifier import DocumentType, classify_document_from_image
import re
import pytesseract
from PIL import Image
import io
from dotenv import load_dotenv


PARSE_PROMPT = """
You are a receipt and order parsing assistant.
Extract all purchased items from the image and return only valid JSON in this exact format:
{
  "merchant": "merchant name or app name",
  "merchant_type": "grocery|restaurant|ecommerce|fuel|utility|other",
  "date": "YYYY-MM-DD or null",
  "currency": "INR",
  "items": [
    {
      "name": "exact item name as shown",
      "quantity": 1,
      "unit": "kg|g|L|ml|item|portion|km|kWh",
      "price": 0.0,
      "inferred_category": "food_grain|food_dairy|food_meat|food_beverage|food_snack|restaurant_meal|transport|household|apparel|electronics|energy|other"
    }
  ],
  "total_amount": 0.0,
  "parse_confidence": "high|medium|low"
}
Rules:
- Return only JSON. Do not wrap it in markdown or add any commentary.
- Include only purchased product line items.
- Exclude totals, subtotals, discounts, taxes, tips, delivery/handling fees, order metadata, and free gifts.
If you cannot extract items, return {"error": "reason"}.
"""

NON_ITEM_PHRASES = {
        "total",
        "subtotal",
        "sub total",
        "tax",
        "vat",
        "gst",
        "tip",
        "service charge",
        "handling charge",
        "delivery charge",
        "delivery charges",
        "discount",
        "coupon",
        "promo",
        "order id",
        "order number",
        "bill total",
        "mrp",
        "free gift",
        "gift",
        "wallet",
        "refund",
}

BLINKIT_MARKER_GROUPS = [
    {"order summary", "download invoice", "bill details"},
    {"items in this order", "repeat order", "how were your ordered items?"},
    {"arrived at", "paid online", "deliver to"},
]

BLINKIT_SECTION_STARTS = {
    "items in this order",
    "2 items in this order",
    "1 item in this order",
    "ordered items",
}

BLINKIT_SECTION_ENDS = {
    "bill details",
    "order details",
    "how were your ordered items?",
    "repeat order",
}

BLINKIT_SECTION_GUARDS = {
    "order summary",
    "download invoice",
    "bill details",
    "order details",
    "repeat order",
    "how were your ordered items?",
    "deliver to",
    "payment",
    "mrp",
    "handling charge",
    "delivery charges",
    "product discount",
    "bill total",
    "item total",
}


def _clean_json_response(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _fallback_document_type(parsed: dict, image_bytes: bytes) -> DocumentType:
    merchant_type = str(parsed.get("merchant_type", "")).lower()
    if merchant_type == "restaurant":
        return DocumentType.RESTAURANT
    if merchant_type == "utility":
        return DocumentType.UTILITY
    if merchant_type == "transport":
        return DocumentType.TRANSPORT

    return classify_document_from_image(image_bytes)


def _sanitize_item_record(item: Any, default_category: str = "other") -> Dict[str, Any] | None:
    if not isinstance(item, dict):
        return None

    name = str(item.get("name", "")).strip()
    if not name or not _is_plausible_item_name(name):
        return None

    category = str(item.get("category") or default_category or "other").strip().lower()
    qty = item.get("qty", 1)
    unit = str(item.get("unit", "item") or "item").strip() or "item"
    price = item.get("price", 0)

    try:
        qty = float(qty)
    except (TypeError, ValueError):
        qty = 1.0

    try:
        price = float(price)
    except (TypeError, ValueError):
        price = 0.0

    return {
        "name": name,
        "qty": qty,
        "category": category,
        "unit": unit,
        "price": price,
        "raw_line": str(item.get("raw_line", name)),
    }


class OllamaDocumentParser:
    def __init__(self):
        self._env_path = Path(__file__).resolve().parent.parent / ".env"

    def _refresh_config(self):
        load_dotenv(self._env_path, override=True)
        self.base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434").strip().rstrip("/")
        self.model = os.environ.get("OLLAMA_MODEL", "llama3.1:8b").strip()
        self.timeout_seconds = float(os.environ.get("OLLAMA_TIMEOUT_SECONDS", "60").strip())
        # Allow overriding the API paths in case your Ollama install uses a different route
        self.generate_path = os.environ.get("OLLAMA_GENERATE_PATH", "/api/generate").strip() or "/api/generate"
        self.chat_path = os.environ.get("OLLAMA_CHAT_PATH", "/api/chat").strip() or "/api/chat"
        self.health_path = os.environ.get("OLLAMA_HEALTH_PATH", "/api/status").strip() or "/api/status"
        self.use_images = os.environ.get("OLLAMA_USE_IMAGES", "false").strip().lower() in {"1", "true", "yes", "on"}

    def parse_document(self, image_bytes: bytes) -> dict:
        self._refresh_config()
        ocr_text = self._extract_ocr_text(image_bytes)
        blinkit_mode = self._looks_like_blinkit_receipt(ocr_text)
        if not blinkit_mode and self.use_images:
            blinkit_mode = self._vision_detects_blinkit(image_bytes)

        if blinkit_mode:
            blinkit_candidates = self._extract_blinkit_candidates_from_ocr_text(ocr_text)
            if not blinkit_candidates:
                blinkit_candidates = self._extract_blinkit_candidates_from_layout(image_bytes)
            vision_candidates = self._parse_blinkit_with_vision(image_bytes, blinkit_candidates)
            if vision_candidates:
                blinkit_candidates = vision_candidates
            if blinkit_candidates:
                items = []
                seen_item_keys = set()
                for candidate in blinkit_candidates:
                    candidate_name = self._normalize_item_name(candidate)
                    if self._looks_like_garbage_item_name(candidate_name):
                        continue
                    item_key = self._item_key(candidate_name)
                    if item_key in seen_item_keys:
                        continue
                    seen_item_keys.add(item_key)
                    items.append(
                        {
                            "name": candidate_name,
                            "qty": 1.0,
                            "unit": "item",
                            "price": 0.0,
                            "category": self._infer_category_from_name(candidate_name),
                            "raw_line": candidate_name,
                        }
                    )

                if items:
                    return {
                        "document_type": DocumentType.GROCERY.value,
                        "items": items,
                        "merchant": "Blinkit",
                        "merchant_type": "ecommerce",
                        "total_amount": None,
                        "parse_confidence": "high" if len(items) >= 2 else "medium",
                        "parser_used": "BlinkitVisionParser",
                    }

        fallback_candidates = self._build_fallback_candidates(image_bytes)
        if self.use_images:
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": self._build_prompt(ocr_text),
                        "images": [base64.b64encode(image_bytes).decode("utf-8")],
                    }
                ],
                "stream": False,
                "format": "json",
            }
            response_text = self._post_json_with_failover(payload, prefer_chat=True)
        else:
            payload = {
                "model": self.model,
                "prompt": self._build_prompt(ocr_text),
                "stream": False,
                "format": "json",
            }
            response_text = self._post_json_with_failover(payload, prefer_chat=False)

        try:
            response = json.loads(response_text)
            if self.use_images:
                text = self._extract_chat_content(response)
            else:
                text = response.get("response", "") if isinstance(response, dict) else str(response)
            parsed = self._parse_model_json(text)
            if not isinstance(parsed, dict):
                raise ValueError("model returned a non-object JSON payload")
        except Exception as exc:
            print(f"[Ollama parser fallback] {exc}")
            return self._fallback_parse(image_bytes, error_message=str(exc))

        if parsed.get("error"):
            return self._fallback_parse(image_bytes, error_message=str(parsed.get("error")))

        document_type = _fallback_document_type(parsed, image_bytes)
        items = []
        fallback_index = 0
        for item in parsed.get("items", []):
            if not isinstance(item, dict):
                continue
            name = self._normalize_item_name(str(item.get("name", "")))
            if self._looks_like_garbage_item_name(name):
                replacement = self._next_fallback_name(fallback_candidates, fallback_index)
                if replacement:
                    name = replacement
                    fallback_index += 1
            if self._should_skip_item(name, item.get("price"), item.get("inferred_category")):
                continue
            items.append(
                {
                    "name": name,
                    "qty": self._safe_float(item.get("quantity", 1), 1.0),
                    "unit": str(item.get("unit", "item")).strip() or "item",
                    "price": self._safe_float(item.get("price", 0), 0.0),
                    "category": self._map_category(name, str(item.get("inferred_category", "other")).strip()),
                    "raw_line": name,
                }
            )

        return {
            "document_type": document_type.value,
            "items": items,
            "merchant": parsed.get("merchant"),
            "merchant_type": parsed.get("merchant_type"),
            "total_amount": parsed.get("total_amount"),
            "parse_confidence": parsed.get("parse_confidence", "medium"),
            "parser_used": "OllamaDocumentParser",
        }

    def _safe_float(self, value: Any, default: float) -> float:
        try:
            if value is None:
                return default
            return float(value)
        except (TypeError, ValueError):
            return default

    def _normalize_item_name(self, name: str) -> str:
        text = re.sub(r"\s+", " ", str(name)).strip()
        text = text.strip("-_,.:;()[]{}")
        text = re.sub(r"\b(?:x|qty|quantity)\s*\d+\b", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\b\d+(?:\.\d+)?\s*(?:g|kg|ml|l|pcs?|pieces?|units?|unit)\b", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s+", " ", text).strip("-_,.:;()[]{}")
        return text

    def _item_key(self, name: str) -> str:
        return re.sub(r"[^a-z0-9]+", "", str(name).lower())

    def _dedupe_candidates(self, candidates: List[str]) -> List[str]:
        deduped: List[str] = []
        seen = set()
        for candidate in candidates:
            normalized = self._normalize_item_name(candidate)
            key = self._item_key(normalized)
            if not key or key in seen:
                continue
            seen.add(key)
            deduped.append(normalized)
        return deduped

    def _looks_like_garbage_item_name(self, name: str) -> bool:
        lowered = re.sub(r"\s+", " ", str(name).lower()).strip()
        if not lowered:
            return True
        letters = len(re.findall(r"[a-z]", lowered))
        digits = len(re.findall(r"\d", lowered))
        if letters < 3:
            return True
        if digits > letters and len(lowered) < 12:
            return True
        if re.fullmatch(r"[a-z]\d+(?:\.\d+)?", lowered):
            return True
        if re.fullmatch(r"[a-z0-9\s,.'()\-]+", lowered) and letters <= 4 and digits >= 2:
            return True
        return False

    def _build_fallback_candidates(self, image_bytes: bytes) -> List[str]:
        candidates: List[str] = []
        for item in extract_items_from_image(image_bytes):
            name = self._normalize_item_name(str(item.get("name", "")))
            if self._looks_like_garbage_item_name(name):
                continue
            if self._should_skip_item(name, item.get("price"), item.get("category")):
                continue
            candidates.append(name)
        return candidates

    def _looks_like_blinkit_receipt(self, ocr_text: str) -> bool:
        lowered = re.sub(r"\s+", " ", str(ocr_text).lower())
        if "order summary" in lowered:
            return True
        if "items in this order" in lowered or "repeat order" in lowered:
            return True

        score = 0
        for group in BLINKIT_MARKER_GROUPS:
            if any(marker in lowered for marker in group):
                score += 1
        return score >= 2 or ("bill details" in lowered and "order details" in lowered)

    def _vision_detects_blinkit(self, image_bytes: bytes) -> bool:
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "Answer with JSON only: {\"is_blinkit\": true/false}. "
                        "Is this a Blinkit order summary screen with product cards and bill details? "
                        "Treat the screenshot as Blinkit if it shows order summary, item cards, bill details, or repeat order."
                    ),
                    "images": [base64.b64encode(image_bytes).decode("utf-8")],
                }
            ],
            "stream": False,
            "format": "json",
        }

        try:
            response_text = self._post_json_with_failover(payload, prefer_chat=True)
            response = json.loads(response_text)
            content = self._extract_chat_content(response)
            parsed = self._parse_model_json(content)
            return bool(parsed.get("is_blinkit"))
        except Exception:
            return False

    def _parse_blinkit_with_vision(self, image_bytes: bytes, supported_candidates: List[str]) -> List[str]:
        prompt = (
            "You are reading a Blinkit order summary screenshot. "
            "Return JSON only in this exact format: {\"items\":[{\"name\":\"...\",\"quantity\":1,\"unit\":\"item\"}]}. "
            "Use only the product cards. Extract every visible item card. "
            "Ignore order summary, bill details, totals, delivery info, buttons, free gifts, and any other chrome. "
            "Do not merge multiple products into one name. Do not invent products. "
            f"Only return items that match one of these visible candidates: {supported_candidates}."
        )

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                    "images": [base64.b64encode(image_bytes).decode("utf-8")],
                }
            ],
            "stream": False,
            "format": "json",
        }

        try:
            response_text = self._post_json_with_failover(payload, prefer_chat=True)
            response = json.loads(response_text)
            content = self._extract_chat_content(response)
            parsed = self._parse_model_json(content)
        except Exception:
            return []

        extracted: List[str] = []
        seen = set()
        for item in parsed.get("items", []):
            if not isinstance(item, dict):
                continue
            name = self._normalize_item_name(str(item.get("name", "")))
            if self._looks_like_garbage_item_name(name):
                continue
            if not self._blinkit_item_supported(name, supported_candidates):
                continue
            if self._should_skip_item(name, item.get("price"), item.get("category")):
                continue
            key = self._item_key(name)
            if key in seen:
                continue
            seen.add(key)
            extracted.append(name)

        return extracted

    def _extract_blinkit_candidates_from_ocr_text(self, ocr_text: str) -> List[str]:
        text = re.sub(r"\r", "\n", ocr_text)
        lines = [re.sub(r"\s+", " ", line).strip(" -_,.:;()[]{}") for line in text.splitlines()]
        candidates: List[str] = []
        for index, line in enumerate(lines):
            lowered = line.lower()
            if not self._looks_like_blinkit_title_line(line):
                continue

            window = " ".join(lines[index : min(len(lines), index + 3)])
            lowered_window = window.lower()
            if not (
                self._looks_like_blinkit_quantity_line(lowered_window)
                or self._looks_like_blinkit_price_line(lowered_window)
                or re.search(r"\b\d+\s*x\s*\d+\b", lowered_window)
            ):
                continue

            candidate = self._normalize_item_name(line)
            if self._is_blinkit_item_candidate(candidate):
                candidates.append(candidate)

        return self._dedupe_candidates(candidates)

    def _blinkit_item_supported(self, name: str, supported_candidates: List[str]) -> bool:
        if not supported_candidates:
            return False

        normalized_name = self._item_key(self._normalize_item_name(name))
        name_tokens = {token for token in re.findall(r"[a-z]+", name.lower()) if len(token) >= 3}
        for candidate in supported_candidates:
            candidate_name = self._normalize_item_name(candidate)
            candidate_key = self._item_key(candidate_name)
            if not candidate_key:
                continue
            if normalized_name == candidate_key:
                return True
            if normalized_name in candidate_key or candidate_key in normalized_name:
                return True
            candidate_tokens = {token for token in re.findall(r"[a-z]+", candidate_name.lower()) if len(token) >= 3}
            if name_tokens and candidate_tokens and len(name_tokens & candidate_tokens) >= 2:
                return True

        return False

    def _extract_blinkit_candidates_from_layout(self, image_bytes: bytes) -> List[str]:
        candidates: List[str] = []
        for config in ("--oem 3 --psm 6", "--oem 3 --psm 11", "--oem 3 --psm 4"):
            try:
                image = preprocess_image_bytes(image_bytes)
                lines = [re.sub(r"\s+", " ", line).strip(" -_,.:;()[]{}") for line in _reconstruct_lines_enhanced(image, config, "eng")]
            except Exception:
                continue

            if not lines:
                continue

            start_index = None
            end_index = None
            for index, line in enumerate(lines):
                lowered = line.lower()
                if start_index is None and any(marker in lowered for marker in BLINKIT_SECTION_STARTS):
                    start_index = index + 1
                    continue
                if start_index is not None and any(marker in lowered for marker in BLINKIT_SECTION_ENDS):
                    end_index = index
                    break

            if start_index is None:
                start_index = 0

            section_lines = lines[start_index:end_index] if end_index is not None else lines[start_index:]
            buffer: List[str] = []

            def flush_buffer() -> None:
                nonlocal buffer
                if not buffer:
                    return
                candidate = self._normalize_item_name(" ".join(buffer))
                if self._is_blinkit_item_candidate(candidate):
                    candidates.append(candidate)
                buffer = []

            for line in section_lines:
                lowered = line.lower().strip()
                if not lowered:
                    flush_buffer()
                    continue

                if any(phrase in lowered for phrase in BLINKIT_SECTION_GUARDS):
                    flush_buffer()
                    continue

                if self._looks_like_blinkit_quantity_line(lowered) or self._looks_like_blinkit_price_line(lowered):
                    flush_buffer()
                    continue

                if self._looks_like_blinkit_title_line(line):
                    buffer.append(line)
                    continue

                flush_buffer()

            flush_buffer()

        return self._dedupe_candidates(candidates)

    def _looks_like_blinkit_title_line(self, line: str) -> bool:
        lowered = re.sub(r"\s+", " ", str(line).lower()).strip()
        if not lowered:
            return False
        if any(phrase in lowered for phrase in NON_ITEM_PHRASES):
            return False
        if re.search(r"\b(?:order|summary|invoice|bill|details|repeat|deliver|payment|mrp|discount|charge|total)\b", lowered):
            return False
        if len(lowered.split()) < 2:
            return False
        if len(re.findall(r"[a-z]", lowered)) < 6:
            return False
        return True

    def _looks_like_blinkit_quantity_line(self, line: str) -> bool:
        lowered = re.sub(r"\s+", " ", str(line).lower()).strip()
        patterns = [
            r"^\d+(?:\.\d+)?\s*(?:g|kg|ml|l)\s*x\s*\d+$",
            r"^\d+\s*(?:unit|units|item|items|pcs|piece|pieces)\s*x\s*\d+$",
            r"^\d+\s*x\s*\d+$",
            r"^\d+(?:\.\d+)?\s*(?:g|kg|ml|l|unit|units|item|items|pcs|piece|pieces)?$",
        ]
        return any(re.fullmatch(pattern, lowered) for pattern in patterns)

    def _looks_like_blinkit_price_line(self, line: str) -> bool:
        lowered = re.sub(r"\s+", " ", str(line).lower()).strip()
        return bool(re.fullmatch(r"(?:₹|rs\.?|inr)?\s*\d+(?:\.\d{1,2})?", lowered))

    def _is_blinkit_item_candidate(self, line: str) -> bool:
        lowered = re.sub(r"\s+", " ", str(line).lower()).strip()
        if not lowered:
            return False
        if any(phrase in lowered for phrase in BLINKIT_SECTION_GUARDS):
            return False
        if any(phrase in lowered for phrase in NON_ITEM_PHRASES):
            return False
        if self._looks_like_garbage_item_name(lowered):
            return False
        if len(lowered.split()) > 14:
            return False
        if len(re.findall(r"[a-z]", lowered)) < 5:
            return False
        return True

    def _next_fallback_name(self, candidates: List[str], start_index: int) -> str | None:
        for index in range(start_index, len(candidates)):
            candidate = self._normalize_item_name(candidates[index])
            if not self._looks_like_garbage_item_name(candidate):
                return candidate
        return None

    def _map_category(self, name: str, category: str) -> str:
        category = category.lower()
        lowered_name = name.lower().strip()
        if self._should_skip_item(lowered_name, None, category):
            return "other"
        if category in {"transport", "energy", "utility"}:
            return category
        if category in {"apparel", "electronics", "household"}:
            return category
        name_category = self._infer_category_from_name(lowered_name)
        if name_category != "food":
            return name_category
        return "food"

    def _infer_category_from_name(self, name: str) -> str:
        lowered = name.lower()
        if any(token in lowered for token in {"toy", "plush", "soft toy", "doll", "stuffed", "game"}):
            return "household"
        if any(token in lowered for token in {"phone", "charger", "cable", "earbud", "headphone", "speaker", "mouse", "keyboard"}):
            return "electronics"
        if any(token in lowered for token in {"soap", "shampoo", "detergent", "cleaner", "bag", "bottle", "container"}):
            return "household"
        if any(token in lowered for token in {"chocolate", "momo", "momos", "paneer", "snack", "cake", "milk", "bread", "rice", "tea", "coffee"}):
            return "food"
        return "food"

    def _should_skip_item(self, name: str, price: Any, category: Any) -> bool:
        lowered = re.sub(r"\s+", " ", str(name).lower()).strip()
        if not lowered:
            return True

        compact = re.sub(r"[^a-z0-9]+", "", lowered)
        if len(compact) < 3:
            return True

        if re.fullmatch(r"x\s*s", lowered) or re.fullmatch(r"x\s*\w", lowered):
            return True

        if any(phrase in lowered for phrase in NON_ITEM_PHRASES):
            return True

        if isinstance(price, (int, float)) and float(price) <= 0 and any(token in lowered for token in {"free gift", "gift", "complimentary", "sample"}):
            return True

        if str(category).lower() in {"other", "charge", "fee", "discount", "meta", "summary"} and any(
            token in lowered for token in {"charge", "fee", "discount", "tax", "tip", "delivery", "subtotal", "total"}
        ):
            return True

        return False

    def _extract_json_block(self, text: str) -> str:
        cleaned = _clean_json_response(text)
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1 and end > start:
            return cleaned[start : end + 1]
        return cleaned

    def _repair_json_like_text(self, text: str) -> str:
        repaired = text.strip()
        repaired = re.sub(r",\s*([}\]])", r"\1", repaired)
        repaired = re.sub(
            r'([\{,]\s*)([A-Za-z_][A-Za-z0-9_\- ]*)(\s*:)',
            lambda match: f'{match.group(1)}"{match.group(2).strip()}"{match.group(3)}',
            repaired,
        )
        return repaired

    def _parse_model_json(self, text: str) -> dict:
        candidates = []
        extracted = self._extract_json_block(text)
        candidates.append(extracted)
        candidates.append(self._repair_json_like_text(extracted))
        candidates.append(re.sub(r"\bnull\b", "None", extracted, flags=re.IGNORECASE))
        candidates.append(re.sub(r"\btrue\b", "True", extracted, flags=re.IGNORECASE))
        candidates.append(re.sub(r"\bfalse\b", "False", extracted, flags=re.IGNORECASE))

        last_error: Exception | None = None
        for candidate in candidates:
            try:
                return json.loads(candidate)
            except Exception as exc:
                last_error = exc
                try:
                    value = ast.literal_eval(candidate)
                    if isinstance(value, dict):
                        return value
                except Exception:
                    continue

        raise ValueError(f"could not parse model JSON: {last_error}")

    def _fallback_parse(self, image_bytes: bytes, error_message: str | None = None) -> dict:
        fallback_items = extract_items_from_image(image_bytes)
        return {
            "document_type": classify_document_from_image(image_bytes).value,
            "items": fallback_items,
            "parser_used": "OCRFallbackParser",
            "parse_confidence": "low",
            "error": error_message,
        }

    def _extract_ocr_text(self, image_bytes: bytes) -> str:
        try:
            img = preprocess_image_bytes(image_bytes)
            text = pytesseract.image_to_string(img, lang="eng", config="--oem 3 --psm 6")
            return text.strip()
        except Exception:
            return ""

    def _extract_blinkit_candidates_from_layout(self, image_bytes: bytes) -> List[str]:
        try:
            image = preprocess_image_bytes(image_bytes)
            lines = [re.sub(r"\s+", " ", line).strip(" -_,.:;()[]{}") for line in _reconstruct_lines_enhanced(image, "--oem 3 --psm 6", "eng")]
        except Exception:
            return []

        if not lines:
            return []

        start_index = None
        end_index = None
        for index, line in enumerate(lines):
            lowered = line.lower()
            if start_index is None and any(marker in lowered for marker in BLINKIT_SECTION_STARTS):
                start_index = index + 1
                continue
            if start_index is not None and any(marker in lowered for marker in BLINKIT_SECTION_ENDS):
                end_index = index
                break

        if start_index is None:
            return []

        section_lines = lines[start_index:end_index] if end_index is not None else lines[start_index:]
        candidates: List[str] = []
        buffer: List[str] = []

        def flush_buffer() -> None:
            nonlocal buffer
            if not buffer:
                return
            candidate = self._normalize_item_name(" ".join(buffer))
            if self._is_blinkit_item_candidate(candidate):
                candidates.append(candidate)
            buffer = []

        for line in section_lines:
            lowered = line.lower().strip()
            if not lowered:
                flush_buffer()
                continue

            if any(phrase in lowered for phrase in BLINKIT_SECTION_GUARDS):
                flush_buffer()
                continue

            if self._looks_like_blinkit_quantity_line(lowered) or self._looks_like_blinkit_price_line(lowered):
                flush_buffer()
                continue

            if self._looks_like_blinkit_title_line(line):
                buffer.append(line)
                continue

            flush_buffer()

        flush_buffer()
        return self._dedupe_candidates(candidates)

    def _build_prompt(self, ocr_text: str) -> str:
        if not ocr_text:
            return PARSE_PROMPT

        return (
            f"{PARSE_PROMPT}\n\n"
            "OCR TEXT:\n"
            f"{ocr_text}\n\n"
            "Return only valid JSON in the requested schema."
        )

    def _extract_chat_content(self, response: dict) -> str:
        if not isinstance(response, dict):
            return str(response)

        message = response.get("message")
        if isinstance(message, dict):
            content = message.get("content", "")
            if content:
                return str(content)

        return str(response)

    def _post_json_with_failover(self, payload: dict, prefer_chat: bool) -> str:
        if prefer_chat:
            paths = [self.chat_path, "/api/chat", self.generate_path, "/api/generate", "/v1/chat", "/v1/generate"]
        else:
            paths = [self.generate_path, "/api/generate", self.chat_path, "/api/chat", "/v1/generate", "/v1/chat"]
        last_error: Exception | None = None

        for path in dict.fromkeys(paths):
            try:
                return self._post_json(path, payload)
            except error.HTTPError as exc:
                last_error = exc
                if exc.code != 404:
                    raise
            except Exception as exc:
                last_error = exc
                continue

        raise RuntimeError(
            f"failed to reach Ollama at {self.base_url} using paths {paths}: {last_error}"
        ) from last_error

    def _post_json(self, path: str, payload: dict) -> str:
        body = json.dumps(payload).encode("utf-8")
        req = request.Request(
            f"{self.base_url}{path}",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=self.timeout_seconds) as resp:
                return resp.read().decode("utf-8")
        except error.URLError as exc:
            raise RuntimeError(f"failed to reach Ollama at {self.base_url}: {exc}") from exc

class BaseParser(ABC):
    """Base class for all document parsers."""

    def __init__(self, document_type: DocumentType):
        self.document_type = document_type

    @abstractmethod
    def parse(self, image_bytes: bytes) -> List[Dict[str, Any]]:
        """Parse document and return list of items with quantities and metadata."""
        pass

    def preprocess_image(self, image_bytes: bytes) -> Image.Image:
        """Enhanced preprocessing for specific document types."""
        return preprocess_image_bytes(image_bytes)

class GroceryParser(BaseParser):
    """Parser for grocery receipts - extends existing OCR functionality."""

    def __init__(self):
        super().__init__(DocumentType.GROCERY)

    def parse(self, image_bytes: bytes) -> List[Dict[str, Any]]:
        """Parse grocery receipt using existing OCR logic."""
        items = [item for item in extract_items_from_image(image_bytes) if _is_plausible_item_name(item.get("name", ""))]
        if items:
            return items

        return [item for item in extract_order_summary_items_from_image(image_bytes) if _is_plausible_item_name(item.get("name", ""))]

class RestaurantParser(BaseParser):
    """Parser for restaurant receipts."""

    def __init__(self):
        super().__init__(DocumentType.RESTAURANT)

    def parse(self, image_bytes: bytes) -> List[Dict[str, Any]]:
        """Parse restaurant receipt with menu item recognition."""
        img = self.preprocess_image(image_bytes)
        text = pytesseract.image_to_string(img, lang='eng', config='--oem 3 --psm 6')
        return self._extract_restaurant_items(text)

    def _extract_restaurant_items(self, text: str) -> List[Dict[str, Any]]:
        """Extract menu items from restaurant receipt text."""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        items = []

        # Restaurant-specific patterns
        menu_patterns = [
            (r'(.+?)\s+\$?(\d+\.?\d{0,2})', 'menu_item'),
            (r'(.+?)\s+(\d+\.?\d{0,2})\s*(?:ea|each)?', 'item_price'),
        ]

        for line in lines:
            line = line.lower().strip()

            # Skip non-item lines
            if any(skip in line for skip in ['total', 'subtotal', 'tax', 'tip', 'change', 'card', 'cash']):
                continue

            for pattern, pattern_type in menu_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    item_name = match.group(1).strip()
                    try:
                        price = float(match.group(2))
                        items.append({
                            'name': self._clean_menu_item(item_name),
                            'qty': 1,
                            'price': price,
                            'raw_line': line,
                            'category': 'restaurant'
                        })
                    except ValueError:
                        continue
                    break

        return items

    def _clean_menu_item(self, item: str) -> str:
        """Clean and normalize menu item names."""
        # Remove common prefixes
        item = re.sub(r'^(small|large|medium|regular)\s+', '', item)
        item = re.sub(r'^\d+\.?\s*', '', item)  # Remove leading numbers

        # Common restaurant item corrections
        corrections = {
            'chk': 'chicken',
            'bf': 'beef',
            'veg': 'vegetable',
            'app': 'appetizer',
            'des': 'dessert',
            'bev': 'beverage'
        }

        for abbr, full in corrections.items():
            item = re.sub(r'\b' + abbr + r'\b', full, item, flags=re.IGNORECASE)

        return item.strip().capitalize()

class UtilityParser(BaseParser):
    """Parser for utility bills."""

    def __init__(self):
        super().__init__(DocumentType.UTILITY)

    def parse(self, image_bytes: bytes) -> List[Dict[str, Any]]:
        """Parse utility bill and extract consumption data."""
        img = self.preprocess_image(image_bytes)
        text = pytesseract.image_to_string(img, lang='eng', config='--oem 3 --psm 6')
        return self._extract_utility_items(text)

    def _extract_utility_items(self, text: str) -> List[Dict[str, Any]]:
        """Extract utility consumption data from bill text."""
        text = text.lower()
        items = []

        # Look for consumption patterns
        patterns = [
            (r'electric.*?(\d+\.?\d*)\s*(kwh|kw-h)', 'electricity_kwh'),
            (r'gas.*?(\d+\.?\d*)\s*(therms|cubic.?feet|ccf)', 'gas_therms'),
            (r'water.*?(\d+\.?\d*)\s*(gallons|liters|cubic.?meters)', 'water_volume'),
        ]

        for pattern, unit_type in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                try:
                    quantity = float(match[0])
                    unit = match[1]

                    items.append({
                        'name': unit_type.replace('_', ' ').title(),
                        'qty': quantity,
                        'unit': unit,
                        'price': 0,  # Will be calculated based on emission factors
                        'raw_line': match[0],
                        'category': 'utility'
                    })
                except (ValueError, IndexError):
                    continue

        # If no specific consumption found, look for total amount
        if not items:
            total_match = re.search(r'total.*?\$?(\d+\.?\d{0,2})', text, re.IGNORECASE)
            if total_match:
                items.append({
                    'name': 'Utility Bill',
                    'qty': 1,
                    'unit': 'bill',
                    'price': float(total_match.group(1)),
                    'raw_line': total_match.group(0),
                    'category': 'utility'
                })

        return items

class InvoiceParser(BaseParser):
    """Parser for general invoices."""

    def __init__(self):
        super().__init__(DocumentType.INVOICE)

    def parse(self, image_bytes: bytes) -> List[Dict[str, Any]]:
        """Parse invoice and extract line items."""
        img = self.preprocess_image(image_bytes)
        text = pytesseract.image_to_string(img, lang='eng', config='--oem 3 --psm 6')
        items = self._extract_invoice_items(text)
        if items:
            return items

        return self._extract_order_summary_items(image_bytes)

    def _extract_invoice_items(self, text: str) -> List[Dict[str, Any]]:
        """Extract items from invoice text."""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        items = []

        for line in lines:
            line = line.lower().strip()

            # Skip header/footer lines
            if any(skip in line for skip in ['invoice', 'total', 'subtotal', 'tax', 'payment', 'due date', 'bill to']):
                continue

            # Look for quantity, description, price pattern
            # Pattern: quantity description price
            qty_match = re.search(r'^(\d+)\s+(.+?)\s+\$?(\d+\.?\d{0,2})', line)
            if qty_match:
                try:
                    qty = int(qty_match.group(1))
                    desc = qty_match.group(2).strip()
                    price = float(qty_match.group(3))

                    if self._should_skip_invoice_line(line, desc):
                        continue

                    items.append({
                        'name': self._clean_description(desc),
                        'qty': qty,
                        'unit': 'item',
                        'price': price,
                        'raw_line': line,
                        'category': 'invoice'
                    })
                except (ValueError, IndexError):
                    continue

        return items

    def _extract_order_summary_items(self, image_bytes: bytes) -> List[Dict[str, Any]]:
        """Fallback parser for ecommerce / order-summary style receipts."""
        from .ocr import extract_items_from_image

        extracted = extract_items_from_image(image_bytes)
        items = []

        for item in extracted:
            name = str(item.get('name', '')).strip()
            if self._should_skip_invoice_line(item.get('raw_line', name), name):
                continue

            items.append({
                'name': self._clean_description(name),
                'qty': float(item.get('qty', 1) or 1),
                'unit': str(item.get('unit', 'item') or 'item'),
                'price': float(item.get('price', 0) or 0),
                'raw_line': item.get('raw_line', name),
                'category': self._infer_order_category(name),
            })

        return items

    def _should_skip_invoice_line(self, line: str, desc: str) -> bool:
        lowered = f"{line} {desc}".lower()
        skip_phrases = [
            'invoice', 'total', 'subtotal', 'sub total', 'tax', 'payment', 'due date', 'bill to',
            'handling charge', 'delivery charge', 'delivery charges', 'discount', 'coupon', 'promo',
            'free gift', 'gift', 'order id', 'order summary', 'view cart'
        ]
        return any(phrase in lowered for phrase in skip_phrases)

    def _infer_order_category(self, desc: str) -> str:
        lowered = desc.lower()
        food_keywords = [
            'chocolate', 'momo', 'momos', 'paneer', 'snack', 'chips', 'cookie', 'biscuit', 'cake',
            'bread', 'milk', 'butter', 'cheese', 'cream', 'ice cream', 'noodles', 'pasta', 'rice',
            'curry', 'sugar', 'tea', 'coffee', 'juice', 'drink', 'mango', 'banana', 'apple'
        ]
        household_keywords = [
            'toy', 'plush', 'soft toy', 'pillow', 'soap', 'shampoo', 'cleaner', 'detergent', 'bag'
        ]
        electronics_keywords = [
            'charger', 'cable', 'earbud', 'headphone', 'speaker', 'phone', 'mouse', 'keyboard'
        ]

        if any(keyword in lowered for keyword in food_keywords):
            return 'food'
        if any(keyword in lowered for keyword in electronics_keywords):
            return 'electronics'
        if any(keyword in lowered for keyword in household_keywords):
            return 'household'
        return 'goods'

    def _clean_description(self, desc: str) -> str:
        """Clean and normalize invoice item descriptions."""
        # Remove common prefixes
        desc = re.sub(r'^(item|product|service)\s*:?\s*', '', desc, flags=re.IGNORECASE)
        desc = re.sub(r'^\d+\.?\s*', '', desc)  # Remove leading numbers

        return desc.strip().capitalize()

class TransportParser(BaseParser):
    """Parser for transport receipts/tickets."""

    def __init__(self):
        super().__init__(DocumentType.TRANSPORT)

    def parse(self, image_bytes: bytes) -> List[Dict[str, Any]]:
        """Parse transport receipt and extract travel data."""
        img = self.preprocess_image(image_bytes)
        text = pytesseract.image_to_string(img, lang='eng', config='--oem 3 --psm 6')
        return self._extract_transport_items(text)

    def _extract_transport_items(self, text: str) -> List[Dict[str, Any]]:
        """Extract transport data from receipt text."""
        text = text.lower()
        items = []

        # Look for transport patterns
        patterns = [
            (r'flight.*?([A-Z]{2}\d+).*?([A-Z]{3}).*?([A-Z]{3})', 'flight_route'),
            (r'train.*?(\d+)\s*(km|kilometers?|miles?)', 'train_distance'),
            (r'bus.*?(\d+)\s*(km|kilometers?|miles?)', 'bus_distance'),
            (r'taxi.*?(\d+\.?\d*)\s*(km|kilometers?|miles?)', 'taxi_distance'),
            (r'fuel.*?(\d+\.?\d*)\s*(liters?|gallons?)', 'fuel_volume'),
        ]

        for pattern, item_type in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                if item_type == 'flight_route':
                    items.append({
                        'name': f'Flight {match[0]}: {match[1]}-{match[2]}',
                        'qty': 1,
                        'unit': 'flight',
                        'price': 0,
                        'raw_line': match[0],
                        'category': 'transport',
                        'metadata': {
                            'flight_number': match[0],
                            'from_airport': match[1],
                            'to_airport': match[2]
                        }
                    })
                else:
                    try:
                        distance = float(match[0])
                        unit = match[1]

                        items.append({
                            'name': item_type.replace('_', ' ').title(),
                            'qty': distance,
                            'unit': unit,
                            'price': 0,
                            'raw_line': match[0],
                            'category': 'transport'
                        })
                    except (ValueError, IndexError):
                        continue

        return items

class DocumentParser:
    """Main parser that routes documents to appropriate specialized parsers."""

    def __init__(self):
        self.ollama_parser = OllamaDocumentParser()
        self.parsers = {
            DocumentType.GROCERY: GroceryParser(),
            DocumentType.RESTAURANT: RestaurantParser(),
            DocumentType.UTILITY: UtilityParser(),
            DocumentType.INVOICE: InvoiceParser(),
            DocumentType.TRANSPORT: TransportParser()
        }

    def parse_document(self, image_bytes: bytes) -> Dict[str, Any]:
        """Parse document and return structured data with classification."""
        parsed = self.ollama_parser.parse_document(image_bytes)
        sanitized_items = [
            item for item in (
                _sanitize_item_record(raw_item, default_category=str(parsed.get("merchant_type") or parsed.get("document_type") or "other"))
                for raw_item in parsed.get("items", [])
            )
            if item is not None
        ]
        if sanitized_items:
            parsed["items"] = sanitized_items
            return parsed

        doc_type = classify_document_from_image(image_bytes)
        parser = self.parsers.get(doc_type, GroceryParser())
        items = [
            item for item in (
                _sanitize_item_record(raw_item, default_category=doc_type.value)
                for raw_item in parser.parse(image_bytes)
            )
            if item is not None
        ]

        return {
            'document_type': doc_type.value,
            'items': items,
            'parser_used': parser.__class__.__name__,
            'parse_confidence': 'low' if not items else 'medium'
        }

# Global parser instance
document_parser = DocumentParser()
