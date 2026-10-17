import math
import datetime
import json
import statistics
import re

SAFE_GLOBALS = {
    "__builtins__": {
        "abs": abs,
        "all": all,
        "any": any,
        "bin": bin,
        "bool": bool,
        "chr": chr,
        "dict": dict,
        "divmod": divmod,
        "enumerate": enumerate,
        "float": float,
        "format": format,
        "hex": hex,
        "int": int,
        "isinstance": isinstance,
        "len": len,
        "list": list,
        "map": map,
        "max": max,
        "min": min,
        "oct": oct,
        "ord": ord,
        "pow": pow,
        "range": range,
        "reversed": reversed,
        "round": round,
        "set": set,
        "sorted": sorted,
        "str": str,
        "sum": sum,
        "tuple": tuple,
        "zip": zip,
    },
    "math": math,
    "datetime": datetime,
    "json": json,
    "statistics": statistics,
    "re": re,
}

def run_python_calc(code_or_expression: str) -> str:
    """
    Safely evaluate a mathematical calculation, formula, unit conversion, or Python snippet.
    Available modules: math, datetime, statistics, json, re.
    
    Args:
        code_or_expression: A Python mathematical expression (e.g. 'math.sqrt(144) * 2') or snippet.
    """
    code = code_or_expression.strip()
    if not code:
        return "Error: Empty expression provided."

    # Disallow dangerous patterns
    forbidden = ["import ", "exec", "eval", "__", "open", "os.", "sys.", "subprocess", "socket"]
    for pattern in forbidden:
        if pattern in code:
            return f"Security Restriction: '{pattern}' is not permitted in the calculation sandbox."

    try:
        # First try as an expression
        result = eval(code, SAFE_GLOBALS, {})
        return f"Calculation Result:\n{result}"
    except SyntaxError:
        # If it's a multi-line snippet, execute it with a local scope and look for result
        local_vars = {}
        try:
            exec(code, SAFE_GLOBALS, local_vars)
            if "result" in local_vars:
                return f"Calculation Result:\n{local_vars['result']}"
            elif local_vars:
                return f"Execution Variables:\n{json.dumps(str(local_vars), indent=2)}"
            else:
                return "Execution completed successfully (no return value)."
        except Exception as e:
            return f"Calculation execution error: {str(e)}"
    except Exception as e:
        return f"Calculation error: {str(e)}"
