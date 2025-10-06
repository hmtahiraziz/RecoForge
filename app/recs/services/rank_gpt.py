"""
GPT-based ranking service for recommendations using OpenAI Responses API.
"""

import openai
from typing import List, Dict, Any, Optional
import logging
import json
from .config import config

logger = logging.getLogger(__name__)

class RankGPTService:
    """Service for re-ranking recommendations using GPT with function calling."""

    def __init__(self):
        if not config.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required")

        # Initialize OpenAI client - only pass organization if it's set
        client_kwargs = {"api_key": config.openai_api_key}
        if config.openai_org_id and config.openai_org_id.strip():
            client_kwargs["organization"] = config.openai_org_id

        self.client = openai.OpenAI(**client_kwargs)
        self.model = config.rerank_model

        # Define the function schema for rank_products
        self.rank_products_tool = {
            "type": "function",
            "function": {
                "name": "rank_products",
                "description": "Rank and score product candidates based on user preferences and questionnaire answers",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ranked_products": {
                            "type": "array",
                            "description": "List of ranked and scored products",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "sku": {"type": "string", "description": "Product SKU"},
                                    "score": {"type": "number", "minimum": 0.0, "maximum": 1.0, "description": "Relevance score (0.0-1.0)"},
                                    "reasons": {"type": "array", "items": {"type": "string"}, "description": "List of reasons for this ranking"},
                                    "qty": {"type": "integer", "minimum": 1, "description": "Recommended quantity"}
                                },
                                "required": ["sku", "score", "reasons", "qty"]
                            }
                        }
                    },
                    "required": ["ranked_products"]
                }
            }
        }

        # Define the expected return schema
        self.return_schema = {
            "type": "object",
            "properties": {
                "ranked_products": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "sku": {"type": "string"},
                            "score": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                            "reasons": {"type": "array", "items": {"type": "string"}},
                            "qty": {"type": "integer", "minimum": 1}
                        },
                        "required": ["sku", "score", "reasons", "qty"]
                    }
                }
            },
            "required": ["ranked_products"]
        }

    def build_candidate_payload(self, faiss_hits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Build candidate payload from FAISS hits for GPT ranking.

        Args:
            faiss_hits: List of items from FAISS search with metadata

        Returns:
            List of candidate objects formatted for GPT function calling
        """
        candidates = []

        for hit in faiss_hits:
            # Extract metadata
            metadata = hit.get('metadata', {})

            candidate = {
                'id': hit.get('id', ''),
                'sku': hit.get('sku', ''),
                'title': hit.get('title', ''),
                'brand': metadata.get('brand', ''),
                'category': metadata.get('category', {}),
                'style': metadata.get('style', ''),
                'abv': metadata.get('abv'),
                'container': {},  # Will be populated from original data if available
                'tags': [],  # Will be populated from original data if available
                'price': None,  # Will be populated from pricing service
                'region_availability': metadata.get('inventory', {}).get('region_codes', [])
            }

            candidates.append(candidate)

        return candidates

    def create_ranking_instruction(self, query: str, answers: Dict[str, Any], candidates: List[Dict[str, Any]]) -> str:
        """
        Create a concise instruction for GPT ranking with acceptance criteria.

        Args:
            query: User's search query
            answers: User questionnaire answers and preferences

        Returns:
            Formatted instruction string
        """
        instruction_parts = [
            f"User Query: {query}",
            "",
            "Rank the following product candidates based on:",
            "1. Relevance to the user's query and preferences",
            "2. User's preferred categories and brands",
            "3. ABV preference and price range",
            "4. Occasion and flavor preferences",
            "5. Overall quality and value",
            "",
            "User Preferences:"
        ]

        if answers.get('preferred_categories'):
            instruction_parts.append(f"- Preferred categories: {', '.join(answers['preferred_categories'])}")

        if answers.get('preferred_brands'):
            instruction_parts.append(f"- Preferred brands: {', '.join(answers['preferred_brands'])}")

        if answers.get('abv_preference'):
            instruction_parts.append(f"- ABV preference: {answers['abv_preference']}")

        if answers.get('price_range'):
            price_range = answers['price_range']
            instruction_parts.append(f"- Price range: ${price_range.get('min', 0)} - ${price_range.get('max', 'unlimited')}")

        if answers.get('occasion'):
            instruction_parts.append(f"- Occasion: {answers['occasion']}")

        if answers.get('flavor_preferences'):
            instruction_parts.append(f"- Flavor preferences: {', '.join(answers['flavor_preferences'])}")

        if answers.get('dietary_requirements'):
            instruction_parts.append(f"- Dietary requirements: {', '.join(answers['dietary_requirements'])}")

        instruction_parts.extend([
            "",
            "Product Candidates to Rank:",
            json.dumps(candidates, indent=2),
            "",
            "Return a ranked list with scores (0.0-1.0), reasons, and quantities.",
            "Focus on products that best match the user's preferences and query intent.",
            f"Return up to {len(candidates)} products, ranked by relevance."
        ])

        return "\n".join(instruction_parts)

    async def rerank_with_function_calling(self,
                                         query: str,
                                         candidates: List[Dict[str, Any]],
                                         answers: Dict[str, Any],
                                         limit: int = 10) -> Dict[str, Any]:
        """
        Re-rank candidates using OpenAI Responses API with function calling.

        Args:
            query: User's search query
            candidates: List of candidate products from FAISS
            answers: User questionnaire answers and preferences
            limit: Maximum number of products to return

        Returns:
            Dictionary with ranked items, reasons, and confidence
        """
        if not candidates:
            return {
                'items': [],
                'reasons': [],
                'confidence': 0.0,
                'subtotal': 0.0
            }

        try:
            # Build candidate payload
            candidate_payload = self.build_candidate_payload(candidates)

            # Create instruction
            instruction = self.create_ranking_instruction(query, answers, candidate_payload)

            # Call OpenAI with function calling
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert product recommendation system. Use the rank_products function to provide structured rankings with scores, reasons, and quantities."
                    },
                    {
                        "role": "user",
                        "content": instruction
                    }
                ],
                tools=[self.rank_products_tool],
                tool_choice={"type": "function", "function": {"name": "rank_products"}},
                temperature=0.1,
                max_tokens=4000
            )

            # Extract function call result
            tool_call = response.choices[0].message.tool_calls[0]
            function_args = json.loads(tool_call.function.arguments)

            # Debug logging
            logger.info(f"GPT function call response: {function_args}")

            # Validate and process results
            ranked_items = self._validate_and_process_ranking(function_args, limit)
            logger.info(f"Validated ranking items: {len(ranked_items)}")

            # Compute subtotal and confidence
            subtotal = self._compute_subtotal(ranked_items)
            confidence = self._compute_confidence(ranked_items)

            return {
                'items': ranked_items,
                'reasons': [item.get('reasons', []) for item in ranked_items],
                'confidence': confidence,
                'subtotal': subtotal
            }

        except Exception as e:
            logger.error(f"Error in GPT function calling ranking: {e}")
            # Fallback to simple ranking
            return self._fallback_ranking(candidates, limit)

    def _validate_and_process_ranking(self, function_args: Dict[str, Any], limit: int) -> List[Dict[str, Any]]:
        """
        Validate and process the GPT ranking results.

        Args:
            function_args: Arguments from the GPT function call
            limit: Maximum number of items to return

        Returns:
            List of validated and processed ranking items
        """
        try:
            # Extract ranked products from function arguments
            ranked_products = function_args.get('ranked_products', [])
            logger.info(f"Extracted ranked_products: {len(ranked_products)} items")

            if not ranked_products:
                logger.warning("No ranked_products found in function arguments")
                return []

            # Validate and clip to limit
            validated_items = []
            for i, item in enumerate(ranked_products[:limit]):
                logger.info(f"Validating item {i+1}: {item}")
                if self._validate_ranking_item(item):
                    validated_items.append(item)
                    logger.info(f"Item {i+1} passed validation")
                else:
                    logger.warning(f"Item {i+1} failed validation")

            logger.info(f"Final validated items: {len(validated_items)}")
            return validated_items

        except Exception as e:
            logger.error(f"Error validating ranking results: {e}")
            return []

    def _validate_ranking_item(self, item: Dict[str, Any]) -> bool:
        """
        Validate a single ranking item.

        Args:
            item: Ranking item to validate

        Returns:
            True if item is valid, False otherwise
        """
        required_fields = ['sku', 'score', 'reasons', 'qty']

        # Check required fields
        if not all(field in item for field in required_fields):
            return False

        # Validate score (0.0-1.0)
        score = item.get('score', 0)
        if not isinstance(score, (int, float)) or not (0.0 <= score <= 1.0):
            return False

        # Validate reasons (list of strings)
        reasons = item.get('reasons', [])
        if not isinstance(reasons, list) or not all(isinstance(r, str) for r in reasons):
            return False

        # Validate quantity (positive integer)
        qty = item.get('qty', 0)
        if not isinstance(qty, int) or qty <= 0:
            return False

        return True

    def _compute_subtotal(self, items: List[Dict[str, Any]]) -> float:
        """
        Compute subtotal for ranked items (treat null price as 0).

        Args:
            items: List of ranked items

        Returns:
            Total subtotal
        """
        subtotal = 0.0

        for item in items:
            price = item.get('price', 0)
            qty = item.get('qty', 1)

            if price is None:
                price = 0

            subtotal += price * qty

        return subtotal

    def _compute_confidence(self, items: List[Dict[str, Any]]) -> float:
        """
        Compute confidence score based on normalized scores.

        Args:
            items: List of ranked items

        Returns:
            Confidence score (0.0-1.0)
        """
        if not items:
            return 0.0

        # Get all scores
        scores = [item.get('score', 0) for item in items]

        # Compute average score as confidence
        confidence = sum(scores) / len(scores)

        return min(1.0, max(0.0, confidence))

    def _fallback_ranking(self, candidates: List[Dict[str, Any]], limit: int) -> Dict[str, Any]:
        """
        Fallback ranking when GPT function calling fails.

        Args:
            candidates: List of candidate items
            limit: Maximum number of items to return

        Returns:
            Fallback ranking result
        """
        fallback_items = []

        for i, candidate in enumerate(candidates[:limit]):
            fallback_item = {
                'sku': candidate.get('sku', ''),
                'score': max(0.1, 1.0 - (i * 0.1)),  # Decreasing scores
                'reasons': [f"Ranked based on similarity score: {candidate.get('score', 0):.3f}"],
                'qty': 1,
                'price': candidate.get('price', 0)
            }
            fallback_items.append(fallback_item)

        subtotal = self._compute_subtotal(fallback_items)
        confidence = self._compute_confidence(fallback_items)

        return {
            'items': fallback_items,
            'reasons': [item.get('reasons', []) for item in fallback_items],
            'confidence': confidence,
            'subtotal': subtotal
        }

    def _format_candidates_for_gpt(self, candidates: List[Dict[str, Any]]) -> str:
        """Format candidates for GPT input."""
        formatted = []

        for i, candidate in enumerate(candidates, 1):
            title = candidate.get('title', 'No title')
            description = candidate.get('description', '')
            content = candidate.get('content', '')
            metadata = candidate.get('metadata', {})
            score = candidate.get('score', 0)

            # Truncate long content
            if content and len(content) > 200:
                content = content[:200] + "..."

            candidate_text = f"{i}. {title}"
            if description:
                candidate_text += f"\n   Description: {description}"
            if content:
                candidate_text += f"\n   Content: {content}"
            if metadata:
                candidate_text += f"\n   Metadata: {json.dumps(metadata, indent=2)}"
            candidate_text += f"\n   Relevance Score: {score:.3f}\n"

            formatted.append(candidate_text)

        return "\n".join(formatted)

    def _create_ranking_prompt(self, query: str, candidates_text: str, limit: int) -> str:
        """Create prompt for GPT ranking."""
        return f"""
Please rank the following items based on their relevance to the user query: "{query}"

Return the top {limit} most relevant items in order of relevance.

For each item, provide:
1. The item number (1, 2, 3, etc.)
2. A relevance score from 0.0 to 1.0
3. A brief explanation of why this item is relevant

Format your response as JSON:
{{
  "rankings": [
    {{
      "item_number": 1,
      "relevance_score": 0.95,
      "explanation": "This item is highly relevant because..."
    }},
    ...
  ]
}}

Items to rank:
{candidates_text}

Please focus on semantic relevance, not just keyword matching. Consider the user's intent and the overall context.
"""

    def _parse_ranking_response(self, response: str, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse GPT response and apply rankings."""
        try:
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1

            if json_start == -1 or json_end == 0:
                logger.warning("No JSON found in GPT response")
                return self._fallback_ranking(candidates, limit)

            json_str = response[json_start:json_end]
            data = json.loads(json_str)

            rankings = data.get('rankings', [])
            if not rankings:
                logger.warning("No rankings found in GPT response")
                return self._fallback_ranking(candidates, limit)

            # Apply rankings to candidates
            ranked_candidates = []
            for ranking in rankings:
                item_number = ranking.get('item_number', 1)
                relevance_score = ranking.get('relevance_score', 0.0)
                explanation = ranking.get('explanation', 'No explanation provided')

                # Get candidate by index (item_number - 1)
                if 1 <= item_number <= len(candidates):
                    candidate = candidates[item_number - 1].copy()
                    candidate['score'] = relevance_score
                    candidate['explanation'] = explanation
                    ranked_candidates.append(candidate)

            return ranked_candidates

        except json.JSONDecodeError as e:
            logger.error(f"Error parsing GPT response JSON: {e}")
            return self._fallback_ranking(candidates, limit)
        except Exception as e:
            logger.error(f"Error parsing GPT response: {e}")
            return self._fallback_ranking(candidates, limit)


    async def explain_recommendation(self, query: str, item: Dict[str, Any]) -> str:
        """Generate explanation for a specific recommendation."""
        try:
            prompt = f"""
Explain why this item is recommended for the query: "{query}"

Item details:
- Title: {item.get('title', 'No title')}
- Description: {item.get('description', 'No description')}
- Content: {item.get('content', 'No content')[:300]}...
- Metadata: {json.dumps(item.get('metadata', {}), indent=2)}

Provide a clear, concise explanation of the relevance.
"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at explaining recommendation relevance. Provide clear, helpful explanations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=300
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"Error generating explanation: {e}")
            return f"Recommended based on similarity score: {item.get('score', 0):.3f}"
