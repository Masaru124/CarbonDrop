from abc import ABC, abstractmethod
from typing import List, Dict, Any
from .ocr import extract_items_from_image, preprocess_image_bytes
from .document_classifier import DocumentType, classify_document_from_image
import re
import pytesseract
from PIL import Image
import io

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
        return extract_items_from_image(image_bytes)

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
        return self._extract_invoice_items(text)

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
        self.parsers = {
            DocumentType.GROCERY: GroceryParser(),
            DocumentType.RESTAURANT: RestaurantParser(),
            DocumentType.UTILITY: UtilityParser(),
            DocumentType.INVOICE: InvoiceParser(),
            DocumentType.TRANSPORT: TransportParser()
        }

    def parse_document(self, image_bytes: bytes) -> Dict[str, Any]:
        """Parse document and return structured data with classification."""
        # Classify document type
        doc_type = classify_document_from_image(image_bytes)

        # Get appropriate parser
        parser = self.parsers.get(doc_type, GroceryParser())

        # Parse with specialized parser
        items = parser.parse(image_bytes)

        return {
            'document_type': doc_type.value,
            'items': items,
            'parser_used': parser.__class__.__name__
        }

# Global parser instance
document_parser = DocumentParser()
