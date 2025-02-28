import os
import requests
import json
import datetime
from dotenv import load_dotenv
import logging

# Import knowledge base
from services.knowledge_base import get_knowledge_base

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ai_assistant")

class ThomasAIAssistant:
    """Thomas AI assistant that interacts with OpenAI's API"""
    
    def __init__(self):
        """Initialize the assistant with API key and system prompt"""
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = "gpt-4" if os.getenv("USE_GPT4", "false").lower() == "true" else "gpt-3.5-turbo"
        
        # Enhanced system prompt that defines Thomas's capabilities for game development
        self.system_prompt = """
        You are Thomas, an AI Chief Operating Officer for a game development company. You are an expert in:
        
        1. Game design principles and industry best practices
        2. Financial tracking and budget management for game projects
        3. Project planning and coordination for game development lifecycles
        4. Asset development monitoring and pipeline optimization
        5. Team management and resource allocation for game studios
        
        Your responses should be professional, data-driven, and focused on helping the company succeed.
        When discussing financial matters, be precise and analytical.
        When discussing creative aspects, be supportive and thoughtful with industry-informed insights.
        
        You have access to company data including projects, payments, employees, and assets.
        When this data is provided, use it to give specific, actionable insights based on game industry standards.
        
        Always provide your reasoning and calculations when making financial recommendations.
        
        For game design questions, draw upon knowledge of successful game mechanics, monetization models,
        player retention strategies, and platform-specific considerations.
        """
        
        # Initialize conversation history with system prompt
        self.conversation_history = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # Initialize knowledge base
        try:
            self.knowledge_base = get_knowledge_base()
            # Initialize with sample data if the database is empty
            self.knowledge_base.initialize_with_sample_data()
            logger.info("Knowledge base initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing knowledge base: {str(e)}")
            self.knowledge_base = None
    
    def ask(self, question, include_data=None):
        """
        Ask a question to Thomas AI
        
        Args:
            question (str): The user's question
            include_data (dict, optional): Context data to include in the prompt
            
        Returns:
            str: Thomas AI's response
        """
        # Get relevant knowledge from the knowledge base
        knowledge_context = ""
        if self.knowledge_base:
            try:
                knowledge_context = self.knowledge_base.get_knowledge_for_context(question)
                if knowledge_context:
                    # Add the knowledge context to the conversation
                    self.conversation_history.append({"role": "system", "content": knowledge_context})
                    logger.info("Added knowledge context to the conversation")
            except Exception as e:
                logger.error(f"Error getting knowledge context: {str(e)}")
        
        # If context data is provided, format it for the assistant
        if include_data:
            # Create a formatted data summary
            data_context = "Here's some relevant company data to consider:\n\n"
            
            # Format projects data
            if "projects" in include_data and include_data["projects"]:
                data_context += "## Projects\n"
                for project in include_data["projects"]:
                    data_context += f"- {project.get('name', 'Unnamed')}: "
                    data_context += f"Budget ${project.get('total_budget', 0):,.2f}, "
                    data_context += f"Timeline: {project.get('start_date', 'N/A')} to {project.get('end_date', 'N/A')}\n"
                data_context += "\n"
            
            # Format payment summary data
            if "payments" in include_data and include_data["payments"]:
                payments = include_data["payments"]
                total_usd = sum(p.get("amount", 0) for p in payments if p.get("currency") == "USD")
                total_sol = sum(p.get("amount", 0) for p in payments if p.get("currency") == "SOL")
                
                data_context += "## Payment Summary\n"
                data_context += f"- Total USD payments: ${total_usd:,.2f}\n"
                data_context += f"- Total SOL payments: {total_sol:,.2f} SOL\n"
                data_context += f"- Total payments in USD equivalent: ${total_usd + (total_sol * 150):,.2f} (using rate of 1 SOL = $150 USD)\n"
                data_context += f"- Number of payments: {len(payments)}\n\n"
            
            # Add employee info if available
            if "employees" in include_data and include_data["employees"]:
                data_context += "## Team Members\n"
                for employee in include_data["employees"]:
                    data_context += f"- {employee}\n"
                data_context += "\n"
            
            # Add detailed employee payment info if available
            if "employee_payments" in include_data and include_data["employee_payments"]:
                data_context += "## Detailed Employee Payments\n"
                for employee, payments in include_data["employee_payments"].items():
                    total_usd = sum(p.get("amount", 0) for p in payments if p.get("currency") == "USD")
                    total_sol = sum(p.get("amount", 0) for p in payments if p.get("currency") == "SOL")
                    
                    data_context += f"- {employee}: ${total_usd:,.2f} USD, {total_sol:,.2f} SOL\n"
                data_context += "\n"
            
            # Add asset info if available
            if "assets" in include_data and include_data["assets"]:
                data_context += "## Asset Status\n"
                assets_by_status = {}
                for asset in include_data["assets"]:
                    status = asset.get("status", "unknown")
                    if status not in assets_by_status:
                        assets_by_status[status] = 0
                    assets_by_status[status] += 1
                
                for status, count in assets_by_status.items():
                    data_context += f"- {status.capitalize()}: {count} assets\n"
                data_context += "\n"
            
            # Add the data context to the conversation
            self.conversation_history.append({"role": "system", "content": data_context})
        
        # Add the user question to the conversation
        self.conversation_history.append({"role": "user", "content": question})
        
        # API key validation with helpful error message
        if not self.api_key:
            return "⚠️ Error: OpenAI API key is not set. Please add your API key to the .env file with the format: OPENAI_API_KEY=your_api_key_here"
        
        if self.api_key.startswith("sk-"):
            # Key has correct prefix format
            pass
        else:
            return "⚠️ Error: The OpenAI API key format is incorrect. It should start with 'sk-'. Please check your API key in the .env file."
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": self.conversation_history,
                "temperature": 0.7
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                response_data = response.json()
                answer = response_data["choices"][0]["message"]["content"]
                
                # Add the assistant's response to the conversation history
                self.conversation_history.append({"role": "assistant", "content": answer})
                
                # Keep conversation history manageable (max 10 exchanges)
                if len(self.conversation_history) > 21:  # system prompt + data context + 10 exchanges
                    # Keep system prompt and last 10 exchanges
                    self.conversation_history = [self.conversation_history[0]] + self.conversation_history[-20:]
                
                # Store this Q&A in knowledge base if it's relevant to game design
                self._potentially_save_to_knowledge_base(question, answer)
                
                return answer
            elif response.status_code == 401:
                return "⚠️ Authentication Error: The API key you provided is invalid. Please check your API key in the .env file and make sure it's current. You can find your API key at https://platform.openai.com/account/api-keys."
            elif response.status_code == 429:
                return "⚠️ Rate Limit Error: The API request has been rate limited. This might be due to exceeding your quota or hitting the rate limits. Check your usage at https://platform.openai.com/account/usage."
            elif response.status_code == 500:
                return "⚠️ Server Error: OpenAI's servers are experiencing issues. Please try again later."
            else:
                return f"⚠️ Error: API returned status code {response.status_code}. {response.text}"
                
        except requests.exceptions.ConnectionError:
            return "⚠️ Connection Error: Could not connect to OpenAI's API. Please check your internet connection."
        except requests.exceptions.Timeout:
            return "⚠️ Timeout Error: The request to OpenAI's API timed out. Please try again later."
        except Exception as e:
            return f"⚠️ Error connecting to OpenAI API: {str(e)}"
    
    def _potentially_save_to_knowledge_base(self, question, answer):
        """
        Analyze the Q&A to determine if it should be saved to the knowledge base
        
        Args:
            question (str): The user's question
            answer (str): Thomas AI's response
        """
        if not self.knowledge_base:
            return
        
        # Keywords that suggest game design relevance
        game_design_keywords = [
            "game design", "mechanics", "gameplay", "player retention", "monetization", 
            "engagement", "level design", "game balance", "progression system",
            "game loop", "core loop", "metagame", "game economy", "difficulty curve"
        ]
        
        # Check if the Q&A is related to game design
        is_game_design_related = False
        for keyword in game_design_keywords:
            if keyword.lower() in question.lower() or keyword.lower() in answer.lower():
                is_game_design_related = True
                break
        
        if not is_game_design_related:
            return
        
        try:
            # Use OpenAI to classify the content and extract key concepts
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            analysis_prompt = f"""
            Analyze this game development Q&A and determine if it contains valuable game design knowledge worth preserving:
            
            Question: {question}
            
            Answer: {answer}
            
            If it contains valuable game design knowledge, extract the key concept name and description.
            Format your response as JSON:
            
            {{
                "is_valuable": true/false,
                "concept_type": "game_design_concepts" or "industry_practices" or "educational_resources" or "market_research",
                "name": "Name of the concept",
                "description": "Clear description of the concept",
                "category": "Relevant category",
                "tags": "comma, separated, tags"
            }}
            
            Only return the JSON, nothing else.
            """
            
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": analysis_prompt}],
                "temperature": 0.3
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                response_data = response.json()
                analysis_text = response_data["choices"][0]["message"]["content"]
                
                try:
                    # Extract the JSON from the response
                    if '{' in analysis_text and '}' in analysis_text:
                        json_str = analysis_text[analysis_text.find('{'):analysis_text.rfind('}')+1]
                        analysis = json.loads(json_str)
                    else:
                        analysis = json.loads(analysis_text)
                    
                    # Save to knowledge base if valuable
                    if analysis.get("is_valuable", False):
                        concept_type = analysis.get("concept_type", "game_design_concepts")
                        
                        if concept_type == "game_design_concepts":
                            self.knowledge_base.add_design_concept({
                                "concept_name": analysis.get("name", "Unnamed Concept"),
                                "description": analysis.get("description", ""),
                                "category": analysis.get("category", "General"),
                                "tags": analysis.get("tags", ""),
                                "source": "Thomas AI Q&A"
                            })
                            logger.info(f"Added new game design concept to knowledge base: {analysis.get('name', 'Unnamed')}")
                        
                        elif concept_type == "industry_practices":
                            self.knowledge_base.add_industry_practice({
                                "practice_name": analysis.get("name", "Unnamed Practice"),
                                "description": analysis.get("description", ""),
                                "category": analysis.get("category", "General"),
                                "tags": analysis.get("tags", ""),
                                "source": "Thomas AI Q&A"
                            })
                            logger.info(f"Added new industry practice to knowledge base: {analysis.get('name', 'Unnamed')}")
                        
                        elif concept_type == "educational_resources":
                            self.knowledge_base.add_educational_resource({
                                "title": analysis.get("name", "Unnamed Resource"),
                                "content_type": "Q&A",
                                "description": analysis.get("description", ""),
                                "category": analysis.get("category", "General"),
                                "tags": analysis.get("tags", ""),
                                "summary": f"Q: {question}\nA: {answer}"
                            })
                            logger.info(f"Added new educational resource to knowledge base: {analysis.get('name', 'Unnamed')}")
                        
                        elif concept_type == "market_research":
                            self.knowledge_base.add_market_research({
                                "title": analysis.get("name", "Unnamed Research"),
                                "key_findings": analysis.get("description", ""),
                                "source": "Thomas AI Q&A"
                            })
                            logger.info(f"Added new market research to knowledge base: {analysis.get('name', 'Unnamed')}")
                
                except json.JSONDecodeError:
                    logger.error(f"Error decoding analysis JSON: {analysis_text}")
                except Exception as e:
                    logger.error(f"Error processing knowledge analysis: {str(e)}")
        
        except Exception as e:
            logger.error(f"Error in knowledge extraction: {str(e)}")
    
    def add_game_design_knowledge(self, knowledge_type, data):
        """
        Add specific game design knowledge to the knowledge base
        
        Args:
            knowledge_type (str): Type of knowledge ('concept', 'practice', 'resource', 'research')
            data (dict): The knowledge data
            
        Returns:
            bool: Success status
        """
        if not self.knowledge_base:
            return False
        
        try:
            if knowledge_type == 'concept':
                self.knowledge_base.add_design_concept(data)
            elif knowledge_type == 'practice':
                self.knowledge_base.add_industry_practice(data)
            elif knowledge_type == 'resource':
                self.knowledge_base.add_educational_resource(data)
            elif knowledge_type == 'research':
                self.knowledge_base.add_market_research(data)
            else:
                return False
            
            return True
        except Exception as e:
            logger.error(f"Error adding knowledge: {str(e)}")
            return False
    
    def reset_conversation(self):
        """Reset the conversation history"""
        self.conversation_history = [
            {"role": "system", "content": self.system_prompt}
        ]
        return "Conversation has been reset."
