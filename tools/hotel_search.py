from langchain.tools import BaseTool
from pydantic import Field, BaseModel
from datetime import datetime
from serpapi import GoogleSearch

class HotelSearchInput(BaseModel):
    destination: str = Field(..., description="Name of destination city/area (e.g., 'Bali Resorts')")
    check_in_date: str = Field(..., description="Check-in date in YYYY-MM-DD format")
    check_out_date: str = Field(..., description="Check-out date in YYYY-MM-DD format")
    
class HotelSearchTool(BaseTool):
    name: str = "hotel_search_tool"
    description: str = """
    Searches for hotels at a given destination.
    Input should be a dictionary with:
    - destination: Name of destination city/area (e.g., 'Bali Resorts')
    - check_in_date: Date in YYYY-MM-DD format
    - check_out_date: Date in YYYY-MM-DD format
    """
    args_schema: type[BaseModel] = HotelSearchInput
    api_key: str = Field(..., description="SerpAPI API key")
    
    def _run(self, destination: str, check_in_date: str, check_out_date: str) -> str:
        """Execute the hotel search"""
        try:
            # Validate dates
            if not (self._validate_date(check_in_date) and self._validate_date(check_out_date)):
                return "Error: Please provide valid future dates in YYYY-MM-DD format."
            
            search_params = {
                "api_key": self.api_key,
                "engine": "google_hotels",
                "q": destination,
                "hl": "en",
                "gl": "us",
                "check_in_date": check_in_date,
                "check_out_date": check_out_date,
                "currency": "USD"
            }
            
            search = GoogleSearch(search_params)
            results = search.get_dict()
            
            # Format the response
            if 'error' in results:
                return f"Error searching hotels: {results['error']}"
            
            # Extract hotel information
            hotels = results.get('properties', [])
            if not hotels:
                return f"No hotels found in {destination} for the specified dates."
            
            # Format response
            response = f"Found the following hotels in {destination}:\n\n"
            for hotel in hotels[:5]:  # Show top 5 results
                name = hotel.get('name', 'N/A')
                price_per_night_lowest = hotel.get('rate_per_night', {}).get('lowest', 'N/A')
                total_price_lowest = hotel.get('total_rate', {}).get('lowest', 'N/A')
                rating = hotel.get('overall_rating', 'N/A')
                reviews = hotel.get('reviews', 'N/A')
                description = hotel.get('essential_info', 'No description available')
                latitude = hotel.get('gps_coordinates', {}).get('latitude', 'N/A')
                longitude = hotel.get('gps_coordinates', {}).get('longitude', 'N/A')
                
                response += f"🏨 {name}\n"
                response += f"   Price: {total_price_lowest} total for your stay\n"
                response += f"   Rating: {rating}/5 ({reviews} reviews)\n"
                response += f"   Description: {description[:200]}...\n\n"
                response += f"   Address: {str(latitude) + ", " + str(longitude)}\n\n"
            
            return response
            
        except Exception as e:
            return f"Error processing hotel search: {str(e)}"

    def _arun(self, query: str):
        raise NotImplementedError("Async implementation not available")
    
    def _validate_date(self, date_str: str) -> bool:
        """Validate date format and ensure it's not in the past"""
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d')
            return date >= datetime.now()
        except ValueError:
            return False