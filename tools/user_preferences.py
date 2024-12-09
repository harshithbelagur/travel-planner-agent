from langchain.tools import BaseTool
from pydantic import Field
import sqlite3
from typing import Optional

class UserPreferencesTool(BaseTool):
    name: str = "user_info_and_preferences_tool"
    description: str = """This tool contains user data including their name, hometown and user preferences for travel recommendations. 
    This is the first tool to be called."""
    conn: sqlite3.Connection = Field(default_factory=lambda: sqlite3.connect('user_preferences.db', check_same_thread=False), exclude=True)
    cursor: sqlite3.Cursor = Field(default=None, exclude=True)
    
    def __init__(self, **data):
        super().__init__(**data)
        if self.cursor is None:
            self.cursor = self.conn.cursor()
    
    def _get_user_preferences(self, username: str) -> Optional[str]:
        """Check if user exists and return their preferences"""
        self.cursor.execute('SELECT preferences FROM users WHERE username = ?', (username,))
        result = self.cursor.fetchone()
        return result[0] if result else None
    
    def _store_preferences(self, username: str, preferences: str, hometown: str = None) -> None:
        """Store or update user preferences"""
        self.cursor.execute('''
            INSERT INTO users (username, preferences) 
            VALUES (?, ?)
            ON CONFLICT(username) 
            DO UPDATE SET preferences = excluded.preferences
        ''', (username, preferences))
        self.conn.commit()
    
    def _run(self, username: str, preferences: str = None, hometown: str = None) -> str:
        """
        Check if user has preferences, if not prompt for them.
        If preferences are provided, store them.
        Returns the preferences for use with recommendations.
        """
        try:
            # If preferences are provided, store them
            if preferences:
                self._store_preferences(username, preferences, hometown)
                return f"Preferences stored successfully for {username}: {preferences}"
            
            # Otherwise, check for existing preferences
            existing_preferences = self._get_user_preferences(username)
            if existing_preferences:
                return f"Found existing preferences: {existing_preferences}"
            
            # If no preferences found, this message will be sent to the agent
            return "Please tell me about your travel preferences. Consider including:\n" + \
                   "- Activities you enjoy\n" + \
                   "- Climate preferences\n" + \
                   "- Cultural interests\n" + \
                   "- Urban vs. rural settings"
        except Exception as e:
            return f"Error accessing preferences: {str(e)}"

    def update_preferences(self, username: str, new_preferences: str) -> str:
        """Store new user preferences and return confirmation"""
        try:
            self._store_preferences(username, new_preferences)
            return f"Preferences stored successfully for {username}"
        except Exception as e:
            return f"Error storing preferences: {str(e)}"
    
    def __del__(self):
        """Ensure database connection is closed"""
        if hasattr(self, 'conn'):
            self.conn.close()