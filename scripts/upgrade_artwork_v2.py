#!/usr/bin/env python3
import re
import json

def generate_upgraded_artwork():
    with open('artwork.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Add SVG symbols if not present
    new_symbols = '''    <symbol id="i-chevron-left" viewBox="0 0 24 24">
      <polyline points="15 18 9 12 15 6"></polyline>
    </symbol>
    <symbol id="i-chevron-right" viewBox="0 0 24 24">
      <polyline points="9 18 15 12 9 6"></polyline>
    </symbol>
    <symbol id="i-clock" viewBox="0 0 24 24">
      <circle cx="12" cy="12" r="10"></circle>
      <polyline points="12 6 12 12 16 14"></polyline>
    </symbol>
'''
    if 'id="i-chevron-left"' not in content:
        content = content.replace('  </defs>', new_symbols + '  </defs>')

    print("Added new SVG symbols.")
    with open('artwork.html', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    generate_upgraded_artwork()
