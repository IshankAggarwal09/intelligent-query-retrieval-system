# llm_service.py
import google.generativeai as genai
from typing import List, Dict, Any
import json
import logging
from config import settings
from ..models import RetrievalResult, DecisionRationale

class LLMService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.LLM_MODEL)
        self.logger = logging.getLogger(__name__)
    
    async def analyze_query_and_context(self, 
                                      query: str, 
                                      retrieved_chunks: List[RetrievalResult],
                                      domain: str = None) -> Dict[str, Any]:
        """Analyze query with retrieved context and provide decision rationale"""
        try:
            # Prepare context from retrieved chunks
            context = self._prepare_context(retrieved_chunks)
            
            # Create domain-specific prompt
            prompt = self._create_analysis_prompt(query, context, domain)
            
            # Generate response
            response = await self._generate_response(prompt)
            
            # Parse structured response
            parsed_response = self._parse_llm_response(response)
            
            return parsed_response
        except Exception as e:
            self.logger.error(f"Error analyzing query: {str(e)}")
            raise
    
    def _prepare_context(self, retrieved_chunks: List[RetrievalResult]) -> str:
        """Prepare context from retrieved chunks"""
        context_parts = []
        for i, chunk in enumerate(retrieved_chunks):
            context_parts.append(
                f"Document {i+1} (Relevance: {chunk.relevance_score:.3f}):\n"
                f"Source: {chunk.metadata.get('filename', 'Unknown')}\n"
                f"Content: {chunk.content}\n"
            )
        return "\n---\n".join(context_parts)
    
    def _create_analysis_prompt(self, query: str, context: str, domain: str = None) -> str:
        """Create domain-specific analysis prompt"""
        domain_instructions = {
            "insurance": """
            Focus on:
            - Coverage details and limitations
            - Exclusions and conditions
            - Claim procedures and requirements
            - Policy terms and definitions
            """,
            "legal": """
            Focus on:
            - Legal clauses and provisions
            - Rights and obligations
            - Compliance requirements
            - Regulatory implications
            """,
            "hr": """
            Focus on:
            - Employee policies and procedures
            - Benefits and entitlements
            - Compliance with labor laws
            - Performance and conduct standards
            """,
            "compliance": """
            Focus on:
            - Regulatory requirements
            - Audit standards
            - Risk assessments
            - Compliance procedures
            """
        }
        
        domain_context = domain_instructions.get(domain, "") if domain else ""
        
        return f"""
        You are an expert document analyst specializing in {domain or 'various'} domains. 
        Analyze the following query and provide a comprehensive, accurate response based on the retrieved context.

        {domain_context}

        Query: {query}

        Retrieved Context:
        {context}

        Provide your response in the following JSON format:
        {{
            "answer": "Direct answer to the query",
            "reasoning": "Detailed explanation of your analysis",
            "confidence_score": 0.0-1.0,
            "supporting_evidence": ["Evidence point 1", "Evidence point 2"],
            "conditions": ["Condition 1", "Condition 2"],
            "limitations": ["Limitation 1", "Limitation 2"],
            "additional_considerations": "Any other relevant information"
        }}

        Important guidelines:
        - Base your answer strictly on the provided context
        - If information is insufficient, clearly state this
        - Provide specific evidence from the documents
        - Include relevant conditions and limitations
        - Rate your confidence based on the clarity and completeness of the evidence
        """
    
    async def _generate_response(self, prompt: str) -> str:
        """Generate response from Gemini"""
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=settings.MAX_TOKENS,
                    candidate_count=1
                )
            )
            return response.text
        except Exception as e:
            self.logger.error(f"Error generating LLM response: {str(e)}")
            raise
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse structured response from LLM"""
        try:
            # Extract JSON from response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON found in response")
            
            json_str = response[start_idx:end_idx]
            parsed = json.loads(json_str)
            
            # Validate and structure the response
            return {
                "answer": parsed.get("answer", "Unable to provide answer"),
                "decision_rationale": DecisionRationale(
                    reasoning=parsed.get("reasoning", "No reasoning provided"),
                    confidence_score=float(parsed.get("confidence_score", 0.0)),
                    supporting_evidence=parsed.get("supporting_evidence", []),
                    conditions=parsed.get("conditions", []),
                    limitations=parsed.get("limitations", [])
                ),
                "additional_considerations": parsed.get("additional_considerations", "")
            }
        except Exception as e:
            self.logger.error(f"Error parsing LLM response: {str(e)}")
            # Fallback response
            return {
                "answer": "Error processing response",
                "decision_rationale": DecisionRationale(
                    reasoning="Unable to parse LLM response",
                    confidence_score=0.0,
                    supporting_evidence=[],
                    conditions=[],
                    limitations=["Response parsing failed"]
                ),
                "additional_considerations": ""
            }
