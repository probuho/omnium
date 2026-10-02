with open('downloader_tui.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the ASCII_LOGO section
import re
pattern = r'ASCII_LOGO = r"""[\s\S]*?"""'
replacement = '''ASCII_LOGO = r"""
  ██████╗ ██████╗ ███╗   ███╗██████╗ ██╗     ██████╗  ██████╗ ████████╗███████╗
 ██════╝██═══██╗████╗ ████║██═══██╗██║     ██═══██╗██═══██╗╚══██══╝██════╝
 ██║     ██║   ██║██╔████╔██║██████═╝ ██║     ██║  ██║██═══██║   ██══╝  ╚════██║
 ██║     ██═══██══╝██══════╝╚══════╝╚══════╝╚══════╝╚══════╝    ╚══════╝╚══════╝
"""'''
new_content = re.sub(pattern, replacement, content)
with open('downloader_tui.py', 'w', encoding='utf-8') as f:
    f.write(new_content)
print('Done')