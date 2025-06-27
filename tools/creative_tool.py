from typing import Any, Dict, List

from .base_tool import BaseTool


class CreativeTool(BaseTool):
    """
    A tool that chains other tools in creative ways to solve complex or open-ended tasks.
    Example: screenshot -> OCR -> translate -> search.
    """

    name = "creative_tool"
    description = (
        "Chains other tools in creative ways to solve complex or open-ended tasks."
    )
    capabilities = ["chain_tools", "creative_workflows"]
    version = "1.0"

    def __init__(self):
        super().__init__()

    async def run(self, tool_chain: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """
        Execute a chain of tools. Each item in tool_chain is a dict: {"tool": tool_name, "args": {...}}
        Returns a list of results.
        """
        self.log_usage("run_chain", {"tool_chain": tool_chain})
        results = []
        last_result = None
        for step in tool_chain:
            tool_name = step["tool"]
            args = step.get("args", {})
            # Optionally pass previous result as input
            if last_result is not None:
                args["input"] = last_result
            result = await self.chain(tool_name, **args)
            results.append({"tool": tool_name, "result": result})
            last_result = result
        return {"status": "success", "results": results}
