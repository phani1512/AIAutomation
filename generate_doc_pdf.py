"""
Simple PDF Generator using weasyprint or markdown-pdf
Converts SYSTEM_DOCUMENTATION.md to PDF
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip"""
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def generate_pdf_weasyprint():
    """Generate PDF using weasyprint"""
    try:
        import markdown
        from weasyprint import HTML, CSS
        from weasyprint.text.fonts import FontConfiguration
        
        # Read markdown file
        with open('SYSTEM_DOCUMENTATION.md', 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Convert markdown to HTML
        html_content = markdown.markdown(
            md_content,
            extensions=['fenced_code', 'tables', 'codehilite']
        )
        
        # Add CSS styling
        css_style = """
        <style>
            @page {
                size: A4;
                margin: 2cm;
            }
            body {
                font-family: Arial, sans-serif;
                font-size: 11pt;
                line-height: 1.6;
                color: #333;
            }
            h1 {
                color: #2563eb;
                font-size: 24pt;
                margin-top: 20pt;
                margin-bottom: 12pt;
                page-break-after: avoid;
            }
            h2 {
                color: #1e40af;
                font-size: 18pt;
                margin-top: 16pt;
                margin-bottom: 10pt;
                page-break-after: avoid;
            }
            h3 {
                color: #3b82f6;
                font-size: 14pt;
                margin-top: 12pt;
                margin-bottom: 8pt;
            }
            pre, code {
                background-color: #f3f4f6;
                padding: 10px;
                border-radius: 4px;
                font-family: 'Courier New', monospace;
                font-size: 9pt;
                overflow-x: auto;
            }
            table {
                border-collapse: collapse;
                width: 100%;
                margin: 12pt 0;
            }
            th {
                background-color: #3b82f6;
                color: white;
                padding: 8pt;
                text-align: left;
            }
            td {
                border: 1px solid #ddd;
                padding: 8pt;
            }
            tr:nth-child(even) {
                background-color: #f9fafb;
            }
            .title-page {
                text-align: center;
                margin-top: 30%;
            }
        </style>
        """
        
        # Create complete HTML
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>System Documentation</title>
            {css_style}
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        # Generate PDF
        from datetime import datetime
        filename = f"System_Documentation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        font_config = FontConfiguration()
        HTML(string=full_html).write_pdf(
            filename,
            font_config=font_config
        )
        
        print(f"✅ PDF generated successfully: {filename}")
        print(f"📁 Location: {os.path.abspath(filename)}")
        return True
        
    except Exception as e:
        print(f"❌ Error with weasyprint: {e}")
        return False

def generate_pdf_simple():
    """Simple method - just copy markdown and open in browser"""
    try:
        import markdown
        from datetime import datetime
        
        # Read markdown file
        with open('SYSTEM_DOCUMENTATION.md', 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Convert to HTML with styling
        html_content = markdown.markdown(
            md_content,
            extensions=['fenced_code', 'tables', 'codehilite', 'toc']
        )
        
        # Create styled HTML file
        html_output = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>System Documentation</title>
    <style>
        @media print {{
            @page {{
                size: A4;
                margin: 2cm;
            }}
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #333;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background: white;
        }}
        h1 {{
            color: #2563eb;
            font-size: 24pt;
            margin-top: 20pt;
            margin-bottom: 12pt;
            border-bottom: 2px solid #2563eb;
            padding-bottom: 8pt;
        }}
        h2 {{
            color: #1e40af;
            font-size: 18pt;
            margin-top: 16pt;
            margin-bottom: 10pt;
            border-bottom: 1px solid #e5e7eb;
            padding-bottom: 6pt;
        }}
        h3 {{
            color: #3b82f6;
            font-size: 14pt;
            margin-top: 12pt;
            margin-bottom: 8pt;
        }}
        pre {{
            background-color: #f3f4f6;
            padding: 12px;
            border-radius: 6px;
            border-left: 4px solid #3b82f6;
            overflow-x: auto;
            font-size: 9pt;
        }}
        code {{
            background-color: #f3f4f6;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', Consolas, monospace;
            font-size: 9pt;
        }}
        pre code {{
            background: none;
            padding: 0;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 12pt 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        th {{
            background-color: #3b82f6;
            color: white;
            padding: 10pt;
            text-align: left;
            font-weight: 600;
        }}
        td {{
            border: 1px solid #e5e7eb;
            padding: 8pt;
        }}
        tr:nth-child(even) {{
            background-color: #f9fafb;
        }}
        tr:hover {{
            background-color: #f3f4f6;
        }}
        .print-button {{
            position: fixed;
            top: 20px;
            right: 20px;
            background: #2563eb;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14pt;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            z-index: 1000;
        }}
        .print-button:hover {{
            background: #1e40af;
        }}
        @media print {{
            .print-button {{
                display: none;
            }}
        }}
        blockquote {{
            border-left: 4px solid #60a5fa;
            padding-left: 16px;
            margin-left: 0;
            color: #6b7280;
        }}
        ul, ol {{
            margin: 8pt 0;
            padding-left: 24pt;
        }}
        li {{
            margin: 4pt 0;
        }}
        hr {{
            border: none;
            border-top: 1px solid #e5e7eb;
            margin: 20pt 0;
        }}
    </style>
    <script>
        function printToPDF() {{
            window.print();
        }}
    </script>
</head>
<body>
    <button class="print-button" onclick="printToPDF()">📄 Save as PDF (Ctrl+P)</button>
    {html_content}
</body>
</html>
"""
        
        # Save HTML file
        html_filename = f"System_Documentation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(html_filename, 'w', encoding='utf-8') as f:
            f.write(html_output)
        
        print(f"✅ HTML file generated: {html_filename}")
        print(f"📁 Location: {os.path.abspath(html_filename)}")
        print(f"\n📌 Instructions to save as PDF:")
        print(f"   1. Open the HTML file in your browser")
        print(f"   2. Click the 'Save as PDF' button or press Ctrl+P")
        print(f"   3. Select 'Save as PDF' or 'Microsoft Print to PDF'")
        print(f"   4. Click Save")
        
        # Try to open in browser
        import webbrowser
        webbrowser.open(f"file:///{os.path.abspath(html_filename)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("📄 System Documentation PDF Generator")
    print("=" * 60)
    
    # Try weasyprint first
    print("\n🔄 Checking for required packages...")
    
    try:
        import markdown
        print("✅ markdown installed")
    except ImportError:
        print("📦 Installing markdown...")
        install_package("markdown")
    
    # Use simple HTML method (most reliable)
    print("\n🔄 Generating HTML version for PDF conversion...")
    success = generate_pdf_simple()
    
    if not success:
        print("\n❌ Failed to generate documentation")
        print("💡 Try installing weasyprint manually: pip install weasyprint")
