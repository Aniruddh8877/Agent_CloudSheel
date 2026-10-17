#!/usr/bin/env python3
import sys
import uvicorn
from app.config import settings

def main():
    print("=" * 60)
    print(" 🚀  Aniruddh PYTHON WEB AGENT")
    print(" 🌐  Live Web Search | 📄 Page Reader | 📝 Notes | 🧮 Sandbox")
    print("=" * 60)
    print(f" • Host: http://{settings.host}:{settings.port}")
    print(f" • Default Model: {settings.model}")
    print(f" • Notes Directory: {settings.notes_dir}")
    print(f" • API Key Status: {'Configured ✅' if settings.get_api_key() else 'Not Set (Set in UI Settings or .env) ⚠️'}")
    print("=" * 60)
    print(f"\n👉 Open in your browser: http://{settings.host}:{settings.port}\n")

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        log_level="info",
    )

if __name__ == "__main__":
    main()
