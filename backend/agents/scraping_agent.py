# backend/agents/scraping_agent.py

"""
Intelligent Scraping Agent - Analyzes websites and decides extraction strategies using new tools
"""
import os
from typing import Dict, List, Optional

import yaml
from langchain.agents import AgentExecutor, create_react_agent
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from backend.core import get_settings
from backend.tools import ALL_TOOLS

settings = get_settings()


class ScrapingAgent:
    """
    Agent that analyzes websites and decides which tools to use for intelligent data extraction
    """

    def __init__(self, tools: List = None):
        # Initialize LLM
        if settings.openai_api_key:
            self.llm = ChatOpenAI(model=settings.openai_model, temperature=0.1)
        elif settings.anthropic_api_key:
            self.llm = ChatAnthropic(model=settings.anthropic_model, temperature=0.1)
        else:
            raise ValueError("Required OPENAI_API_KEY or ANTHROPIC_API_KEY")

        # Use provided tools or default to all available tools
        self.available_tools = tools or ALL_TOOLS

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
                os.path.dirname(__file__), "prompts", "scraping_agent.yaml"
            )
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError("scraping_agent.yaml prompts file not found")

    def _create_agent_executor(self):
        """Create agent executor with tools"""
        try:
            # Get the raw prompt template from config
            prompt_template = self.config["prompts"]["intelligent_strategy"]
            
            # Format tool descriptions
            tools_description = "\n".join([f"- {tool.name}: {tool.description}" for tool in self.available_tools])
            tool_names = ", ".join([tool.name for tool in self.available_tools])
            
            # Create the proper ReAct prompt template with ALL required variables
            prompt = PromptTemplate(
                input_variables=["url", "declared_type", "config", "tools_description", "input", "agent_scratchpad"],
                partial_variables={
                    "tools": tools_description,
                    "tool_names": tool_names
                },
                template=prompt_template
            )

            # Create ReAct agent with the prompt template
            agent = create_react_agent(
                llm=self.llm,
                tools=self.available_tools,
                prompt=prompt
            )

            # Create executor with optimized settings
            self.agent_executor = AgentExecutor(
                agent=agent,
                tools=self.available_tools,
                verbose=True,
                max_iterations=5,  # Increased for multi-step analysis
                handle_parsing_errors=True,
                early_stopping_method="generate",
            )

        except Exception as e:
            raise RuntimeError(f"Failed to create agent executor: {str(e)}")

    async def analyze_and_scrape(self, state: Dict) -> Dict:
        """
        Analyze website and execute intelligent scraping strategy
        """
        try:
            # If no tools available, use direct LLM analysis
            if not self.agent_executor:
                return await self._direct_llm_analysis(state)

            # Prepare input for intelligent agent workflow
            agent_input = {
                "input": self._format_intelligent_input(state),
                "url": state["url"],
                "declared_type": state["tipo"],
                "config": state["configuracion_scraping"],
                "tools_description": self._get_tools_description(),
            }

            # Execute agent with new workflow
            result = await self.agent_executor.ainvoke(agent_input)

            # Parse agent output to extract structured results
            parsed_result = self._parse_intelligent_output(result)

            # Update state with comprehensive results
            state["scraping_strategy"] = parsed_result.get(
                "strategy", "intelligent_analysis"
            )
            state["scraped_data"] = parsed_result.get("data", [])
            state["scraping_errors"] = parsed_result.get("errors", [])
            state["scraping_metadata"] = parsed_result.get("metadata", {})

            # Add new intelligence metadata
            state["analysis_results"] = parsed_result.get("analysis_results", {})
            state["temporal_results"] = parsed_result.get("temporal_results", {})
            state["prioritization_results"] = parsed_result.get(
                "prioritization_results", {}
            )

            return state

        except Exception as e:
            state["scraping_errors"].append(
                f"Intelligent scraping agent error: {str(e)}"
            )
            state["scraped_data"] = []
            return state

    async def _direct_llm_analysis(self, state: Dict) -> Dict:
        """Enhanced direct LLM analysis when no tools available"""
        try:
            # Create enhanced analysis prompt
            analysis_prompt = PromptTemplate.from_template(
                self.config["prompts"]["enhanced_analysis"]
            )

            # Format input with new context
            formatted_input = {
                "url": state["url"],
                "declared_type": state["tipo"],
                "config": state["configuracion_scraping"],
                "available_strategies": self._get_available_strategies(),
            }

            # Execute LLM
            response = await self.llm.ainvoke(analysis_prompt.format(**formatted_input))

            # Update state with enhanced analysis
            state["scraping_strategy"] = "llm_enhanced_analysis"
            state["scraped_data"] = []
            state["scraping_errors"] = ["Tools required for actual extraction"]
            state["scraping_metadata"] = {
                "analysis": response.content,
                "strategy_recommendation": "implement_intelligent_tools",
                "recommended_workflow": [
                    "1. Analyze page structure",
                    "2. Detect temporal patterns",
                    "3. Prioritize content",
                    "4. Extract using appropriate tools",
                ],
            }

            return state

        except Exception as e:
            state["scraping_errors"].append(f"Enhanced LLM analysis error: {str(e)}")
            return state

    def _get_tools_description(self) -> str:
        """Get formatted tools description"""
        return "\n".join([f"- {tool.name}: {tool.description}" for tool in self.available_tools])

    def _format_intelligent_input(self, state: Dict) -> str:
        """Format input for intelligent agent workflow"""
        
        return f"""
        You are an intelligent scraping agent. Analyze this website and extract events using the available tools.
        
        WEBSITE INFORMATION:
        URL: {state['url']}
        Declared Type: {state['tipo']}
        Configuration: {state['configuracion_scraping']}
        
        INTELLIGENT WORKFLOW (follow these steps):
        
        1. ANALYZE PAGE STRUCTURE:
           - Use analyze_page_structure() to understand content organization
           - Use analyze_content_types() to identify content types
        
        2. DETECT TEMPORAL PATTERNS:
           - Use detect_temporal_patterns() to find time-based organization
           - Use extract_dates_from_text() if temporal patterns found
        
        3. PRIORITIZE CONTENT:
           - Use prioritize_by_temporal_relevance() if temporal data available
           - Use prioritize_content_final() to make final decision
        
        4. EXTRACT DATA:
           - Use extract_html_with_pdfs() if PDFs detected
           - Use extract_pdf_direct() for selected PDF
           - Use extract_html_simple() for direct HTML content
        
        5. VALIDATE (if needed):
           - Use validate_event_relevance() to filter results
        
        Execute this workflow step by step to extract relevant events for seniors in Madrid.
        Focus on finding the most recent and relevant content.
        """

    def _parse_intelligent_output(self, result: Dict) -> Dict:
        """Parse agent execution result to extract structured data"""
        try:
            # Extract information from agent output
            output_text = result.get("output", "")
            intermediate_steps = result.get("intermediate_steps", [])

            # Initialize results structure
            parsed_result = {
                "strategy": "intelligent_workflow",
                "data": [],
                "errors": [],
                "metadata": {
                    "agent_output": output_text,
                    "steps_executed": len(intermediate_steps),
                },
                "analysis_results": {},
                "temporal_results": {},
                "prioritization_results": {},
            }

            # Parse intermediate steps to extract tool results
            for step in intermediate_steps:
                try:
                    if (
                        hasattr(step, "tool")
                        and hasattr(step, "tool_input")
                        and hasattr(step, "observation")
                    ):
                        tool_name = step.tool
                        tool_result = step.observation

                        # Parse tool results based on tool type
                        if tool_name in [
                            "analyze_page_structure",
                            "analyze_content_types",
                        ]:
                            parsed_result["analysis_results"][tool_name] = tool_result

                        elif tool_name in [
                            "detect_temporal_patterns",
                            "extract_dates_from_text",
                            "prioritize_by_temporal_relevance",
                        ]:
                            parsed_result["temporal_results"][tool_name] = tool_result

                        elif tool_name in [
                            "rank_content_by_strategy",
                            "select_top_content",
                            "prioritize_content_final",
                        ]:
                            parsed_result["prioritization_results"][
                                tool_name
                            ] = tool_result

                        elif tool_name in [
                            "extract_html_simple",
                            "extract_html_with_pdfs",
                            "extract_pdf_direct",
                        ]:
                            # Try to parse extraction results
                            if isinstance(tool_result, dict) and "data" in tool_result:
                                parsed_result["data"].extend(tool_result["data"])
                            elif isinstance(tool_result, list):
                                parsed_result["data"].extend(tool_result)

                        elif tool_name == "validate_event_relevance":
                            if isinstance(tool_result, dict) and "data" in tool_result:
                                parsed_result["data"] = tool_result[
                                    "data"
                                ]  # Replace with validated data

                except Exception as e:
                    parsed_result["errors"].append(f"Error parsing step: {str(e)}")

            # Determine final strategy based on what was executed
            if parsed_result["temporal_results"]:
                parsed_result["strategy"] = "temporal_intelligent_extraction"
            elif parsed_result["analysis_results"]:
                parsed_result["strategy"] = "structure_based_extraction"
            else:
                parsed_result["strategy"] = "fallback_extraction"

            return parsed_result

        except Exception as e:
            return {
                "strategy": "parsing_error",
                "data": [],
                "errors": [f"Failed to parse intelligent agent output: {str(e)}"],
                "metadata": {"raw_output": str(result)},
                "analysis_results": {},
                "temporal_results": {},
                "prioritization_results": {},
            }

    def _get_available_strategies(self) -> List[str]:
        """Get list of available intelligent strategies"""
        return [
            "temporal_pdf_analysis",
            "structured_content_extraction",
            "intelligent_prioritization",
            "multi_step_validation",
            "adaptive_strategy_selection",
        ]

    def get_agent_capabilities(self) -> Dict:
        """Get information about agent capabilities"""
        return {
            "total_tools": len(self.available_tools),
            "tool_categories": {
                "analysis": [
                    "analyze_page_structure",
                    "analyze_content_types",
                    "analyze_web_structure",
                ],
                "temporal": [
                    "detect_temporal_patterns",
                    "extract_dates_from_text",
                    "prioritize_by_temporal_relevance",
                ],
                "extraction": [
                    "extract_html_simple",
                    "extract_html_with_pdfs",
                    "extract_pdf_direct",
                    "extract_multiple_pdfs",
                ],
                "prioritization": [
                    "rank_content_by_strategy",
                    "select_top_content",
                    "prioritize_content_final",
                ],
                "validation": ["validate_event_relevance"],
            },
            "intelligent_workflow": True,
            "can_handle_complex_pages": True,
            "supports_temporal_analysis": True,
        }