import os
import requests
import json
import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ThomasAIAssistant:
    """Thomas AI assistant that interacts with OpenAI's API"""
    
    def __init__(self):
        """Initialize the assistant with API key and system prompt"""
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = "gpt-4" if os.getenv("USE_GPT4", "false").lower() == "true" else "gpt-3.5-turbo"
        
        # System prompt that defines Thomas's capabilities and personality
        self.system_prompt = """
        You are Thomas, an AI assistant for a Roblox game development company. You help the management team with:
        
        1. Financial tracking and budget management
        2. Project planning and coordination
        3. Asset development monitoring
        4. Team management and resource allocation
        
        Your responses should be professional, data-driven, and focused on helping the company succeed.
        When discussing financial matters, be precise and analytical.
        When discussing creative aspects, be supportive and thoughtful.
        
        You have access to company data including projects, payments, employees, and assets.
        When this data is provided, use it to give specific, actionable insights.
        
        Always provide your reasoning and calculations when making financial recommendations.
        """
        
        # Initialize conversation history with system prompt
        self.conversation_history = [
            {"role": "system", "content": self.system_prompt}
        ]
    
    def ask(self, question, include_data=None):
        """
        Ask a question to Thomas AI
        
        Args:
            question (str): The user's question
            include_data (dict, optional): Context data to include in the prompt
            
        Returns:
            str: Thomas AI's response
        """
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
        
        # Send the conversation to OpenAI API
        if not self.api_key:
            return "Error: OpenAI API key is not set. Please add your API key to the .env file."
        
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
                
                return answer
            else:
                return f"Error: API returned status code {response.status_code}. {response.text}"
                
        except Exception as e:
            return f"Error connecting to OpenAI API: {str(e)}"
    
    def reset_conversation(self):
        """Reset the conversation history"""
        self.conversation_history = [
            {"role": "system", "content": self.system_prompt}
        ]
        return "Conversation has been reset."
