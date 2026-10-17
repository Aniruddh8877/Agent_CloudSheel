from app.tools.web_search import web_search
from app.tools.web_reader import fetch_webpage
from app.tools.notes import (
    create_or_update_note,
    read_note,
    list_notes,
    search_notes,
    delete_note,
)
from app.tools.calculator import run_python_calc
from app.tools.datetime_tool import get_current_datetime

ALL_TOOL_FUNCTIONS = [
    web_search,
    fetch_webpage,
    create_or_update_note,
    read_note,
    list_notes,
    search_notes,
    delete_note,
    run_python_calc,
    get_current_datetime,
]

TOOL_REGISTRY = {fn.__name__: fn for fn in ALL_TOOL_FUNCTIONS}

TOOLS_METADATA = [
    {
        "name": "web_search",
        "icon": "globe",
        "display_name": "Web Search",
        "description": "Live DuckDuckGo search for news, real-time facts, and documentation.",
    },
    {
        "name": "fetch_webpage",
        "icon": "file-text",
        "display_name": "Webpage Reader",
        "description": "Extracts and reads full text and article content from any URL.",
    },
    {
        "name": "notes_manager",
        "icon": "book-open",
        "display_name": "Notes & Workspace",
        "description": "Create, recall, search, and delete Markdown notes in your workspace.",
    },
    {
        "name": "run_python_calc",
        "icon": "cpu",
        "display_name": "Python Sandbox & Calc",
        "description": "Math, statistical computations, and data transformations in Python.",
    },
    {
        "name": "get_current_datetime",
        "icon": "clock",
        "display_name": "DateTime & Timezone",
        "description": "Accurate current local date, time, and weekday information.",
    },
]
