from langchain.tools import BaseTool
from pydantic import Field
from city_vector_db import CityVectorDB
from sentence_transformers import SentenceTransformer
import sqlite3

class CityRecommendationTool(BaseTool):
    name: str = "city_recommendation_tool"
    description: str = """
    Gets personalized city recommendations based on a user's stored preferences.
    Input should be a username (string) and optionally the number of recommendations (integer).
    Should be called only when we do not know the user's travel destination and not multiple times.
    """
    
    vector_db: CityVectorDB = Field(
        default_factory=CityVectorDB,
        description="Vector database for city matching"
    )
    model: SentenceTransformer = Field(
        default_factory=lambda: SentenceTransformer('all-MiniLM-L6-v2'),
        description="Sentence transformer model for encoding"
    )
    
    def __init__(self, **data):
        super().__init__(**data)
        self.vector_db.load("cities_vector_db")  # Load the saved vector database
    
    def _run(self, user_preferences: str, k: int = 3) -> str:
        """Get city recommendations for a user based on their stored preferences"""
        try:
            # Connect to database
            # with sqlite3.connect('user_preferences.db') as conn:
            #     cursor = conn.cursor()
            #     cursor.execute('SELECT preferences FROM users WHERE username = ?', (username,))
            #     result = cursor.fetchone()
            
            # if not result:
            #     return f"No preferences found for user: {username}. Please store preferences first."
            
            # # Get recommendations using the vector_db's search method
            # user_preferences = result[0]
            # matches = self.vector_db.search(user_preferences, k)
            
            # if not matches:
            #     return "No matching cities found based on your preferences."
            
            # # Format response
            # response = [f"Based on your preferences: '{user_preferences}'\n"]
            # response.append(f"Here are {len(matches)} recommended cities:\n")
            
            # for i, match in enumerate(matches, 1):
            #     response.append(f"{i}. {match['city']}")
            #     response.append(f"   Matching aspects: {match['chunk']}\n")

           
            matches = self.vector_db.search(user_preferences, k)
            
            if not matches:
                return "No matching cities found based on your preferences."
            
            # Format response
            response = [f"Based on your preferences: '{user_preferences}'\n"]
            response.append(f"Here are {len(matches)} recommended cities:\n")
            
            for i, match in enumerate(matches, 1):
                response.append(f"{i}. {match['city']}")
                response.append(f"   Matching aspects: {match['chunk']}\n")
            
            return "\n".join(response)
            
        except Exception as e:
            return f"Error getting recommendations: {str(e)}"
    
    def _arun(self, username: str, k: int = 3) -> str:
        """Async version - Not implemented"""
        raise NotImplementedError("Async implementation not available")