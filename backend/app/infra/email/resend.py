import logging
import base64
import resend
from .base import EmailServiceBase, EmailMessage
from .exceptions import (
    EmailServiceError, 
    EmailServiceConnectionError, 
    EmailServiceRateLimitError,
    EmailServiceAuthenticationError,
    EmailServiceQuotaExceededError
)

logger = logging.getLogger(__name__)


class ResendEmailService(EmailServiceBase):
    
    def __init__(self, sender_email: str, api_key: str):
        self.sender_email = sender_email
        self.api_key = api_key
        if not resend.api_key:
            resend.api_key = api_key
    
    async def send_email(self, message: EmailMessage) -> bool:
        try:
            params: resend.Emails.SendParams = {
                "from": f"Vellora <{self.sender_email}>",
                "to": [r.email for r in message.recipients],
                "subject": message.subject,
            }
            
            if message.html_body:
                params["html"] = message.html_body
            if message.text_body:
                params["text"] = message.text_body
            
            if message.reply_to:
                params["reply_to"] = [message.reply_to]
            
            if message.attachments:
                attachments_list = []
                for att in message.attachments:
                    attachment_data = {
                        "filename": att.filename,
                        "content": base64.b64encode(att.content).decode('utf-8'),
                        "content_type": att.content_type
                    }
                    if att.content_id:
                        attachment_data["content_id"] = att.content_id
                    attachments_list.append(attachment_data)
                params["attachments"] = attachments_list
            
            response = resend.Emails.send(params)
            
            if isinstance(response, dict) and response.get('id'):
                email_id = response.get('id', 'unknown')
                logger.info(f"Resend email sent successfully (ID: {email_id}) to {len(message.recipients)} recipients")
                return True
            elif hasattr(response, 'id'):
                email_id = response.id
                logger.info(f"Resend email sent successfully (ID: {email_id}) to {len(message.recipients)} recipients")
                return True
            else:
                logger.error(f"Resend SDK returned unexpected response: {response}")
                raise EmailServiceError("Resend SDK returned unexpected response")
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Resend SDK error: {error_msg}")
            
            #map specific error types based on Resend SDK error thingy
            if "timeout" in error_msg.lower() or "connection" in error_msg.lower():
                raise EmailServiceConnectionError(f"Email service connection failed: {error_msg}")
            elif "rate limit" in error_msg.lower() or "429" in error_msg or "too many requests" in error_msg.lower():
                raise EmailServiceRateLimitError(f"Email service rate limit exceeded: {error_msg}")
            elif "unauthorized" in error_msg.lower() or "401" in error_msg or "api key" in error_msg.lower():
                raise EmailServiceAuthenticationError(f"Email service authentication failed: {error_msg}")
            elif "quota" in error_msg.lower() or "limit exceeded" in error_msg.lower():
                raise EmailServiceQuotaExceededError(f"Email service quota exceeded: {error_msg}")
            else:
                raise EmailServiceError(f"Email service failed: {error_msg}")
    
    async def verify_sender_email(self, email: str) -> bool:
        try:
            sender_domain = email.split('@')[1]
            if sender_domain == 'resend.dev':
                logger.info(f"Using Resend test domain: {sender_domain}")
                return True
            
            domains_response = resend.Domains.list()
            
            #extract domains list from response
            domains = []
            if hasattr(domains_response, 'data'):
                domains = domains_response.data
            elif isinstance(domains_response, list):
                domains = domains_response
            elif isinstance(domains_response, dict) and 'data' in domains_response:
                domains = domains_response['data']
            
            #check if domain is verified
            for domain in domains:
                domain_name = domain.name if hasattr(domain, 'name') else domain.get('name', '')
                domain_status = domain.status if hasattr(domain, 'status') else domain.get('status', '')
                
                if domain_name == sender_domain and domain_status == 'verified':
                    logger.info(f"Domain {sender_domain} is verified in Resend")
                    return True
            
            logger.warning(f"Domain {sender_domain} not found or not verified in Resend")
            return False
                
        except Exception as e:
            logger.error(f"Resend domain verification failed: {e}")
            return False
    
    def get_sender_email(self) -> str:
        return self.sender_email