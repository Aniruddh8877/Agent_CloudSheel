import os
import re
from datetime import datetime
from pathlib import Path
from app.config import settings

def _sanitize_filename(title: str) -> str:
    cleaned = re.sub(r'[\\/*?:"<>|]', "", title).strip()
    cleaned = cleaned.replace(" ", "_")
    return cleaned or "untitled"

def _get_note_path(title: str) -> Path:
    filename = _sanitize_filename(title)
    if not filename.endswith(".md"):
        filename += ".md"
    return settings.notes_dir / filename

def create_or_update_note(title: str, content: str) -> str:
    """
    Create a new note or update an existing note in the user's workspace notes repository.
    Use this to save research findings, summaries, to-do lists, task plans, or references.

    Args:
        title: The title or topic of the note (e.g. 'Quantum_Computing_Overview').
        content: The markdown content to write in the note.
    """
    try:
        path = _get_note_path(title)
        existed = path.exists()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Add metadata frontmatter if not present
        full_content = f"# {title}\n*Last modified: {timestamp}*\n\n{content.strip()}\n"

        path.write_text(full_content, encoding="utf-8")
        action = "Updated" if existed else "Created"
        return f"Successfully {action.lower()} note '{title}' at {path.name}."
    except Exception as e:
        return f"Error saving note: {str(e)}"

def read_note(title: str) -> str:
    """
    Read the contents of an existing note by its title.

    Args:
        title: The title or filename of the note to read.
    """
    try:
        path = _get_note_path(title)
        if not path.exists():
            # Check case-insensitive match
            matches = [p for p in settings.notes_dir.glob("*.md") if p.stem.lower() == _sanitize_filename(title).lower()]
            if matches:
                path = matches[0]
            else:
                return f"Note '{title}' not found. Use list_notes to see existing notes."

        return path.read_text(encoding="utf-8")
    except Exception as e:
        return f"Error reading note: {str(e)}"

def list_notes() -> str:
    """
    List all saved notes in the workspace with their title, file size, and modification date.
    """
    try:
        notes = list(settings.notes_dir.glob("*.md"))
        if not notes:
            return "No notes found in workspace. You can create one using create_or_update_note."

        output = [f"Found {len(notes)} note(s):"]
        for p in sorted(notes, key=lambda x: x.stat().st_mtime, reverse=True):
            mtime = datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            size_kb = max(1, p.stat().st_size // 1024)
            output.append(f"- **{p.stem}** ({size_kb} KB, updated {mtime})")

        return "\n".join(output)
    except Exception as e:
        return f"Error listing notes: {str(e)}"

def search_notes(query: str) -> str:
    """
    Search within all saved notes for a specific word, phrase, or topic.

    Args:
        query: The search term or keyword to find.
    """
    try:
        notes = list(settings.notes_dir.glob("*.md"))
        if not notes:
            return "No notes exist to search."

        query_lower = query.lower()
        matches = []
        for p in notes:
            content = p.read_text(encoding="utf-8", errors="ignore")
            if query_lower in p.stem.lower() or query_lower in content.lower():
                # Extract small snippet
                lines = [line.strip() for line in content.splitlines() if query_lower in line.lower()]
                snippet = lines[0][:150] if lines else "Matched in note title."
                matches.append(f"- **{p.stem}**: \"{snippet}\"")

        if not matches:
            return f"No notes matched the query: '{query}'."

        return f"Found {len(matches)} note(s) matching '{query}':\n" + "\n".join(matches)
    except Exception as e:
        return f"Error searching notes: {str(e)}"

def delete_note(title: str) -> str:
    """
    Delete a saved note from the workspace.

    Args:
        title: The title of the note to delete.
    """
    try:
        path = _get_note_path(title)
        if not path.exists():
            return f"Note '{title}' does not exist."
        path.unlink()
        return f"Successfully deleted note '{title}'."
    except Exception as e:
        return f"Error deleting note: {str(e)}"
