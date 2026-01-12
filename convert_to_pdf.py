"""
Convert AI_PROMPTS_GUIDE.md to PDF using markdown and reportlab
"""

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Preformatted
    from reportlab.lib.enums import TA_LEFT, TA_CENTER
    from reportlab.lib.colors import HexColor
    import markdown
    import re
    
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False
    print("Installing required libraries...")
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab", "markdown"])
    print("Libraries installed. Please run this script again.")
    sys.exit(0)

def convert_md_to_pdf(md_file, pdf_file):
    """Convert markdown to PDF with proper formatting."""
    
    # Read markdown file
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Create PDF
    doc = SimpleDocTemplate(
        pdf_file,
        pagesize=letter,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch,
        leftMargin=0.75*inch,
        rightMargin=0.75*inch
    )
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=HexColor('#1e3a8a'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    h1_style = ParagraphStyle(
        'CustomH1',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=HexColor('#1e40af'),
        spaceAfter=12,
        spaceBefore=16,
        fontName='Helvetica-Bold'
    )
    
    h2_style = ParagraphStyle(
        'CustomH2',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=HexColor('#2563eb'),
        spaceAfter=10,
        spaceBefore=14,
        fontName='Helvetica-Bold'
    )
    
    h3_style = ParagraphStyle(
        'CustomH3',
        parent=styles['Heading3'],
        fontSize=14,
        textColor=HexColor('#3b82f6'),
        spaceAfter=8,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    h4_style = ParagraphStyle(
        'CustomH4',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=HexColor('#60a5fa'),
        spaceAfter=6,
        spaceBefore=10,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=10,
        spaceAfter=8,
        fontName='Helvetica'
    )
    
    code_style = ParagraphStyle(
        'CodeBlock',
        parent=styles['Code'],
        fontSize=8,
        fontName='Courier',
        leftIndent=20,
        rightIndent=20,
        spaceAfter=10,
        spaceBefore=10,
        backColor=HexColor('#f3f4f6')
    )
    
    # Story (content container)
    story = []
    
    # Split content by lines
    lines = md_content.split('\n')
    
    in_code_block = False
    code_lines = []
    in_table = False
    
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        
        # Code blocks
        if line.startswith('```'):
            if in_code_block:
                # End code block
                if code_lines:
                    code_text = '\n'.join(code_lines)
                    # Escape special characters for reportlab
                    code_text = code_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    pre = Preformatted(code_text, code_style)
                    story.append(pre)
                    story.append(Spacer(1, 0.1*inch))
                code_lines = []
                in_code_block = False
            else:
                in_code_block = True
            i += 1
            continue
        
        if in_code_block:
            code_lines.append(line)
            i += 1
            continue
        
        # Headers
        if line.startswith('# '):
            text = line[2:].replace('📋', '').replace('🎯', '').replace('📝', '').replace('🎨', '').strip()
            if i == 0:  # Title
                story.append(Paragraph(text, title_style))
            else:
                story.append(Paragraph(text, h1_style))
            story.append(Spacer(1, 0.15*inch))
        
        elif line.startswith('## '):
            text = line[3:].replace('📋', '').replace('🎯', '').replace('📝', '').replace('🔧', '').replace('📊', '').replace('🚀', '').replace('💾', '').replace('🎯', '').replace('🔍', '').replace('📚', '').strip()
            story.append(Paragraph(text, h1_style))
            story.append(Spacer(1, 0.12*inch))
        
        elif line.startswith('### '):
            text = line[4:].replace('✅', '').replace('❌', '').replace('💡', '').replace('1️⃣', '').replace('2️⃣', '').replace('3️⃣', '').replace('4️⃣', '').replace('5️⃣', '').replace('6️⃣', '').replace('7️⃣', '').replace('8️⃣', '').replace('9️⃣', '').replace('🔟', '').replace('1️⃣1️⃣', '').replace('1️⃣2️⃣', '').replace('1️⃣3️⃣', '').replace('1️⃣4️⃣', '').strip()
            story.append(Paragraph(text, h2_style))
            story.append(Spacer(1, 0.1*inch))
        
        elif line.startswith('#### '):
            text = line[5:].strip()
            story.append(Paragraph(text, h3_style))
            story.append(Spacer(1, 0.08*inch))
        
        # Horizontal rule
        elif line.startswith('---'):
            story.append(Spacer(1, 0.2*inch))
            story.append(PageBreak())
        
        # Bold text
        elif line.startswith('**') and line.endswith('**'):
            text = line[2:-2]
            story.append(Paragraph(f'<b>{text}</b>', body_style))
        
        # Lists
        elif line.startswith('- ') or line.startswith('* '):
            text = line[2:].replace('✅', '✓').replace('❌', '✗').replace('✓', '• ').replace('✗', '• ')
            story.append(Paragraph(f'&nbsp;&nbsp;&nbsp;• {text}', body_style))
        
        elif re.match(r'^\d+\.', line):
            text = re.sub(r'^\d+\.\s*', '', line)
            story.append(Paragraph(f'&nbsp;&nbsp;&nbsp;{text}', body_style))
        
        # Table detection (simple)
        elif '|' in line and not in_table:
            in_table = True
            i += 1
            continue
        
        elif in_table and line.strip() == '':
            in_table = False
            story.append(Spacer(1, 0.1*inch))
        
        elif in_table:
            # Skip table formatting lines
            if line.strip().startswith('|--'):
                i += 1
                continue
            # Convert table rows to simple text
            cells = [cell.strip() for cell in line.split('|') if cell.strip()]
            if cells:
                row_text = ' | '.join(cells)
                story.append(Paragraph(row_text, body_style))
        
        # Regular paragraphs
        elif line.strip() and not line.startswith('>'):
            # Remove emojis for PDF
            text = re.sub(r'[^\x00-\x7F]+', '', line)
            if text.strip():
                story.append(Paragraph(text, body_style))
        
        # Empty line
        elif line.strip() == '':
            story.append(Spacer(1, 0.08*inch))
        
        i += 1
    
    # Build PDF
    print(f"Generating PDF: {pdf_file}")
    doc.build(story)
    print(f"✓ PDF created successfully: {pdf_file}")

if __name__ == '__main__':
    md_file = 'AI_PROMPTS_GUIDE.md'
    pdf_file = 'AI_PROMPTS_GUIDE.pdf'
    
    try:
        convert_md_to_pdf(md_file, pdf_file)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
