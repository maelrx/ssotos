"""Templates REST API — per D-48 (internal modules)."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any

router = APIRouter(prefix="/templates", tags=["templates"])

# Built-in templates per Phase 1
TEMPLATES = {
    "daily": {
        "name": "Daily Note",
        "description": "Template for daily notes with date, tasks, and reflections",
        "fields": ["date", "tasks", "reflections", "highlights"],
        "content": """# {{date}}

## Tasks
- [ ]

## Reflections
-

## Highlights
-
""",
    },
    "project": {
        "name": "Project Note",
        "description": "Template for project documentation",
        "fields": ["project_name", "status", "objectives", "tasks", "links"],
        "content": """# {{project_name}}

**Status:** {{status}}

## Objectives
-

## Tasks
- [ ]

## Notes
-

## Links
- [[]]
""",
    },
    "area": {
        "name": "Area of Focus",
        "description": "Template for long-term areas and responsibilities",
        "fields": ["area_name", "vision", "metrics", "projects"],
        "content": """# {{area_name}}

## Vision
{{vision}}

## Success Metrics
-

## Active Projects
- [[]]

## Notes
-
""",
    },
    "resource": {
        "name": "Resource Note",
        "description": "Template for reference materials and resources",
        "fields": ["resource_name", "type", "source", "summary", "tags"],
        "content": """# {{resource_name}}

**Type:** {{type}}
**Source:** {{source}}

## Summary
{{summary}}

## Key Points
-

## Related
- [[]]

## Tags
#{{tags}}
""",
    },
    "fleeting": {
        "name": "Fleeting Note",
        "description": "Quick capture for transient thoughts",
        "fields": ["content"],
        "content": """# Fleeting — {{date}}

{{content}}
""",
    },
    "permanent": {
        "name": "Permanent Note",
        "description": "Refined, atomic knowledge note",
        "fields": ["title", "sources", "ideas", "links"],
        "content": """# {{title}}

**Sources:** {{sources}}

## Ideas
-

## References
- [[]]

## Links
- [[]]
""",
    },
    "source": {
        "name": "Source Note",
        "description": "Literature reference with bibliographic info",
        "fields": ["title", "author", "type", "url", "date_accessed"],
        "content": """# {{title}}

**Author:** {{author}}
**Type:** {{type}}
**URL:** {{url}}
**Accessed:** {{date_accessed}}

## Summary
-

## Key Quotations
> "

## Notes
-

## Related
- [[]]
""",
    },
    "synthesis": {
        "name": "Synthesis Note",
        "description": "Research synthesis combining multiple sources",
        "fields": ["topic", "sources", "findings", "questions"],
        "content": """# Synthesis: {{topic}}

**Sources:** {{sources}}

## Key Findings
-

## Questions Raised
-

## Implications
-

## Next Steps
- [ ]
""",
    },
}


class RenderTemplateRequest(BaseModel):
    """Request to render a template with variables."""
    template_name: str
    variables: dict[str, Any] = {}


@router.get("/")
async def list_templates():
    """List all available templates."""
    return {
        "templates": [
            {
                "name": name,
                "display_name": info["name"],
                "description": info["description"],
                "fields": info["fields"],
            }
            for name, info in TEMPLATES.items()
        ],
        "total": len(TEMPLATES),
    }


@router.get("/{template_name}")
async def get_template(template_name: str):
    """Get a template by name with its full content and metadata."""
    if template_name not in TEMPLATES:
        raise HTTPException(
            status_code=404,
            detail=f"Template '{template_name}' not found. "
                   f"Available: {list(TEMPLATES.keys())}"
        )

    info = TEMPLATES[template_name]
    return {
        "name": template_name,
        "display_name": info["name"],
        "description": info["description"],
        "fields": info["fields"],
        "content": info["content"],
    }


@router.post("/render")
async def render_template(request: RenderTemplateRequest):
    """Render a template with the provided variables.

    Variables are substituted using {{variable_name}} syntax.
    """
    if request.template_name not in TEMPLATES:
        raise HTTPException(
            status_code=404,
            detail=f"Template '{request.template_name}' not found"
        )

    content = TEMPLATES[request.template_name]["content"]

    # Simple variable substitution
    for key, value in request.variables.items():
        placeholder = f"{{{{{key}}}}}"
        content = content.replace(placeholder, str(value))

    return {
        "template": request.template_name,
        "rendered": content,
        "variables_used": list(request.variables.keys()),
    }
