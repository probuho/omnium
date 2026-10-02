with open('downloader_tui.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Replace lines 138-144 (0-indexed: 137-143)
new_ascii = '''ASCII_LOGO = r"""
  ██████╗ ██████╗ ███╗   ███╗██████╗ ██╗     ██████╗  ██████╗ ████████╗███████╗
 ██╔════╝██╔═══██╗████╗ ████║██╔══██╗██║     ██╔══██╗██╔═══██╗╚══██╔══╝██╔════╝
 ██║     ██║   ██║██╔████╔██║██████═╝ ██║     ██║  ██║██═══██║   ██══╝  ╚════██║
 ██║     ██═══██══╝██══════╝╚══════╝╚══════╝╚══════╝╚══════╝    ╚══════╝╚══════╝
"""
'''

# Lines 138-144 are the ascii logo (0-indexed: 137-143)
# Replace them
lines[137:144] = [new_ascii]

with open('downloader_tui.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')