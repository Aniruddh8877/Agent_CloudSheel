import json
import logging
import asyncio
from typing import AsyncGenerator, Dict, Any, List

from google import genai
from google.genai import types
from google.genai.errors import APIError

from app.config import settings
from app.tools import ALL_TOOL_FUNCTIONS, TOOL_REGISTRY
from app.agent.prompts import SYSTEM_INSTRUCTION

logger = logging.getLogger("agent.core")

class AgentRunner:
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or settings.get_api_key()
        self.model = model or settings.model

    async def run_stream(self, messages: List[Dict[str, str]], temperature: float = 0.3) -> AsyncGenerator[str, None]:
        """
        Runs the agent ReAct tool-use loop and yields SSE event strings:
        - data: {"type": "status", "content": "..."}
        - data: {"type": "tool_call", "name": "...", "args": {...}}
        - data: {"type": "tool_result", "name": "...", "result": "..."}
        - data: {"type": "chunk", "content": "..."}
        - data: {"type": "done", "status": "completed"}
        - data: {"type": "error", "message": "..."}
        """
        def format_sse(data: dict) -> str:
            return f"data: {json.dumps(data)}\n\n"

        if not self.api_key:
            yield format_sse({
                "type": "error",
                "message": (
                    "**Gemini API Key Required**\n\n"
                    "To enable live web search and task execution, please provide your Google Gemini API key:\n\n"
                    "1. Click the **Settings** gear icon in the top-right header.\n"
                    "2. Paste your API key (get a free key at [Google AI Studio](https://aistudio.google.com/)).\n"
                    "3. Click **Save Settings** and try again!"
                )
            })
            yield format_sse({"type": "done", "status": "error"})
            return

        yield format_sse({"type": "status", "content": "Initializing agent..."})

        try:
            client = genai.Client(api_key=self.api_key)
        except Exception as e:
            yield format_sse({"type": "error", "message": f"Client initialization error: {str(e)}"})
            yield format_sse({"type": "done", "status": "error"})
            return

        # Prepare chat contents
        contents: List[types.Content] = []
        for msg in messages:
            role = "user" if msg.get("role") == "user" else "model"
            text = msg.get("content", "")
            if text:
                contents.append(types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=text)]
                ))

        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            tools=ALL_TOOL_FUNCTIONS,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            temperature=temperature,
        )

        max_iterations = 8
        current_iteration = 0

        try:
            while current_iteration < max_iterations:
                current_iteration += 1

                yield format_sse({"type": "status", "content": "Thinking..."})

                # Run model generation in thread pool to keep asyncio responsive
                response = await asyncio.to_thread(
                    client.models.generate_content,
                    model=self.model,
                    contents=contents,
                    config=config
                )

                # Check if the model requested function execution
                function_calls = getattr(response, "function_calls", None)

                if function_calls:
                    # Model issued tool calls
                    # First, add the model's candidate parts to contents to keep the conversation valid
                    model_parts = []
                    if response.candidates and response.candidates[0].content:
                        model_parts = response.candidates[0].content.parts

                    contents.append(types.Content(
                        role="model",
                        parts=model_parts
                    ))

                    # Process each function call
                    for call in function_calls:
                        fn_name = call.name
                        fn_args = dict(call.args) if call.args else {}

                        yield format_sse({
                            "type": "tool_call",
                            "name": fn_name,
                            "args": fn_args,
                            "content": f"Executing tool: {fn_name}"
                        })

                        # Execute the tool
                        tool_func = TOOL_REGISTRY.get(fn_name)
                        if tool_func:
                            try:
                                yield format_sse({"type": "status", "content": f"Running {fn_name}..."})
                                result_str = await asyncio.to_thread(tool_func, **fn_args)
                            except Exception as tool_err:
                                result_str = f"Tool execution failed with error: {str(tool_err)}"
                        else:
                            result_str = f"Error: Tool '{fn_name}' is not registered."

                        yield format_sse({
                            "type": "tool_result",
                            "name": fn_name,
                            "result": str(result_str)[:2000] # preview in UI
                        })

                        # Append tool response turn to contents
                        contents.append(types.Content(
                            role="user",
                            parts=[types.Part.from_function_response(
                                name=fn_name,
                                response={"result": str(result_str)}
                            )]
                        ))

                    # Continue loop to allow model to synthesize or call next tool
                    continue

                else:
                    # No function calls: this is the final answer!
                    answer_text = response.text or ""
                    
                    # Stream the text in chunks for a smooth, natural reading experience
                    chunk_size = 20
                    for i in range(0, len(answer_text), chunk_size):
                        chunk = answer_text[i:i + chunk_size]
                        yield format_sse({
                            "type": "chunk",
                            "content": chunk
                        })
                        await asyncio.sleep(0.015)

                    break

            yield format_sse({"type": "done", "status": "completed"})

        except APIError as api_err:
            logger.error(f"Gemini API Error: {api_err}")
            yield format_sse({
                "type": "error",
                "message": f"Gemini API Error: {api_err.message if hasattr(api_err, 'message') else str(api_err)}"
            })
            yield format_sse({"type": "done", "status": "error"})
        except Exception as e:
            logger.error(f"Unexpected error in agent runner: {e}", exc_info=True)
            yield format_sse({
                "type": "error",
                "message": f"An error occurred: {str(e)}"
            })
            yield format_sse({"type": "done", "status": "error"})
