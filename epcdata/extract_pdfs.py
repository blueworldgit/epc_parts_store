#!/usr/bin/env python3
"""
PDF Text Extractor
Extracts text from PDF files in the media folder and creates Django template pages
"""

import os
import sys
import fitz  # PyMuPDF
import html
from pathlib import Path

def extract_pdf_text(pdf_path):
    """Extract text from a PDF file using PyMuPDF"""
    try:
        doc = fitz.open(pdf_path)
        text = ""
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            page_text = page.get_text()
            text += page_text + "\n\n"
        
        doc.close()
        
        # Clean up the text formatting
        text = clean_pdf_text(text)
        return text.strip()
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
        return None

def clean_pdf_text(text):
    """Aggressively clean up PDF text formatting issues"""
    import re
    
    # First, handle the most common spacing issues
    # Remove single character + space patterns that form words
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Skip empty lines
        if not line.strip():
            cleaned_lines.append('')
            continue
            
        # Handle severely spaced text
        # Look for pattern: single char + space + single char
        words = line.split()
        cleaned_words = []
        
        i = 0
        while i < len(words):
            word = words[i]
            
            # If word is single character, try to combine with following characters
            if len(word) == 1 and word.isalpha():
                combined_word = word
                j = i + 1
                
                # Combine consecutive single characters
                while j < len(words) and len(words[j]) == 1 and words[j].isalpha():
                    combined_word += words[j]
                    j += 1
                
                # If we combined multiple characters, use the combined word
                if j > i + 1:
                    cleaned_words.append(combined_word)
                    i = j
                else:
                    cleaned_words.append(word)
                    i += 1
            else:
                cleaned_words.append(word)
                i += 1
        
        cleaned_line = ' '.join(cleaned_words)
        
        # Additional cleaning for common patterns
        cleaned_line = re.sub(r'\b([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\b', r'\1\2\3\4\5\6\7\8\9\10\11\12\13\14\15', cleaned_line)
        cleaned_line = re.sub(r'\b([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\b', r'\1\2\3\4\5\6\7\8\9\10\11\12\13\14', cleaned_line)
        cleaned_line = re.sub(r'\b([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\b', r'\1\2\3\4\5\6\7\8\9\10\11\12\13', cleaned_line)
        cleaned_line = re.sub(r'\b([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\b', r'\1\2\3\4\5\6\7\8\9\10\11\12', cleaned_line)
        cleaned_line = re.sub(r'\b([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\b', r'\1\2\3\4\5\6\7\8\9\10\11', cleaned_line)
        cleaned_line = re.sub(r'\b([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\b', r'\1\2\3\4\5\6\7\8\9\10', cleaned_line)
        cleaned_line = re.sub(r'\b([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\b', r'\1\2\3\4\5\6\7\8\9', cleaned_line)
        cleaned_line = re.sub(r'\b([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\b', r'\1\2\3\4\5\6\7\8', cleaned_line)
        cleaned_line = re.sub(r'\b([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\b', r'\1\2\3\4\5\6\7', cleaned_line)
        cleaned_line = re.sub(r'\b([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\b', r'\1\2\3\4\5\6', cleaned_line)
        cleaned_line = re.sub(r'\b([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\b', r'\1\2\3\4\5', cleaned_line)
        cleaned_line = re.sub(r'\b([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\b', r'\1\2\3\4', cleaned_line)
        cleaned_line = re.sub(r'\b([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])\b', r'\1\2\3', cleaned_line)
        cleaned_line = re.sub(r'\b([A-Za-z])\s+([A-Za-z])\b', r'\1\2', cleaned_line)
        
        cleaned_lines.append(cleaned_line)
    
    text = '\n'.join(cleaned_lines)
    
    # Clean up multiple spaces and normalize whitespace
    text = re.sub(r' +', ' ', text)  # Multiple spaces to single space
    text = re.sub(r'\n\s+', '\n', text)  # Remove spaces at start of lines
    text = re.sub(r'\n{3,}', '\n\n', text)  # Multiple newlines to double newline
    
    return text

