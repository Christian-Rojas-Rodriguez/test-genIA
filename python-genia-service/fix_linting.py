#!/usr/bin/env python3
import re
import glob

def fix_blank_lines(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Fix E302: expected 2 blank lines, found 1
    # Before function/class definitions
    content = re.sub(r'\n(\s*(?:@\w+(?:\([^)]*\))?\s*\n)*\s*(?:def|class|async def)\s+\w+)', r'\n\n\1', content)
    
    # Fix E305: expected 2 blank lines after class or function definition, found 1  
    # After class/function definitions before other top-level code
    content = re.sub(r'(\n\s*(?:def|class|async def)\s+[^\n]+(?:\n(?:\s+[^\n]*|\s*))*\n)(\n*)([^\s\n])', r'\1\n\n\3', content)
    
    # Remove f-string without placeholders
    content = content.replace('f"⚠️  Detailed health check degraded - Gemini API unhealthy"', '"⚠️  Detailed health check degraded - Gemini API unhealthy"')
    
    with open(filepath, 'w') as f:
        f.write(content)

# Fix all Python files
for file in glob.glob('src/*.py'):
    fix_blank_lines(file)
    print(f"Fixed: {file}") 