with open('downloader_tui.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find ASCII_LOGO line
for i, line in enumerate(lines):
    if 'ASCII_LOGO = r"""' in line:
        start = i
        break

# Find closing """
for i in range(start + 1, len(lines)):
    if '"""' in lines[i] and i > start:
        end = i
        break

# Replace lines[start:end+1]
new_ascii = '''ASCII_LOGO = r"""
  ██████╗ ██████╗ ███╗   ███╗██████╗ ██╗     ██████╗  ██████╗ ████████╗███████╗
 ██╔════╝██═══██╗████╗ ████║██╔══██╗██║     ██═══██╗██═══██╗╚══██══╝██════╝
 ██║     ██║   ██║██╔████╔██║██████═╝ ██║     ██║  ██║██═══██║   ██══╝  ╚════██║
 ██║     ██═══██══╝██══════╝╚══════╝╚══════╝╚══════╝╚══════╝    ╚══════╝╚══════╝
"""
'''

lines[start:end+1] = [new_ascii]

with open('downloader_tui.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')