def create_django_template(title, content, filename):
    """Create a Django template for the content"""
    
    # Clean up the title for URL and template
    clean_title = title.replace('.pdf', '').replace('.docx', '').replace(' - ', ' ').strip()
    
    # Escape HTML content
    escaped_content = html.escape(content)
    
    # Create template content
    template_content = """{% extends 'oscar/storefront_base.html' %}
{% load static %}
{% load i18n %}

{% block title %}
    """ + clean_title + """ - {{ settings.OSCAR_SHOP_NAME }}
{% endblock %}

{% block page_title %}
    """ + clean_title + """
{% endblock %}

{% block breadcrumb_items %}
    <li><a href="{% url 'catalogue:index' %}">{% trans "Home" %}</a></li>
    <li class="active">""" + clean_title + """</li>
{% endblock %}

{% block content %}
<div class="container-fluid">
    <div class="row">
        <div class="col-lg-12">
            <div class="legal-content-wrapper">
                <div class="legal-header mb-4">
                    <h1 class="page-title">""" + clean_title + """</h1>
                    <p class="text-muted">Last updated: {% now "F d, Y" %}</p>
                </div>
                
                <div class="legal-content">
                    <div class="content-text">
                        <div class="legal-text">""" + escaped_content + """</div>
                    </div>
                </div>
                
                <div class="legal-footer mt-5">
                    <div class="alert alert-info">
                        <i class="fa fa-info-circle"></i>
                        If you have any questions about this document, please <a href="mailto:info@vanpartsdirect.com">contact us</a>.
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_css %}
<style>
.legal-content-wrapper {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
}

.legal-header {
    text-align: center;
    border-bottom: 2px solid #eee;
    padding-bottom: 20px;
}

.page-title {
    color: #333;
    font-size: 2.5rem;
    font-weight: 600;
    margin-bottom: 10px;
}

.legal-content {
    background: #fff;
    padding: 30px;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    margin: 20px 0;
}

.legal-text {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    font-size: 15px;
    line-height: 1.8;
    color: #444;
    white-space: pre-line;
    word-wrap: break-word;
    background: transparent;
    margin: 0;
    padding: 0;
    text-align: justify;
}

.legal-text h1, .legal-text h2, .legal-text h3 {
    color: #333;
    margin-top: 25px;
    margin-bottom: 15px;
    font-weight: 600;
}

.legal-text h1 {
    font-size: 1.8rem;
    border-bottom: 2px solid #eee;
    padding-bottom: 10px;
}

.legal-text h2 {
    font-size: 1.4rem;
}

.legal-text h3 {
    font-size: 1.2rem;
}

.legal-footer {
    text-align: center;
}

@media (max-width: 768px) {
    .legal-content-wrapper {
        padding: 10px;
    }
    
    .page-title {
        font-size: 2rem;
    }
    
    .legal-content {
        padding: 20px;
    }
    
    .legal-text {
        font-size: 13px;
    }
}
</style>
{% endblock %}"""

    return template_content

def main():
    # Define the media directory
    media_dir = Path("c:/pythonstuff/vansdirect/epc_parts_store/epcdata/media")
    templates_dir = Path("c:/pythonstuff/vansdirect/epc_parts_store/epcdata/templates/oscar/pages")
    
    # Create templates directory if it doesn't exist
    templates_dir.mkdir(parents=True, exist_ok=True)
    
    # PDF files to process
    pdf_files = [
        "7. GDPR Data Protection Policy (GB).docx.pdf",
        "privacy policy September 25.docx.pdf", 
        "Van Parts Direct - Terms and Conditions.pdf"
    ]
    
    pages_created = []
    
    for pdf_file in pdf_files:
        pdf_path = media_dir / pdf_file
        
        if pdf_path.exists():
            print(f"Processing: {pdf_file}")
            
            # Extract text
            text_content = extract_pdf_text(pdf_path)
            
            if text_content:
                # Determine template filename based on content
                if "GDPR" in pdf_file or "Data Protection" in pdf_file:
                    template_name = "data-protection-policy.html"
                    page_title = "GDPR Data Protection Policy"
                elif "privacy policy" in pdf_file.lower():
                    template_name = "privacy-policy.html"
                    page_title = "Privacy Policy"
                elif "Terms and Conditions" in pdf_file:
                    template_name = "terms-and-conditions.html"
                    page_title = "Terms and Conditions"
                else:
                    # Fallback
                    safe_name = pdf_file.replace('.pdf', '').replace('.docx', '').replace(' ', '-').lower()
                    template_name = f"{safe_name}.html"
                    page_title = pdf_file.replace('.pdf', '').replace('.docx', '')
                
                # Create Django template
                template_content = create_django_template(page_title, text_content, template_name)
                
                # Write template file
                template_path = templates_dir / template_name
                with open(template_path, 'w', encoding='utf-8') as f:
                    f.write(template_content)
                
                pages_created.append({
                    'file': template_name,
                    'title': page_title,
                    'path': str(template_path)
                })
                
                print(f"Created template: {template_path}")
            else:
                print(f"Failed to extract text from: {pdf_file}")
        else:
            print(f"PDF file not found: {pdf_path}")
    
    # Print summary
    print(f"\n=== Summary ===")
    print(f"Created {len(pages_created)} pages:")
    for page in pages_created:
        print(f"- {page['title']}: {page['file']}")
    
    return pages_created

if __name__ == "__main__":
    main()
