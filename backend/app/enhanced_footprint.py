import pandas as pd
from rapidfuzz import process, fuzz
import os
import re

class EnhancedFootprintMatcher:
    """Enhanced footprint matcher that supports multiple domains and categories."""

    def __init__(self, dataset_df):
        self.df = dataset_df.copy()
        self.choices = list(self.df['item'])

        # Multi-domain emission factors
        self.category_factors = {
            # Transport factors (kg CO2e per unit)
            'transport': {
                'flight_km': 0.25,  # kg CO2e per km for short flights
                'train_km': 0.04,   # kg CO2e per km for train
                'bus_km': 0.08,     # kg CO2e per km for bus
                'car_km': 0.17,     # kg CO2e per km for average car
                'taxi_km': 0.17,    # kg CO2e per km for taxi
                'fuel_liter': 2.3,  # kg CO2e per liter of gasoline
                'electricity_kwh': 0.4,  # kg CO2e per kWh (average grid)
                'gas_therm': 5.3,   # kg CO2e per therm of natural gas
                'water_liter': 0.0003,  # kg CO2e per liter (treatment + supply)
            },
            # Utility factors
            'utility': {
                'electricity_kwh': 0.4,
                'gas_therm': 5.3,
                'water_cubic_meter': 0.3,
                'water_gallon': 0.0011,
            },
            # Energy factors
            'energy': {
                'electricity_kwh': 0.4,
                'gas_therm': 5.3,
                'fuel_oil_liter': 2.7,
            }
        }

    def match_and_compute(self, items):
        """Enhanced matching that considers item categories and units."""
        results = []
        total = 0.0

        for it in items:
            name = it.get('name', '').strip()
            qty = float(it.get('qty', 1) or 1)
            category = it.get('category', 'food')
            unit = it.get('unit', 'kg')

            # Try to match in the emission database first with multiple strategies
            match_result = self._find_best_match(name, category)

            if match_result and len(match_result) == 4:
                matched_name, score, idx, row = match_result
                # Ensure row is a pandas Series and get the co2 value
                try:
                    if isinstance(row, pd.Series):
                        co2_per_unit = float(row['co2'])
                    else:
                        # Fallback for unexpected types
                        co2_per_unit = float(row.get('co2', 0) if hasattr(row, 'get') else 0)
                except (TypeError, KeyError) as e:
                    print(f"Error accessing co2 value from row: {row}, type: {type(row)}, error: {e}")
                    # Skip this item if we can't get the co2 value
                    results.append({
                        'name': name,
                        'matched_name': None,
                        'match_score': 0,
                        'qty': qty,
                        'unit': unit,
                        'co2_per_unit': None,
                        'footprint': 0.0,
                        'category': category
                    })
                    continue
                item_category = category or 'food'

                # Calculate footprint based on quantity and unit
                footprint = self._calculate_footprint(qty, unit, co2_per_unit, item_category)

                results.append({
                    'name': name,
                    'matched_name': matched_name,
                    'match_score': int(score),
                    'qty': qty,
                    'unit': unit,
                    'co2_per_unit': co2_per_unit,
                    'footprint': footprint,
                    'category': item_category
                })
                total += footprint
            else:
                # Try category-specific matching
                footprint = self._calculate_category_footprint(name, qty, category, unit)
                if footprint > 0:
                    results.append({
                        'name': name,
                        'matched_name': f'{name} (category: {category})',
                        'match_score': 50,  # Lower confidence for category matching
                        'qty': qty,
                        'unit': unit,
                        'co2_per_unit': footprint / qty if qty > 0 else 0,
                        'footprint': footprint,
                        'category': category
                    })
                    total += footprint
                else:
                    # Enhanced fallback matching - try partial matches and common variations
                    fallback_match = self._find_fallback_match(name, category)
                    if fallback_match and len(fallback_match) == 4:
                        matched_name, score, idx, row = fallback_match
                        try:
                            if isinstance(row, pd.Series):
                                co2_per_unit = float(row['co2'])
                            else:
                                co2_per_unit = float(row.get('co2', 0) if hasattr(row, 'get') else 0)
                        except (TypeError, KeyError) as e:
                            print(f"Error accessing co2 value from fallback row: {row}, type: {type(row)}, error: {e}")
                            # Skip to unmatched case
                            results.append({
                                'name': name,
                                'matched_name': None,
                                'match_score': 0,
                                'qty': qty,
                                'unit': unit,
                                'co2_per_unit': None,
                                'footprint': 0.0,
                                'category': category
                            })
                            total += 0.0
                            continue
                        footprint = self._calculate_footprint(qty, unit, co2_per_unit, category)

                        results.append({
                            'name': name,
                            'matched_name': f'{matched_name} (fallback)',
                            'match_score': int(score),
                            'qty': qty,
                            'unit': unit,
                            'co2_per_unit': co2_per_unit,
                            'footprint': footprint,
                            'category': category
                        })
                        total += footprint
                    else:
                        results.append({
                            'name': name,
                            'matched_name': None,
                            'match_score': 0,
                            'qty': qty,
                            'unit': unit,
                            'co2_per_unit': None,
                            'footprint': 0.0,
                            'category': category
                        })

        return results, round(total, 4)

    def _find_best_match(self, name, category):
        """Find the best match using semantic and category-aware strategies."""
        # Strategy 1: Category-specific matching first (most important)
        if category != 'food':
            category_items = self.df[self.df['category'] == category]
            if not category_items.empty:
                # Try exact or near-exact matches in category
                best = process.extractOne(name, category_items['item'], scorer=fuzz.WRatio, score_cutoff=70)
                if best:
                    matched_name, score, idx = best
                    matched_rows = category_items[category_items['item'] == matched_name]
                    if not matched_rows.empty:
                        return matched_name, score, 0, matched_rows.iloc[0]

        # Strategy 2: Normalize and clean both search term and database items
        normalized_name = self._normalize_item_name(name)

        # Get potential matches from same category first
        if category != 'food':
            category_items = self.df[self.df['category'] == category]
            category_matches = self._find_matches_in_subset(normalized_name, category_items)
            if category_matches:
                return category_matches

        # Strategy 3: For food items, look for semantic matches
        food_items = self.df[self.df['category'] == 'food']
        food_matches = self._find_matches_in_subset(normalized_name, food_items)
        if food_matches:
            return food_matches

        # Strategy 4: Fallback to cross-category but with higher threshold
        all_matches = self._find_matches_in_subset(normalized_name, self.df, min_score=80)
        if all_matches:
            return all_matches

        return None

    def _normalize_item_name(self, name):
        """Normalize item name for better matching."""
        # Remove common prefixes and suffixes
        name = name.lower().strip()

        # Remove specific descriptors that make matching harder
        remove_patterns = [
            r',.*',  # Remove everything after comma (e.g., "milk, whole" -> "milk")
            r'\(.*\)',  # Remove parentheses content
            r' - .*',  # Remove dash content
            r' with .*',  # Remove "with" phrases
            r' and .*',  # Remove "and" phrases
        ]

        for pattern in remove_patterns:
            name = re.sub(pattern, '', name)

        # Clean up extra spaces
        name = re.sub(r'\s+', ' ', name).strip()

        return name

    def _find_matches_in_subset(self, search_term, subset_df, min_score=60):
        """Find matches within a subset of the database."""
        if subset_df.empty:
            return None

        choices = list(subset_df['item'])

        # Try multiple matching strategies
        strategies = [
            (fuzz.WRatio, min_score),
            (fuzz.token_sort_ratio, min_score + 10),  # Higher threshold for token sort
            (fuzz.partial_ratio, min_score + 15),     # Higher threshold for partial
        ]

        best_match = None
        best_score = 0

        for scorer, threshold in strategies:
            try:
                result = process.extractOne(search_term, choices, scorer=scorer, score_cutoff=threshold)
                if result:
                    matched_name, score, idx = result

                    # Additional validation: check if this makes semantic sense
                    if self._is_semantically_valid_match(search_term, matched_name, scorer.__name__ if hasattr(scorer, '__name__') else str(scorer)):
                        if score > best_score:
                            # Use idx to get the row from the original DataFrame
                            # idx is the index in the choices list, so we need to get it from subset_df
                            matched_rows = subset_df[subset_df['item'] == matched_name]
                            if not matched_rows.empty:
                                best_match = (matched_name, score, idx, matched_rows.iloc[0])
                                best_score = score
            except Exception as e:
                print(f"Error in matching strategy: {e}")
                continue

        return best_match if best_match and len(best_match) == 4 else None

    def _is_semantically_valid_match(self, search_term, matched_item, method):
        """Check if a match makes semantic sense."""
        search_lower = search_term.lower()
        matched_lower = matched_item.lower()

        # Same word matches are always valid
        if search_lower == matched_lower:
            return True

        # Check if search term is contained in matched item (good for specific -> general)
        if search_lower in matched_lower:
            return True

        # Check if matched item contains search term (good for general -> specific)
        if matched_lower in search_lower:
            return True

        # Check for common word overlaps (at least 60% of words should match)
        search_words = set(search_lower.split())
        matched_words = set(matched_lower.split())

        if len(search_words) > 0 and len(matched_words) > 0:
            overlap = search_words.intersection(matched_words)
            overlap_ratio = len(overlap) / max(len(search_words), len(matched_words))
            if overlap_ratio >= 0.6:  # At least 60% word overlap
                return True

        return False

    def _find_fallback_match(self, name, category):
        """Find fallback matches for common items using semantic normalization."""
        normalized_name = self._normalize_item_name(name)

        # Enhanced fallback mappings with normalized keys
        fallback_mappings = {
            'milk': ['milk', 'dairy milk', 'whole milk', 'skim milk', 'semi skimmed milk'],
            'bread': ['bread', 'white bread', 'brown bread', 'wholemeal bread', 'loaf'],
            'eggs': ['eggs', 'egg', 'free range eggs', 'large eggs'],
            'chicken': ['chicken', 'chicken breast', 'chicken thigh', 'whole chicken'],
            'beef': ['beef', 'ground beef', 'steak', 'mince', 'minced beef'],
            'cheese': ['cheese', 'cheddar', 'mozzarella', 'parmesan', 'feta'],
            'tomato': ['tomato', 'tomatoes', 'cherry tomato', 'plum tomato'],
            'potato': ['potato', 'potatoes', 'baking potato', 'new potato'],
            'apple': ['apple', 'apples', 'braeburn', 'granny smith', 'gala'],
            'banana': ['banana', 'bananas', 'fairtrade banana'],
            'rice': ['rice', 'white rice', 'brown rice', 'basmati', 'jasmine rice'],
            'pasta': ['pasta', 'spaghetti', 'penne', 'fusilli', 'macaroni'],
        }

        # Check if normalized name matches any fallback category
        for fallback_key, variations in fallback_mappings.items():
            if normalized_name == fallback_key or any(var in normalized_name for var in variations):
                # Look for the fallback key in the appropriate category
                target_category = category if category != 'food' else 'food'
                matches = self.df[(self.df['category'] == target_category) &
                                (self.df['item'].str.lower().str.contains(fallback_key))]
                if not matches.empty:
                    best_match = matches.iloc[0]
                    # Calculate actual match score instead of hardcoding
                    match_score = fuzz.token_set_ratio(normalized_name, best_match['item'].lower())
                    # Ensure minimum fallback score of 60 to indicate valid match
                    match_score = max(match_score, 60)
                    return best_match['item'], match_score, 0, best_match

        return None

    def _calculate_footprint(self, qty, unit, co2_per_unit, category):
        """Calculate footprint considering units and categories."""
        # Handle unit conversions
        if category == 'food':
            # Most food items are in kg CO2 per kg
            if unit in ['kg', 'kilogram']:
                return round(qty * co2_per_unit, 4)
            elif unit in ['g', 'gram']:
                return round((qty / 1000) * co2_per_unit, 4)
            elif unit in ['liter', 'l']:
                # Assume density of 1 kg/L for liquids
                return round(qty * co2_per_unit, 4)
            else:
                return round(qty * co2_per_unit, 4)
        else:
            # For non-food items, use the co2_per_unit directly
            return round(qty * co2_per_unit, 4)

    def _calculate_category_footprint(self, name, qty, category, unit):
        """Calculate footprint using category-specific factors."""
        if category in self.category_factors:
            # Try to match item name to category factors
            category_items = self.category_factors[category]

            # Look for matching patterns in the name
            for item_key, factor in category_items.items():
                if item_key in name.lower():
                    return round(qty * factor, 4)

            # If no specific match, try to infer from unit
            if unit in category_items:
                return round(qty * category_items[unit], 4)

        return 0.0

    def add_category_data(self, category, item_name, factor, unit='unit'):
        """Add category-specific emission factor."""
        self.category_factors.setdefault(category, {})[item_name] = factor

    def get_category_factors(self, category):
        """Get all factors for a specific category."""
        return self.category_factors.get(category, {})
