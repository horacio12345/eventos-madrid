# backend/agents/scraping_agent.py

"""
Intelligent Scraping Agent - Analyzes websites and decides extraction strategies
"""
import os
import yaml
from typing import Dict, List, Optional
from langchain.agents import AgentExecutor, create_react_agent
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import PromptTemplate
from langchain.hub import pull

from backend.core import get_settings

settings = get_settings()


class ScrapingAgent:
    """
    Agent that analyzes websites and decides which tools to use for data extraction
    """
    
    def __init__(self, tools: List = None):
        # Initialize LLM
        if settings.openai_api_key:
            self.llm = ChatOpenAI(
                model=settings.openai_model,
                temperature=0.1
            )
        elif settings.anthropic_api_key:
            self.llm = ChatAnthropic(
                model=settings.anthropic_model,
                temperature=0.1
            )
        else:
            raise ValueError("Required OPENAI_API_KEY or ANTHROPIC_API_KEY")
        
        # Available tools (will come from backend/tools/)
        self.available_tools = tools or []
        
        # Load prompts from external file
        self.config = self._load_config()
        
        # Create agent executor
        self.agent_executor = None
        if self.available_tools:
            self._create_agent_executor()
    
    def _load_config(self) -> Dict:
        """Load prompts from YAML file"""
        try:
            config_path = os.path.join(
                os.path.dirname(__file__), 
                "prompts", 
                "scraping_agent.yaml"
            )
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError("scraping_agent.yaml prompts file not found")
    
    def _create_agent_executor(self):
        """Create agent executor with tools"""
        try:
            # Use ReAct prompt from hub or custom
            prompt = PromptTemplate.from_template(
                self.config["prompts"]["analyze_strategy"]
            )
            
            # Create ReAct agent
            agent = create_react_agent(
                llm=self.llm,
                tools=self.available_tools,
                prompt=prompt
            )
            
            # Create executor
            self.agent_executor = AgentExecutor(
                agent=agent,
                tools=self.available_tools,
                verbose=True,
                max_iterations=3,
                handle_parsing_errors=True
            )
            
        except Exception as e:
            raise RuntimeError(f"Failed to create agent executor: {str(e)}")
    
    async def analyze_and_scrape(self, state: Dict) -> Dict:
        """
        Analyze website and execute scraping strategy
        """
        try:
            # If no tools available, use direct LLM analysis
            if not self.agent_executor:
                return await self._direct_llm_analysis(state)
            
            # Prepare input for agent
            agent_input = {
                "input": self._format_agent_input(state),
                "chat_history": []
            }
            
            # Execute agent
            result = await self.agent_executor.ainvoke(agent_input)
            
            # Parse agent output
            parsed_result = self._parse_agent_output(result)
            
            # Update state
            state["scraping_strategy"] = parsed_result.get("strategy", "agent_based")
            state["scraped_data"] = parsed_result.get("data", [])
            state["scraping_errors"] = parsed_result.get("errors", [])
            state["scraping_metadata"] = parsed_result.get("metadata", {})
            
            return state
            
        except Exception as e:
            state["scraping_errors"].append(f"Scraping agent error: {str(e)}")
            state["scraped_data"] = []
            return state
    
    async def _direct_llm_analysis(self, state: Dict) -> Dict:
        """Direct LLM analysis when no tools available"""
        try:
            # Create analysis prompt
            analysis_prompt = PromptTemplate.from_template(
                self.config["prompts"]["direct_analysis"]
            )
            
            # Format input
            formatted_input = {
                "url": state["url"],
                "declared_type": state["tipo"],
                "config": state["configuracion_scraping"]
            }
            
            # Execute LLM
            response = await self.llm.ainvoke(
                analysis_prompt.format(**formatted_input)
            )
            
            # Update state with analysis
            state["scraping_strategy"] = "llm_analysis_only"
            state["scraped_data"] = []  # No actual scraping without tools
            state["scraping_errors"] = ["No tools available for scraping"]
            state["scraping_metadata"] = {
                "analysis": response.content,
                "strategy_recommendation": "tools_required"
            }
            
            return state
            
        except Exception as e:
            state["scraping_errors"].append(f"LLM analysis error: {str(e)}")
            return state
    
    def _format_agent_input(self, state: Dict) -> str:
        """Format input for agent"""
        return f"""
        Analyze and scrape this website:
        
        URL: {state['url']}
        Declared Type: {state['tipo']}
        Configuration: {state['configuracion_scraping']}
        
        Available tools: {[tool.name for tool in self.available_tools]}
        
        Determine the best scraping strategy and execute it.
        """
    
    def _parse_agent_output(self, result: Dict) -> Dict:
        """Parse agent execution result"""
        try:
            # Extract information from agent output
            output_text = result.get("output", "")
            
            # Simple parsing - in production, this would be more sophisticated
            return {
                "strategy": "agent_executed",
                "data": [],  # Would be populated by tools
                "errors": [],
                "metadata": {
                    "agent_output": output_text,
                    "intermediate_steps": len(result.get("intermediate_steps", []))
                }
            }
            
        except Exception as e:
            return {
                "strategy": "parsing_error",
                "data": [],
                "errors": [f"Failed to parse agent output: {str(e)}"],
                "metadata": {}
            }