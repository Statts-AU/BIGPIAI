# cv_processor/config/settings.py
"""
Configuration settings for the CV processing system.
"""
import os
from pathlib import Path

# AI Configuration
AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini")
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-1.5-flash")

# File Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
CONTENT_DIR = PROJECT_ROOT / "content"
TEMPLATES_DIR = PROJECT_ROOT / "templates"
OUTPUT_DIR = PROJECT_ROOT / "output"

TEMPLATE_PATH = TEMPLATES_DIR / "Template.docx"
ANALYSIS_JSON_PATH = OUTPUT_DIR / "analysis.json"
SOURCE_PROFILE_JSON_PATH = OUTPUT_DIR / "source_profile.json"
TEMPLATE_SCHEMA_JSON_PATH = OUTPUT_DIR / "template_schema.json"
POSITIONAL_EXECUTION_PLAN_PATH = OUTPUT_DIR / "positional_execution_plan.json"
POSITIONAL_PLACEHOLDERS_PATH = OUTPUT_DIR / "positional_placeholders.json"
POSITION_MAP_PATH = OUTPUT_DIR / "position_map.json"
REPLACEMENT_MAP_PATH = OUTPUT_DIR / "replacement_map.json"

# Processing Configuration
CONCURRENCY = int(os.getenv("CONCURRENCY", "3"))
