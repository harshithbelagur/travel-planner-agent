from langchain.tools import BaseTool

class CalculatorTool(BaseTool):
    name: str = "calculator_tool"
    description: str = """
    Performs basic mathematical calculations. Can handle:
    - Addition (+)
    - Subtraction (-)
    - Multiplication (*)
    - Division (/)
    - Exponents (**)
    - Parentheses ()
    
    Input should be a mathematical expression as a string (e.g., "2 + 2" or "(23 * 4.5) / 2").
    """
    
    def _run(self, expression: str) -> str:
        """Execute the calculation"""
        try:
            # Remove any dangerous functions/attributes
            if any(x in expression.lower() for x in ['import', 'eval', 'exec', 'getattr', '__']):
                return "Error: Invalid expression. Please use only basic mathematical operations."
            
            # Calculate the result
            result = eval(expression, {"__builtins__": {}})
            
            # Format the result
            if isinstance(result, (int, float)):
                # Handle integer results
                if result.is_integer():
                    return f"{int(result)}"
                # Format float results to 4 decimal places
                return f"{result:.4f}".rstrip('0').rstrip('.')
            
            return str(result)
            
        except ZeroDivisionError:
            return "Error: Division by zero"
        except Exception as e:
            return f"Error calculating result: {str(e)}"
    
    def _arun(self, expression: str):
        """Async implementation not available"""
        raise NotImplementedError("Async implementation not available")