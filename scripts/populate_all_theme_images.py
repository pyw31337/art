import os, json, urllib.request, time
from PIL import Image

def get_file_thumb(title, width=1920):
    url = f'https://commons.wikimedia.org/w/api.php?action=query&titles={urllib.parse.quote(title)}&prop=imageinfo&iiprop=url&iiurlwidth={width}&format=json'
    req = urllib.request.Request(url, headers={'User-Agent': 'LetsArt/1.0 (dev@letsart.io)'})
    try:
        with urllib.request.urlopen(req, timeout=12) as r:
            d = json.loads(r.read().decode('utf-8'))
            for p in d['query']['pages'].values():
                if 'imageinfo' in p:
                    info = p['imageinfo'][0]
                    return info.get('thumburl') or info.get('url')
    except Exception as e:
        print(f"Error getting thumb for {title}: {e}")
    return None

def download_and_save_webp(url, dest_path):
    req = urllib.request.Request(url, headers={'User-Agent': 'LetsArt/1.0 (dev@letsart.io)'})
    with urllib.request.urlopen(req, timeout=15) as resp:
        import io
        im = Image.open(io.BytesIO(resp.read())).convert('RGB')
        im.save(dest_path, 'WEBP', quality=82)

# Specific title mappings for items
mapping = {
    ('color_mint', 'mint_01'): 'File:1957 Chevrolet Bel Air (green).jpg',
    ('color_mint', 'mint_03'): 'File:Mint leaves (Mentha spicata).jpg',
    ('color_mint', 'mint_04'): 'File:Door in Gamla Stan Stockholm (2012).jpg',
    ('color_mint', 'mint_05'): 'File:Aurora Borealis over Tromsø.jpg',
    ('color_mint', 'mint_06'): 'File:Eucalyptus trees in Agioi Apostoli. Crete, Greece.jpg',
    ('color_mint', 'mint_11'): 'File:Emerald Cove, Lake Tahoe.jpg',
    ('color_mint', 'mint_12'): 'File:Claude Monet - Water Lilies - Google Art Project.jpg',
    
    ('camping_forest', 'camp_02'): 'File:Campfire and sparks in Anttoora 3.jpg',
    ('camping_forest', 'camp_04'): 'File:Canoe on Lake Louise, Alberta, Canada.jpg',
    ('camping_forest', 'camp_09'): 'File:Morning mist over Lake Bled.jpg',
    ('camping_forest', 'camp_11'): 'File:Volkswagen T2 camper van.jpg',
    ('camping_forest', 'camp_12'): 'File:Vincent van Gogh - The Olive Trees - Google Art Project.jpg',

    ('midnight_blue', 'night_03'): 'File:Sunbeams into underwater cave.jpg',
    ('midnight_blue', 'night_07'): 'File:Fog in Paris (Unsplash).jpg',
    ('midnight_blue', 'night_10'): 'File:Bioluminescence in Maldives.jpg',

    ('monet_garden', 'monet_01'): 'File:Detail of "The Water-Lily Pond" by Claude Monet 02.jpg',
    ('monet_garden', 'monet_02'): 'File:Vincent van Gogh - Peach Tree in Blossom (Souvenir de Mauve) - Google Art Project.jpg',
    ('monet_garden', 'monet_03'): 'File:Pierre-Auguste Renoir - Luncheon of the Boating Party - Google Art Project.jpg',
    ('monet_garden', 'monet_04'): 'File:Claude Monet - Woman with a Parasol - Madame Monet and Her Son - Google Art Project.jpg',
    ('monet_garden', 'monet_05'): 'File:Camille Pissarro - The Orchard - Google Art Project.jpg',
    ('monet_garden', 'monet_06'): 'File:Edgar Germain Hilaire Degas 021.jpg',
    ('monet_garden', 'monet_07'): 'File:Paul Cézanne - Mont Sainte-Victoire - Google Art Project (718366).jpg',
    ('monet_garden', 'monet_08'): 'File:Gustav Klimt - Birch Forest (1903).jpg',
    ('monet_garden', 'monet_09'): 'assets/featured/art_seurat_grande_jatte.webp',
    ('monet_garden', 'monet_10'): 'File:Alfred Sisley - Snow at Louveciennes - Google Art Project.jpg',
    ('monet_garden', 'monet_11'): 'File:Gustave Caillebotte - Paris Street; Rainy Day - Google Art Project.jpg',
    ('monet_garden', 'monet_12'): 'File:Claude Monet - Coquelicots (Poppies) - Google Art Project.jpg',

    ('zen_minimal', 'zen_01'): 'File:Ryoan-ji rock garden in spring.jpg',
    ('zen_minimal', 'zen_02'): 'assets/featured/arch_tadao_ando_church_of_light.webp',
    ('zen_minimal', 'zen_03'): 'File:Arashiyama bamboo grove path.jpg',
    ('zen_minimal', 'zen_04'): 'assets/featured/cont_art_lee_ufan.webp',
    ('zen_minimal', 'zen_05'): 'File:Traditional Japanese tatami room with shoji.jpg',
    ('zen_minimal', 'zen_06'): 'File:Water droplet splash.jpg',
    ('zen_minimal', 'zen_07'): 'File:Desert sand dune ripples.jpg',
    ('zen_minimal', 'zen_08'): 'File:BonsaiTridentMaple.jpg',
    ('zen_minimal', 'zen_11'): 'assets/featured/arch_zaha_hadid_ddp.webp'
}

for (t_id, i_id), target in mapping.items():
    dest = f'assets/themes/{t_id}/{i_id}.webp'
    os.makedirs(f'assets/themes/{t_id}', exist_ok=True)
    if target.startswith('assets/featured/'):
        im = Image.open(target).convert('RGB')
        im.save(dest, 'WEBP', quality=82)
        print(f"Copied local {target} -> {dest}")
        continue
    
    time.sleep(0.5)
    u = get_file_thumb(target)
    if not u:
        # Fallback to search query
        clean_title = target.replace('File:', '').rsplit('.', 1)[0][:30]
        url_search = f'https://commons.wikimedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(clean_title)}&srnamespace=6&srlimit=1&format=json'
        try:
            req = urllib.request.Request(url_search, headers={'User-Agent': 'LetsArt/1.0 (dev@letsart.io)'})
            with urllib.request.urlopen(req) as r:
                d = json.loads(r.read().decode('utf-8'))
                res = d.get('query', {}).get('search', [])
                if res:
                    u = get_file_thumb(res[0]['title'])
        except Exception:
            pass

    if u:
        try:
            download_and_save_webp(u, dest)
            print(f"Saved {dest} from {u[:50]} ({os.path.getsize(dest):,}B)")
        except Exception as e:
            print(f"Failed download {dest}: {e}")
    else:
        print(f"No thumb found for: {target}")

print("Image population finished!")
