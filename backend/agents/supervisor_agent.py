# backend/agents/supervisor_agent.py

"""
Supervisor Agent - Reviews quality and decides publication
"""
import os
import yaml
import json
from typing import Dict, List
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from backend.core import get_settings

settings = get_settings()


class SupervisorAgent:
    """
    Agent that supervises final quality and decides whether to publish events
    """
    
    def __init__(self):
        # Initialize LLM
        if settings.openai_api_key:
            self.llm = ChatOpenAI(
                model=settings.openai_model,
                temperature=0
            )
        elif settings.anthropic_api_key:
            self.llm = ChatAnthropic(
                model=settings.anthropic_model,
                temperature=0
            )
        else:
            raise ValueError("Required OPENAI_API_KEY or ANTHROPIC_API_KEY")
        
        # Load configuration from external file
        self.config = self._load_config()
        
        # JSON output parser for structured responses
        self.json_parser = JsonOutputParser()
        
        # Create supervision prompt template
        self.supervision_prompt = PromptTemplate(
            input_variables=["events_sample", "quality_criteria", "pipeline_errors"],
            template=self.config["prompts"]["quality_review"]
        )
    
    def _load_config(self) -> Dict:
        """Load prompts and criteria from YAML file"""
        try:
            config_path = os.path.join(
                os.path.dirname(__file__), 
                "prompts", 
                "supervisor_agent.yaml"
            )
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError("supervisor_agent.yaml prompts file not found")
    
    async def supervise_quality(self, state: Dict) -> Dict:
        """
        Supervise quality and decide approval for publication
        """
        try:
            events = state.get("processed_events", [])
            all_errors = (
                state.get("scraping_errors", []) +
                state.get("processing_errors", [])
            )
            
            # Automatic validation
            auto_validation = self._automatic_validation(events)
            
            # Intelligent supervision with LLM
            llm_decision = await self._llm_supervision(events, all_errors)
            
            # Final decision
            final_decision = self._make_final_decision(auto_validation, llm_decision)
            
            # Update state
            state["supervision_decision"] = final_decision["status"]
            state["supervision_reasoning"] = final_decision["reasoning"]
            state["approved_events"] = final_decision.get("approved_events", [])
            state["rejected_events"] = final_decision.get("rejected_events", [])
            
            return state
            
        except Exception as e:
            state["supervision_decision"] = "ERROR"
            state["supervision_reasoning"] = f"Supervisor error: {str(e)}"
            state["approved_events"] = []
            return state
    
    def _automatic_validation(self, events: List[Dict]) -> Dict:
        """Automatic validation based on criteria from config"""
        valid_events = []
        invalid_events = []
        
        # Get criteria from config
        criteria = self.config.get("criteria", {})
        required_fields = criteria.get("required_fields", [])
        valid_categories = criteria.get("valid_categories", [])
        max_price = criteria.get("max_price", 15)
        
        for event in events:
            is_valid = True
            reasons = []
            
            # Check required fields
            for field in required_fields:
                if not event.get(field):
                    is_valid = False
                    reasons.append(f"Missing field: {field}")
            
            # Check valid category
            if valid_categories and event.get("categoria") not in valid_categories:
                is_valid = False
                reasons.append("Invalid category")
            
            # Check price
            precio_str = event.get("precio", "0")
            try:
                precio_num = float(precio_str.replace("€", "").replace("Gratis", "0"))
                if precio_num > max_price:
                    is_valid = False
                    reasons.append("Price too high")
            except:
                pass  # If can't parse, continue
            
            if is_valid:
                valid_events.append(event)
            else:
                invalid_events.append({"event": event, "reasons": reasons})
        
        min_events = criteria.get("min_events", 1)
        
        return {
            "valid_count": len(valid_events),
            "invalid_count": len(invalid_events),
            "valid_events": valid_events,
            "invalid_events": invalid_events,
            "meets_minimum": len(valid_events) >= min_events
        }
    
    async def _llm_supervision(self, events: List[Dict], errors: List[str]) -> Dict:
        """Intelligent supervision with LLM"""
        try:
            # Prepare supervision input
            supervision_input = {
                "events_sample": json.dumps(events[:3], ensure_ascii=False, indent=2),
                "quality_criteria": self._format_criteria(),
                "pipeline_errors": json.dumps(errors, ensure_ascii=False)
            }
            
            # Create chain with prompt and parser
            chain = self.supervision_prompt | self.llm | self.json_parser
            
            # Execute supervision
            response = await chain.ainvoke(supervision_input)
            
            # Parse structured response
            decision = response.get("decision", "ERROR").upper()
            reasoning = response.get("reasoning", "No reasoning provided")
            
            return {
                "decision": decision,
                "reasoning": reasoning
            }
                
        except Exception as e:
            return {
                "decision": "ERROR", 
                "reasoning": f"LLM supervision failed: {str(e)}"
            }
    
    def _format_criteria(self) -> str:
        """Format quality criteria from config"""
        criteria = self.config.get("criteria", {})
        
        formatted_criteria = []
        for key, value in criteria.items():
            if isinstance(value, list):
                formatted_criteria.append(f"- {key.replace('_', ' ').title()}: {', '.join(map(str, value))}")
            else:
                formatted_criteria.append(f"- {key.replace('_', ' ').title()}: {value}")
        
        return "\n".join(formatted_criteria)
    
    def _make_final_decision(self, auto_validation: Dict, llm_decision: Dict) -> Dict:
        """Combine automatic validation and LLM for final decision"""
        
        # If doesn't meet automatic minimums → REJECT
        if not auto_validation["meets_minimum"]:
            return {
                "status": "REJECTED",
                "reasoning": "Does not meet minimum quality criteria",
                "approved_events": [],
                "rejected_events": auto_validation["invalid_events"]
            }
        
        # If LLM approves and has valid events → APPROVE
        if llm_decision["decision"] == "APPROVE" and auto_validation["valid_count"] > 0:
            return {
                "status": "APPROVED",
                "reasoning": llm_decision["reasoning"],
                "approved_events": auto_validation["valid_events"],
                "rejected_events": auto_validation["invalid_events"]
            }
        
        # If LLM explicitly rejects → REJECT
        if llm_decision["decision"] == "REJECT":
            return {
                "status": "REJECTED",
                "reasoning": llm_decision["reasoning"],
                "approved_events": [],
                "rejected_events": auto_validation["invalid_events"]
            }
        
        # Other cases → MANUAL REVIEW
        return {
            "status": "MANUAL_REVIEW",
            "reasoning": f"Auto: {auto_validation['valid_count']} valid. LLM: {llm_decision['reasoning']}",
            "approved_events": [],
            "rejected_events": []
        }