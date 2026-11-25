with open('artwork.html', 'r', encoding='utf-8') as f:
    c = f.read()

brand_symbols = """    <symbol id="i-brand-museum" viewBox="0 0 24 24">
      <path fill="#2563EB" d="M12 2L2 7v2h20V7L12 2zM4 11v8h3v-8H4zm6 0v8h4v-8h-4zm7 0v8h3v-8h-3zM2 20v2h20v-2H2z"/>
    </symbol>
    <symbol id="i-brand-handmaker" viewBox="0 0 24 24">
      <circle cx="12" cy="12" r="10" fill="#D97706"/>
      <path fill="#FFFFFF" d="M8 7h8v2H8zm0 4h8v2H8zm0 4h5v2H8z"/>
    </symbol>
"""

if 'id="i-brand-museum"' not in c:
    c = c.replace('</defs>', brand_symbols + '  </defs>')

# Update getPlatformIcon in artwork.html:
c = c.replace(
    "if (plat === 'museum_official') return '#i-museum';",
    "if (plat === 'museum_official') return '#i-brand-museum';"
)
c = c.replace(
    "if (plat === 'handmaker') return '#i-sparkles';",
    "if (plat === 'handmaker') return '#i-brand-handmaker';"
)

with open('artwork.html', 'w', encoding='utf-8') as f:
    f.write(c)
print("Updated museum and handmaker vector brand icons.")
