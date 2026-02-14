import pdfplumber
import re

pdf_path = "uploads/LAB MANUAL PDF FOR TESTING.pdf"
with pdfplumber.open(pdf_path) as pdf:
    full_text = ""
    for page in pdf.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"
    
    print("Searching for experiment patterns...\n")
    
    # Try different patterns
    patterns = [
        (r'experiment[s]?\s*(\d+)', 'experiment N'),
        (r'exp[.\s]+(\d+)', 'exp.N'),
        (r'^(\d+)\s*[.)\-]\s*([A-Za-z].*?)$', 'numbered list'),
        (r'aim[:|]?\s*([^\n]+)', 'aim:'),
        (r'procedure[:|]?\s*([^\n]+)', 'procedure:'),
    ]
    
    for pattern, label in patterns:
        matches = re.finditer(pattern, full_text, re.IGNORECASE | re.MULTILINE)
        matches_list = list(matches)
        if matches_list:
            print(f"Found {len(matches_list)} matches for '{label}':")
            for i, m in enumerate(matches_list[:5]):
                print(f"  {i+1}. {m.group(0)[:100]}")
            print()
    
    # Also show a middle section
    mid = len(full_text) // 4
    print("Sample from PDF (1/4 mark):")
    print(full_text[mid:mid+1500])
