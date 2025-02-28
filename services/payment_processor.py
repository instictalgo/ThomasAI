import os
import requests
import json
from datetime import datetime
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class PayPalProcessor:
    def __init__(self):
        self.client_id = os.getenv("PAYPAL_CLIENT_ID")
        self.client_secret = os.getenv("PAYPAL_CLIENT_SECRET")
        self.base_url = "https://api-m.sandbox.paypal.com" if os.getenv("PAYPAL_SANDBOX", "true").lower() == "true" else "https://api-m.paypal.com"
        self.access_token = None
        self.token_expiry = None
    
    def _get_access_token(self):
        """Get OAuth access token from PayPal"""
        if self.access_token and self.token_expiry and self.token_expiry > datetime.now():
            return self.access_token
        
        url = f"{self.base_url}/v1/oauth2/token"
        headers = {
            "Accept": "application/json",
            "Accept-Language": "en_US"
        }
        data = {
            "grant_type": "client_credentials"
        }
        
        response = requests.post(
            url, 
            auth=(self.client_id, self.client_secret),
            headers=headers,
            data=data
        )
        
        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data["access_token"]
            # Set expiry time (subtract 60 seconds to be safe)
            expires_in = token_data["expires_in"] - 60
            self.token_expiry = datetime.now() + datetime.timedelta(seconds=expires_in)
            return self.access_token
        else:
            raise Exception(f"Failed to get PayPal access token: {response.text}")
    
    def create_payment(self, amount, currency, employee_id, description=None):
        """Create a PayPal payout to an employee's PayPal email"""
        token = self._get_access_token()
        
        # Generate a unique batch ID for this payout
        batch_id = f"THOMAS_PAYOUT_{str(uuid.uuid4())[:8]}"
        
        url = f"{self.base_url}/v1/payments/payouts"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        payload = {
            "sender_batch_header": {
                "sender_batch_id": batch_id,
                "email_subject": "Payment from Your Company",
                "email_message": description or f"Payment of {amount} {currency} from Your Company"
            },
            "items": [
                {
                    "recipient_type": "EMAIL",
                    "amount": {
                        "value": str(amount),
                        "currency": currency
                    },
                    "note": f"Payment for employee {employee_id}",
                    "receiver": employee_id,  # Assuming employee_id is the PayPal email
                    "sender_item_id": f"PAYMENT_{str(uuid.uuid4())[:8]}"
                }
            ]
        }
        
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        if response.status_code in (200, 201):
            return {
                "success": True,
                "payout_batch_id": response.json().get("batch_header", {}).get("payout_batch_id"),
                "status": response.json().get("batch_header", {}).get("batch_status")
            }
        else:
            return {
                "success": False,
                "error": response.text
            }
    
    def get_payment_status(self, payout_batch_id):
        """Check the status of a payout"""
        token = self._get_access_token()
        
        url = f"{self.base_url}/v1/payments/payouts/{payout_batch_id}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return {
                "success": True,
                "status": response.json().get("batch_header", {}).get("batch_status"),
                "details": response.json()
            }
        else:
            return {
                "success": False,
                "error": response.text
            }

class CryptoProcessor:
    def __init__(self):
        # In a production system, you might integrate with a crypto payment provider
        # For demonstration, we'll simulate crypto payments
        pass
    
    def generate_payment_request(self, amount, currency, wallet_address=None):
        """
        Generate a simulated crypto payment request
        In a real implementation, this would create a request with an actual crypto wallet
        """
        if currency.lower() not in ("btc", "eth", "usdt"):
            raise ValueError(f"Unsupported cryptocurrency: {currency}")
        
        # Generate a simulated wallet address if none provided
        if not wallet_address:
            if currency.lower() == "btc":
                wallet_address = f"bc1q{uuid.uuid4().hex[:34]}"
            elif currency.lower() == "eth":
                wallet_address = f"0x{uuid.uuid4().hex[:40]}"
        
        # Generate a fake transaction ID
        transaction_id = f"{currency.lower()}_tx_{uuid.uuid4().hex[:16]}"
        
        return {
            "payment_address": wallet_address,
            "amount": amount,
            "currency": currency.upper(),
            "transaction_id": transaction_id,
            "status": "pending",
            "instructions": f"Please send {amount} {currency.upper()} to {wallet_address}",
            "expiry": (datetime.now() + datetime.timedelta(hours=24)).isoformat()
        }
    
    def check_transaction_status(self, transaction_id):
        """
        Check status of a crypto transaction
        In a real implementation, this would query the blockchain or a crypto payment provider
        """
        # Simulate random status for demo purposes
        import random
        statuses = ["pending", "confirmed", "completed", "failed"]
        status = random.choice(statuses)
        
        return {
            "transaction_id": transaction_id,
            "status": status,
            "confirmations": random.randint(0, 6) if status != "failed" else 0,
            "checked_at": datetime.now().isoformat()
        } 