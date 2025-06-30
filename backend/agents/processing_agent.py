# backend/agents/processing_agent.py - Fix para mantener validation_results

"""
Processing Agent - Normalizes and validates scraped data
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Tuple

import yaml
from langchain_anthropic import ChatAnthropic
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from backend.core import get_settings
from backend.services.event_normalizer import EventNormalizer

settings = get_settings()


class ProcessingAgent:
    """
    Agent that processes raw data and normalizes it to standard format
    """

    def __init__(self):
        # Initialize LLM
        if settings.openai_api_key:
            self.llm = ChatOpenAI(model=settings.openai_model, temperature=0)
        elif settings.anthropic_api_key:
            self.llm = ChatAnthropic(model=settings.anthropic_model, temperature=0)
        else:
            raise ValueError("Required OPENAI_API_KEY or ANTHROPIC_API_KEY")

        # Existing normalizer service
        self.normalizer = EventNormalizer()

        # Load prompts and criteria from external file
        self.config = self._load_config()

        # JSON output parser for structured responses
        self.json_parser = JsonOutputParser()

        # Create validation prompt template
        self.validation_prompt = PromptTemplate(
            input_variables=["events_data", "current_date", "criteria"],
            template=self.config["prompts"]["validate_events"],
        )

    def _load_config(self) -> Dict:
        """Load prompts and criteria from YAML file"""
        try:
            config_path = os.path.join(
                os.path.dirname(__file__), "prompts", "processing_agent.yaml"
            )
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError("processing_agent.yaml prompts file not found")

    async def process_data(self, state: Dict) -> Dict:
        """
        Process scraped data and normalize it
        """
        print(f"⚙️ [DEBUG] ProcessingAgent.process_data - input state keys: {list(state.keys())}")
        print(f"⚙️ [DEBUG] ProcessingAgent.process_data - validation_results in input: {'validation_results' in state}")
        
        try:
            raw_data = state.get("scraped_data", [])
            field_mapping = state.get("mapeo_campos", {})

            if not raw_data:
                # PRESERVAR estado completo y actualizar campos específicos
                result_state = state.copy()  # CRÍTICO: preservar todo el estado
                result_state["processed_events"] = []
                result_state["processing_errors"] = ["No data to process"]
                
                # MANTENER o inicializar validation_results
                if "validation_results" not in result_state:
                    result_state["validation_results"] = {
                        "quality_score": 0.0,
                        "total_extracted": 0,
                        "total_validated": 0,
                        "approval_rate": 0.0
                    }
                
                return result_state

            # Step 1: Basic normalization
            normalized_events = []
            normalization_errors = []

            for i, event_data in enumerate(raw_data):
                try:
                    normalized = self.normalizer.normalize_event(
                        event_data, field_mapping
                    )
                    if normalized:
                        normalized_events.append(normalized)
                    else:
                        normalization_errors.append(f"Event {i}: Failed normalization")
                except Exception as e:
                    normalization_errors.append(f"Event {i}: {str(e)}")

            # Step 2: LLM validation
            if normalized_events:
                validated_events, validation_errors = await self._validate_with_llm(
                    normalized_events
                )
            else:
                validated_events = []
                validation_errors = ["No events passed normalization"]

            # PRESERVAR estado completo y actualizar campos específicos
            result_state = state.copy()  # CRÍTICO: preservar todo el estado
            result_state["processed_events"] = validated_events
            result_state["processing_errors"] = normalization_errors + validation_errors
            result_state["processing_metadata"] = {
                "total_raw": len(raw_data),
                "normalized": len(normalized_events),
                "validated": len(validated_events),
                "rejection_rate": (
                    1 - (len(validated_events) / len(raw_data)) if raw_data else 0
                ),
            }

            # ACTUALIZAR validation_results
            result_state["validation_results"] = {
                "quality_score": 1.0 - result_state["processing_metadata"]["rejection_rate"],
                "total_extracted": len(raw_data),
                "total_validated": len(validated_events),
                "approval_rate": 1.0 - result_state["processing_metadata"]["rejection_rate"]
            }
            
            print(f"⚙️ [DEBUG] ProcessingAgent.process_data - output validation_results: {result_state['validation_results']}")
            return result_state

        except Exception as e:
            print(f"💥 [DEBUG] ProcessingAgent.process_data - Exception: {str(e)}")
            # PRESERVAR estado completo en caso de error
            result_state = state.copy()
            result_state["processing_errors"] = [f"Processing agent error: {str(e)}"]
            result_state["processed_events"] = []
            
            # MANTENER o inicializar validation_results
            if "validation_results" not in result_state:
                result_state["validation_results"] = {
                    "quality_score": 0.0,
                    "total_extracted": 0,
                    "total_validated": 0,
                    "approval_rate": 0.0
                }
            
            return result_state

    async def _validate_with_llm(
        self, events: List[Dict]
    ) -> Tuple[List[Dict], List[str]]:
        """Intelligent validation with LLM"""
        try:
            # Prepare validation input
            validation_input = {
                "events_data": json.dumps(events, ensure_ascii=False, indent=2),
                "current_date": datetime.now().strftime("%Y-%m-%d"),
                "criteria": self._format_criteria(),
            }

            # Create chain with prompt and parser
            chain = self.validation_prompt | self.llm | self.json_parser

            # Execute validation
            response = await chain.ainvoke(validation_input)

            # Parse response
            validated_events = response.get("valid_events", [])
            rejected_reasons = response.get("rejected_events", [])

            # Format errors from rejected events
            validation_errors = []
            for rejection in rejected_reasons:
                validation_errors.append(
                    f"Rejected: {rejection.get('reason', 'Unknown')}"
                )

            return validated_events, validation_errors

        except Exception as e:
            error_msg = f"LLM validation failed: {str(e)}"
            # Fallback: return normalized events without LLM validation
            return events, [error_msg]

    def _format_criteria(self) -> str:
        """Format validation criteria from config"""
        criteria = self.config.get("criteria", {})

        formatted_criteria = []
        for key, value in criteria.items():
            formatted_criteria.append(f"- {key.replace('_', ' ').title()}: {value}")

        return "\n".join(formatted_criteria)