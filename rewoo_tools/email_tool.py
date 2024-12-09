from langchain.tools import BaseTool
from pydantic import Field, BaseModel
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Dict, Optional
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import json
import os

class EmailItineraryInput(BaseModel):
    """Input schema for the Gmail Itinerary Tool"""
    to_email: str
    username: Optional[str] = None
    flight_details: List[Dict]
    hotel_details: Optional[Dict] = None
    attractions: List[Dict]
    html_file_path: Optional[str] = None

class EmailItineraryTool(BaseTool):
    name: str = "gmail_itinerary_tool"
    description: str = """
    Sends an itinerary email including flights, hotel, points of attraction, and a map using Gmail.
    The input should be a JSON string containing:
    {
        "to_email": "recipient's email",
        "username": "traveler's name",
        "flight_details": [list of flight information],
        "hotel_details": {hotel booking information},
        "attractions": [list of attractions],
        "map_url": "optional map URL"
    }
    """
    
    smtp_server: str = Field(default="smtp.gmail.com")
    smtp_port: int = Field(default=587)
    smtp_user: str = Field(default="your.email@gmail.com")
    smtp_password: str = Field(default="your-app-password")

    def format_itinerary_email(self, data: EmailItineraryInput) -> str:
        """Format the email body with itinerary details"""
        
        email_body = f"""
Dear {data.username},

Thank you for booking your trip! Here's your complete itinerary:

FLIGHT DETAILS:
"""
        # Add flight details
        for flight in data.flight_details:
            email_body += f"""
🛫 {flight.get('airline', 'Airline')} - ${flight.get('price', 'N/A')}
   Departure: {flight.get('departure_time', 'N/A')}
   Arrival: {flight.get('arrival_time', 'N/A')}
   Duration: {flight.get('duration', 'N/A')} minutes
"""

        # Add hotel details
        email_body += f"""
HOTEL DETAILS:
🏨 {data.hotel_details.get('name', 'Hotel Name')}
   Address: {data.hotel_details.get('address', 'N/A')}
   Price: {data.hotel_details.get('price', 'N/A')}
"""

        # Add attractions
        email_body += """
POINTS OF INTEREST:
"""
        for attraction in data.attractions:
            email_body += f"""
🎯 {attraction.get('name', 'Attraction Name')}
"""

        if data.map_url:
            email_body += f"""
MAP:
🗺️ View your trip map here: {data.map_url}
"""

        email_body += """

Have a great trip!
Best regards,
Fred, Your Travel Assistant
"""
        return email_body

    def _run(self, tool_input: str) -> str:
        """Execute the email sending tool"""
        try:
            # Parse the input JSON string into a dictionary
            if isinstance(tool_input, str):
                input_data = json.loads(tool_input)
            else:
                input_data = tool_input
                
            # Convert to GmailItineraryInput
            data = EmailItineraryInput(**input_data)

            # Create the email
            msg = MIMEMultipart()
            msg['From'] = self.smtp_user
            msg['To'] = data.to_email
            msg['Subject'] = f"Your Travel Itinerary - {datetime.now().strftime('%B %d, %Y')}"

            # Format and attach the body text
            body = self.format_itinerary_email(data)
            msg.attach(MIMEText(body, 'plain'))

            if data.html_file_path and os.path.exists(data.html_file_path):
                with open(data.html_file_path, 'rb') as attachment:
                    part = MIMEBase('text', 'html')
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    
                    # Add header to attachment
                    filename = os.path.basename(data.html_file_path)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {filename}'
                    )
                    msg.attach(part)

            # Send the email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            return f"Itinerary email sent successfully to {data.to_email}"

        except Exception as e:
            return f"Error sending email: {str(e)}"

    def _arun(self, tool_input: str) -> str:
        raise NotImplementedError("Async version not implemented")

# Example usage
def create_gmail_tool(gmail_address: str, app_password: str) -> EmailItineraryTool:
    return EmailItineraryTool(
        smtp_user=gmail_address,
        smtp_password=app_password
    )