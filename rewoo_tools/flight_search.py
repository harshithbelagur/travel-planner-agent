from langchain.tools import BaseTool
from pydantic import Field, BaseModel, validator
from datetime import datetime
from serpapi import GoogleSearch
import json

class FlightSearchInput(BaseModel):
    input_str: str = Field(..., description="JSON string containing flight search parameters")

    @validator('input_str')
    def validate_and_parse_input(cls, v):
        try:
            # Convert single quotes to double quotes for JSON parsing
            v = v.replace("'", '"')
            data = json.loads(v)
            required_fields = ['departure_airport', 'arrival_airport', 'departure_date']
            if not all(field in data for field in required_fields):
                raise ValueError(f"Missing required fields: {required_fields}")
            return v
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format")

class FlightSearchTool(BaseTool):
    name: str = "flight_search_tool"
    description: str = """
    Searches for flight information between airports. 
    Input should be a JSON string with:
    - departure_airport: IATA code of departure airport (e.g., 'JFK')
    - arrival_airport: IATA code of arrival airport (e.g., 'LAX')
    - departure_date: Date in YYYY-MM-DD format
    - return_date: Optional return date in YYYY-MM-DD format
    """
    args_schema: type[BaseModel] = FlightSearchInput
    api_key: str = Field(..., description="SerpAPI API key")
    
    def _run(self, input_str: str) -> str:
        """Execute the flight search"""
        try:
            # Parse input JSON
            # data = json.loads(input_str.replace("'", '"'))
            data = json.loads(input_str)

            
            # Extract parameters
            departure_airport = data['departure_airport']
            arrival_airport = data['arrival_airport']
            departure_date = data['departure_date']
            return_date = data.get('return_date')
            
            type_num = 2 if return_date is None else 1
            
            search_params = {
                "engine": "google_flights",
                "hl": "en",
                "gl": "us",
                "departure_id": departure_airport,
                "arrival_id": arrival_airport,
                "outbound_date": departure_date,
                "type": type_num,
                "currency": "USD",
                "api_key": self.api_key
            }
            
            if return_date:
                search_params["return_date"] = return_date
            
            # Rest of your existing search code...
            search = GoogleSearch(search_params)
            results = search.get_dict()
            
            # Format the response
            if 'error' in results:
                return f"Error searching flights: {results['error']}"
            
            # Extract relevant flight information
            best_flights = results.get('best_flights', [])
            if not best_flights:
                return "No flights found for the specified criteria."
            
            # Format response
            response = "Found the following flights:\n"
            for flight in best_flights[:1]:  # Show just 1 result
                price = flight.get('price', 'N/A')
                duration = flight.get('total_duration', 'N/A')
                airline = flight['flights'][0].get('airline', 'N/A')
                departure_time = flight['flights'][0]['departure_airport'].get('time', 'N/A')
                arrival_time = flight['flights'][0]['arrival_airport'].get('time', 'N/A')
                
                response += f"- {airline}: ${price}, Duration: {duration}min ({departure_time} - {arrival_time})\n"
            
            return response
            
        except Exception as e:
            return f"Error processing flight search: {str(e)}"