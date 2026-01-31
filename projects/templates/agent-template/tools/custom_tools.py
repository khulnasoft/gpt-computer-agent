"""
Custom Tools

Define your custom tools here using the @tool decorator or BaseTool class.
"""

from aideck.agent import BaseTool, ToolResult, tool


@tool(name="example_tool", description="An example custom tool")
def example_tool(input_text: str) -> str:
    """
    An example custom tool that processes input text.

    Args:
        input_text: The text to process

    Returns:
        Processed text
    """
    return f"Processed: {input_text.upper()}"


class CustomAdvancedTool(BaseTool):
    """Example of an advanced custom tool using BaseTool."""

    def __init__(self):
        super().__init__(
            name="advanced_tool",
            description="An advanced custom tool with complex logic",
        )

    async def execute(self, data: str, operation: str = "analyze") -> ToolResult:
        """
        Execute the advanced tool with custom logic.

        Args:
            data: Data to process
            operation: Operation to perform (analyze, transform, validate)

        Returns:
            Tool execution result
        """
        try:
            if operation == "analyze":
                result = f"Analyzed data: {len(data)} characters"
            elif operation == "transform":
                result = f"Transformed: {data[::-1]}"  # Reverse string
            elif operation == "validate":
                result = f"Valid: {bool(data)}"
            else:
                result = f"Unknown operation: {operation}"

            return ToolResult(success=True, data=result)

        except Exception as e:
            return ToolResult(success=False, error=f"Error in advanced tool: {str(e)}")


# Add more custom tools as needed
@tool(name="calculator", description="Perform mathematical calculations")
def calculator(expression: str) -> str:
    """
    Calculate the result of a mathematical expression.

    Args:
        expression: Mathematical expression (e.g., "2 + 3 * 4")

    Returns:
        Calculation result
    """
    try:
        # Safe evaluation (simplified)
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"
