import re

def remove_comments(text):
    """Удаляет многострочные комментарии из текста"""
    pattern = r'<#.*?#>'
    return re.sub(pattern, '', text, flags=re.DOTALL)