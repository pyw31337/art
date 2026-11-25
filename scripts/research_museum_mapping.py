import json

with open('data/digital_gallery_master_db.json') as f:
    dg = json.load(f)

artworks = dg.get('artworks', [])

# Map artists to their primary world-class museums
# e.g.:
# Van Gogh -> Van Gogh Museum, Amsterdam / Orsay / MoMA / Met
# Monet -> Musée d'Orsay / Marmottan Monet / Met
# Leonardo da Vinci -> Musée du Louvre
# Michelangelo / Raphael -> Vatican / Louvre / Uffizi
# Renoir, Degas, Cezanne -> Musée d'Orsay / Met
# Rembrandt, Vermeer -> Rijksmuseum, Amsterdam / Mauritshuis / Louvre
# Picasso -> Musée Picasso, Paris / MoMA, New York / Reina Sofía
# Rodin -> Musée Rodin, Paris
# Kim Hong-do, Jeong Seon, Shin Yun-bok -> National Museum of Korea / Kansong
# Velazquez, Goya -> Museo del Prado, Madrid
# Botticelli, Titian -> Galleria degli Uffizi, Florence
# Turner, Constable -> National Gallery, London / Tate Britain

print(f"Total artworks in digital gallery: {len(artworks)}")
