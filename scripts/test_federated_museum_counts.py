import json

with open('data/top_museums_master_catalog.json') as f:
    museums = json.load(f)['museums']

# Load digital gallery 7865 + masterpieces
with open('data/digital_gallery_master_db.json') as f:
    dg = json.load(f).get('artworks', [])

with open('data/art_paintings_master_db.json') as f:
    pm = json.load(f).get('featured_masterpieces', [])

all_works = pm + dg

for m in museums:
    mid = m['id']
    m_artists = [a.lower() for a in m.get('artists', [])]
    
    count = 0
    for art in all_works:
        akr = (art.get('artist_name_kr') or art.get('artist') or '').lower().strip()
        aen = (art.get('artist_name_en') or '').lower().strip()
        mus = (art.get('museum') or art.get('location') or '').lower().strip()

        # Direct museum string match OR artist collection match
        direct_match = False
        if mid == 'louvre' and ('루브르' in mus or 'louvre' in mus): direct_match = True
        elif mid == 'moma' and ('moma' in mus or '근대미술관' in mus): direct_match = True
        elif mid == 'met' and ('메트로폴리탄' in mus or 'metropolitan' in mus): direct_match = True
        elif mid == 'orsay' and ('오르세' in mus or 'orsay' in mus): direct_match = True
        elif mid == 'prado' and ('프라도' in mus or 'prado' in mus): direct_match = True
        elif mid == 'uffizi' and ('우피치' in mus or 'uffizi' in mus): direct_match = True
        elif mid == 'national_gallery' and ('내셔널' in mus or 'national gallery' in mus): direct_match = True
        elif mid == 'nmk' and ('국립중앙박물관' in mus or '간송' in mus): direct_match = True
        elif mid == 'rijksmuseum' and ('암스테르담' in mus or 'rijks' in mus): direct_match = True
        elif mid == 'tate' and ('테이트' in mus or 'tate' in mus): direct_match = True

        artist_match = any(art_name in akr or akr in art_name for art_name in m_artists)
        
        if direct_match or artist_match:
            count += 1
            
    print(f"{m['name_kr']} ({mid}): {count} artworks matched")
