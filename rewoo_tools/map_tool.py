from pydantic import BaseModel, Field
from typing import List, Tuple, Union
from langchain.tools import BaseTool
import folium
import re

class MapCoordinates(BaseModel):
    input: str = Field(
        ...,
        description="String description of what to plot on the map"
    )

class MapPlottingTool(BaseTool):
    name: str = "map_plotting_tool"
    description: str = """
    Creates an interactive map with markers for specified locations.
    Input should be a text description of what to plot, like:
    "plot attractions in Sydney" or "show hotels in Barcelona"
    
    The tool will extract coordinates from previous tool results and create the map.
    """
    args_schema: type[BaseModel] = MapCoordinates

    def _extract_coordinates(self, input_text: str, previous_results: dict) -> tuple[List[List[float]], List[str]]:
        """Extract coordinates and names from previous results"""
        coordinates = []
        location_names = []
        
        # Look for attraction results in previous steps
        for result in previous_results.values():
            if isinstance(result, str) and "Coordinates:" in result:
                # Split into individual attractions
                attractions = result.split('\n\n')
                
                for attraction in attractions:
                    # Extract name and coordinates using more flexible regex
                    name_match = re.search(r'-\s*([^\n]+)', attraction)
                    coord_match = re.search(r'Coordinates:\s*([-\d.]+)°\s*[NS],\s*([-\d.]+)°\s*[EW]', attraction)
                    
                    if name_match and coord_match:
                        name = name_match.group(1).strip()
                        lat = float(coord_match.group(1))
                        lon = float(coord_match.group(2))
                        coordinates.append([lat, lon])
                        location_names.append(name)
        
        return coordinates, location_names

    def _run(self, input: str, **kwargs) -> str:
        """Create a map with coordinates extracted from previous results"""
        try:
            # Get the state directly from kwargs instead of run_manager
            state = kwargs.get('state', {})
            if not state or 'results' not in state:
                return "Error: No previous results available"
            
            previous_results = state['results']
            
            # Extract coordinates and names
            coordinates, location_names = self._extract_coordinates(input, previous_results)
            
            if not coordinates:
                return "Error: Could not find any coordinates in previous results"

            # Create filename from input
            filename = f"map_{input.replace(' ', '_').replace('=','_')}.html"

            # Create a map centered on the first coordinate
            center_lat = coordinates[0][0]
            center_lon = coordinates[0][1]
            map_location = folium.Map(
                location=[center_lat, center_lon],
                zoom_start=12,
                tiles='OpenStreetMap'
            )

            # Add markers for each coordinate
            for [lat, lon], name in zip(coordinates, location_names):
                folium.Marker(
                    [lat, lon],
                    popup=name,
                    tooltip=f'{name}\nCoordinates: {lat:.4f}, {lon:.4f}'
                ).add_to(map_location)

            # Save the map
            map_location.save(filename)
            return f"Map successfully created with {len(coordinates)} locations and saved as '{filename}'"

        except Exception as e:
            return f"Error creating map: {str(e)}"

    def _arun(self, input: str):
        """Async implementation not available"""
        raise NotImplementedError("Async implementation not available")