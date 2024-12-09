import requests
import time
from typing import Dict, List, Optional, Tuple
from pydantic import Field
from langchain.tools import BaseTool
import sqlite3
class CityAttractionsTool(BaseTool):
    name: str = "city_attractions_tool"
    description: str = """
    Fetches attractions for a given city from the database and retrieves their coordinates.
    Input should be a city name (string).
    Returns a list of attractions with their details and coordinates.
    """
    conn: sqlite3.Connection = Field(
        default_factory=lambda: sqlite3.connect('user_preferences.db', check_same_thread=False),
        exclude=True
    )
    cursor: sqlite3.Cursor = Field(
        default=None,
        exclude=True
    )
    
    def __init__(self, **data):
        super().__init__(**data)
        if self.cursor is None:
            self.cursor = self.conn.cursor()
    
    def get_coordinates(self, location: str, city: str) -> Optional[Tuple[float, float]]:
        """Get coordinates for a location using Nominatim geocoding service"""
        try:
            # Add city name to make the search more accurate
            search_query = f"{location}, {city}"
            
            # Use Nominatim API with a custom User-Agent
            url = "https://nominatim.openstreetmap.org/search"
            headers = {"User-Agent": "TravelPlannerAgent/1.0"}
            params = {
                "q": search_query,
                "format": "json",
                "limit": 1
            }
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            results = response.json()
            if results:
                lat = float(results[0]["lat"])
                lon = float(results[0]["lon"])
                return (lat, lon)
            
            return None
            
        except Exception as e:
            print(f"Error getting coordinates for {location}: {str(e)}")
            return None
        finally:
            # Be nice to the free API by adding a small delay
            time.sleep(1)
    
    def get_attractions(self, city: str) -> List[Dict]:
        """Get all attractions for a city with their coordinates"""
        try:
            self.cursor.execute('''
                SELECT name, category, description 
                FROM attractions 
                WHERE city = ?
            ''', (city,))
            
            attractions = []
            for name, category, description in self.cursor.fetchall():
                coordinates = self.get_coordinates(name, city)
                attractions.append({
                    "name": name,
                    "category": category,
                    "description": description,
                    "coordinates": coordinates
                })
            
            return attractions
            
        except Exception as e:
            print(f"Error fetching attractions: {str(e)}")
            return []
    
    def _run(self, city: str) -> str:
        """Get attractions with coordinates for a specific city"""
        attractions = self.get_attractions(city)
        
        if not attractions:
            return f"No attractions found for {city}"
        
        # Format response
        response = [f"Attractions in {city}:\n"]
        
        for attraction in attractions:
            response.append(f"- {attraction['name']}")
            response.append(f"  Category: {attraction['category']}")
            response.append(f"  Description: {attraction['description']}")
            if attraction['coordinates']:
                lat, lon = attraction['coordinates']
                response.append(f"  Coordinates: {lat:.4f}° N, {lon:.4f}° E")
            response.append("")  # Empty line for readability
        
        return "\n".join(response)
    
    def _arun(self, city: str) -> str:
        """Async version - Not implemented"""
        raise NotImplementedError("Async implementation not available")
    
    def __del__(self):
        """Clean up database connection"""
        if hasattr(self, 'conn'):
            self.conn.close()