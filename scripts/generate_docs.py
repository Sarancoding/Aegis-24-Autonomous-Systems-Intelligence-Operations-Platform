#!/usr/bin/env python3
"""
Generate PDF documentation from Markdown files for Aegis-24 Platform.
Uses weasyprint to convert MD -> HTML -> PDF.
"""

import os
import markdown
from weasyprint import HTML, CSS
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
DOCS_DIR = ROOT_DIR / "docs"
ARTIFACTS_DIR = ROOT_DIR / "artifacts"
OUTPUT_DIR = ROOT_DIR

# CSS styling for professional PDF output
PDF_CSS = CSS(string="""
    @page {
        size: A4;
        margin: 2cm;
        @bottom-right {
            content: counter(page);
        }
    }
    body {
        font-family: 'Segoe UI', Arial, sans-serif;
        line-height: 1.6;
        color: #333;
    }
    h1 {
        color: #2563eb;
        border-bottom: 2px solid #2563eb;
        padding-bottom: 0.5em;
        page-break-after: avoid;
    }
    h2 {
        color: #1e40af;
        border-bottom: 1px solid #e5e7eb;
        padding-bottom: 0.3em;
        page-break-after: avoid;
    }
    h3 {
        color: #1e3a8a;
        page-break-after: avoid;
    }
    code {
        background-color: #f3f4f6;
        padding: 0.2em 0.4em;
        border-radius: 3px;
        font-family: 'Courier New', monospace;
    }
    pre {
        background-color: #1f2937;
        color: #f9fafb;
        padding: 1em;
        border-radius: 6px;
        overflow-x: auto;
        page-break-inside: avoid;
    }
    blockquote {
        border-left: 4px solid #2563eb;
        margin-left: 0;
        padding-left: 1em;
        color: #4b5563;
    }
    table {
        border-collapse: collapse;
        width: 100%;
        margin: 1em 0;
    }
    th, td {
        border: 1px solid #d1d5db;
        padding: 0.5em 1em;
        text-align: left;
    }
    th {
        background-color: #f3f4f6;
        font-weight: bold;
    }
    ul, ol {
        padding-left: 1.5em;
    }
    a {
        color: #2563eb;
        text-decoration: none;
    }
    .warning {
        background-color: #fef3c7;
        border-left: 4px solid #f59e0b;
        padding: 1em;
        margin: 1em 0;
    }
    .note {
        background-color: #dbeafe;
        border-left: 4px solid #2563eb;
        padding: 1em;
        margin: 1em 0;
    }
""")


def md_to_pdf(md_path: Path, pdf_path: Path) -> bool:
    """Convert a Markdown file to PDF."""
    try:
        if not md_path.exists():
            print(f"⚠️  Warning: {md_path} not found, skipping...")
            return False
        
        # Read markdown content
        md_content = md_path.read_text(encoding='utf-8')
        
        # Convert to HTML
        html_content = markdown.markdown(
            md_content,
            extensions=['tables', 'fenced_code', 'toc', 'nl2br']
        )
        
        # Wrap in proper HTML document
        full_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>{md_path.stem.replace('_', ' ').title()}</title>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        # Generate PDF
        HTML(string=full_html).write_pdf(
            str(pdf_path),
            stylesheets=[PDF_CSS]
        )
        
        print(f"✅ Generated: {pdf_path.name}")
        return True
        
    except Exception as e:
        print(f"❌ Error generating {pdf_path.name}: {e}")
        return False


def generate_all_pdfs():
    """Generate all required PDFs for the landing page."""
    print("🚀 Generating PDF documentation for Aegis-24 Platform...\n")
    
    pdf_mappings = [
        # (source_md, output_pdf)
        (ROOT_DIR / "README.md", OUTPUT_DIR / "Aegis24_Readme.pdf"),
        (DOCS_DIR / "INSTALLATION.md", OUTPUT_DIR / "Aegis24_Installation_Guide.pdf"),
        (DOCS_DIR / "SETUP.md", OUTPUT_DIR / "Aegis24_Setup_Guide.pdf"),
        (DOCS_DIR / "SYSTEM_REQUIREMENTS.md", OUTPUT_DIR / "Aegis24_System_Requirements.pdf"),
        (DOCS_DIR / "WORKFLOW.md", OUTPUT_DIR / "Aegis24_Workflow.pdf"),
        (ARTIFACTS_DIR / "compliance_audit_report.md", OUTPUT_DIR / "Aegis24_Testing_Report.pdf"),
    ]
    
    success_count = 0
    total_count = len(pdf_mappings)
    
    for md_path, pdf_path in pdf_mappings:
        if md_to_pdf(md_path, pdf_path):
            success_count += 1
    
    print(f"\n📊 Summary: {success_count}/{total_count} PDFs generated successfully")
    
    if success_count == total_count:
        print("✅ All PDFs ready for GitHub landing page!")
        return True
    else:
        print("⚠️  Some PDFs failed to generate. Check errors above.")
        return False


if __name__ == "__main__":
    generate_all_pdfs()
