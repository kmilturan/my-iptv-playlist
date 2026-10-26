import urllib.request
import urllib.error
import re
import os
from concurrent.futures import ThreadPoolExecutor

# Dəqiq master kanallar siyahısı
MASTER_CHANNELS = {
    "aztv": {"name": "AzTV", "group": "Azerbaycan", "tvg_id": "AzTV.az", "matches": ["aztv", "az tv", "azerbaijan tv"]},
    "itv": {"name": "İTV HD", "group": "Azerbaycan", "tvg_id": "ITV.az", "matches": ["itv", "itv hd", "ictimai tv", "ictimai"]},
    "baku tv": {"name": "Baku TV", "group": "Azerbaycan", "tvg_id": "BakuTV.az", "matches": ["baku tv", "bakutv", "baku.tv", "baku-tv"]},
    "xəzər tv": {"name": "Xəzər TV", "group": "Azerbaycan", "tvg_id": "KhazarTV.az", "matches": ["xəzər tv", "khazar tv", "xezer tv", "xəzər"]},
    "arb tv": {"name": "ARB TV", "group": "Azerbaycan", "tvg_id": "ARBTv.az", "matches": ["arb tv", "azad azərbaycan", "arb hd"]},
    "arb 24": {"name": "ARB 24", "group": "Xeber", "tvg_id": "ARB24.az", "matches": ["arb 24", "arb24"]},
    "arb günəş": {"name": "ARB Günəş", "group": "Usaq ve Senedli", "tvg_id": "ARBGunesh.az", "matches": ["arb günəş", "arb gunes"]},
    "space tv": {"name": "Space TV", "group": "Azerbaycan", "tvg_id": "SpaceTV.az", "matches": ["space tv", "spacetv"]},
    "mədəniyyət tv": {"name": "Mədəniyyət TV", "group": "Azerbaycan", "tvg_id": "MedeniyyetTV.az", "matches": ["mədəniyyət tv", "medeniyyet tv"]},
    "dunya tv": {"name": "Dünya TV", "group": "Azerbaycan", "tvg_id": "DunyaTV.az", "matches": ["dunya tv", "dünya tv", "dunyatv"]},
    "cbc az": {"name": "CBC Azerbaijan", "group": "Azerbaycan", "tvg_id": "CBCAzerbaijan.az", "matches": ["cbc az", "cbc azerbaijan", "cbcaz"]},
    "cbc sport": {"name": "CBC Sport", "group": "Idman", "tvg_id": "CBCSport.az", "matches": ["cbc sport", "cbcsport"]},
    "idman az": {"name": "İdman Azərbaycan", "group": "Idman", "tvg_id": "IdmanAzerbaijan.az", "matches": ["idman az", "idmanazerbaijan", "idman tv"]},
    
    # Türkiyə və əsaslar
    "trt 1": {"name": "TRT 1", "group": "Turkiye - Esas", "tvg_id": "TRT1.tr", "matches": ["trt 1", "trt1"]},
    "kanal d": {"name": "Kanal D", "group": "Turkiye - Esas", "tvg_id": "KanalD.tr", "matches": ["kanal d", "kanald", "euro d"]},
    "show tv": {"name": "Show TV", "group": "Turkiye - Esas", "tvg_id": "ShowTV.tr", "matches": ["show tv", "showtv", "show hd"]},
    "star tv": {"name": "Star TV", "group": "Turkiye - Esas", "tvg_id": "StarTV.tr", "matches": ["star tv", "startv"]},
    "atv tr": {"name": "ATV", "group": "Turkiye - Esas", "tvg_id": "ATV.tr", "matches": ["atv türkiye", "atv turkiye", "tr: atv", "atv hd", "atv tr"]},
    "tv8": {"name": "TV8", "group": "Turkiye - Esas", "tvg_id": "TV8.tr", "matches": ["tv8"]},
    "tv8.5": {"name": "TV8.5", "group": "Idman", "tvg_id": "TV85.tr", "matches": ["tv8.5", "tv85", "tv 8.5"]},
    "now tv": {"name": "NOW TV", "group": "Turkiye - Esas", "tvg_id": "NowTV.tr", "matches": ["now tv", "nowtv", "fox tv", "fox hd", "now tr"]},
    "kanal 7": {"name": "Kanal 7", "group": "Turkiye - Esas", "tvg_id": "Kanal7.tr", "matches": ["kanal 7", "kanal7"]},
    "beyaz tv": {"name": "Beyaz TV", "group": "Turkiye - Esas", "tvg_id": "BeyazTV.tr", "matches": ["beyaz tv", "beyaztv"]},
    "teve2": {"name": "Teve2", "group": "Turkiye - Esas", "tvg_id": "Teve2.tr", "matches": ["teve2", "teve 2"]},
    "trt haber": {"name": "TRT Haber", "group": "Xeber", "tvg_id": "TRTHaber.tr", "matches": ["trt haber", "trthaber"]},
    "trt spor": {"name": "TRT Spor", "group": "Idman", "tvg_id": "TRTSpor.tr", "matches": ["trt spor", "trtspor", "trt spor yıldız"]},
    "a haber": {"name": "A Haber", "group": "Xeber", "tvg_id": "AHaber.tr", "matches": ["a haber", "ahaber"]},
    "cnnturk": {"name": "CNN Türk", "group": "Xeber", "tvg_id": "CNNTurk.tr", "matches": ["cnn türk", "cnn turk", "cnntürk"]},
    "haberturk": {"name": "Habertürk", "group": "Xeber", "tvg_id": "Haberturk.tr", "matches": ["habertürk", "haberturk"]},
    "haberglobal": {"name": "Haber Global", "group": "Xeber", "tvg_id": "", "matches": ["haber global"]},
    "halk tv": {"name": "Halk TV", "group": "Xeber", "tvg_id": "", "matches": ["halk tv", "halktv"]},
    "ntv": {"name": "NTV", "group": "Xeber", "tvg_id": "", "matches": ["ntv tr", "ntvturkey", "ntv türkiye"]}
}

# Yanlış/xarici qarışıq kanalları süzmək üçün açar sözlər
EXCLUDED_KEYWORDS = ["russia", "ru:", "ukraine", "ua:", "bulgaria", "poland", "fox kids russia"]

def load_sources():
    sources = []
    if os.path.exists("sources.txt"):
        with open("sources.txt", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and line not in sources:
                    sources.append(line)
                    
    if not sources:
        sources = [
            "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/az.m3u",
            "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/tr.m3u"
        ]
    return sources

def classify_channel(channel_name, raw_group):
    name_lower = channel_name.lower().strip()
    
    # Ödənişli / premium kanalları blokla
    if any(b in name_lower for b in ["bein sports", "s sport", "exxen", "tivibu", "smart spor", "d-smart"]):
        return None

    # Xarici zibil/rus kanallarını blokla
    if any(ex in name_lower for ex in EXCLUDED_KEYWORDS):
        return None

    # 1. Master kanallarla dəqiq yoxlama
    for key, data in MASTER_CHANNELS.items():
        for match in data["matches"]:
            pattern = r'(^|\b)' + re.escape(match) + r'(\b|$)'
            if re.search(pattern, name_lower):
                if match in ["now tv", "nowtv", "fox tv", "fox"] and ("ru" in name_lower or "us" in name_lower):
                    continue
                return data["group"], data["name"], data["tvg_id"]

    # 2. Qrup və ya ada görə kateqoriya təyini
    group_lower = raw_group.lower() if raw_group else ""
    
    if any(k in group_lower or k in name_lower for k in ["idman", "sport", "futbol"]):
        return "Idman", channel_name, ""
        
    if any(k in group_lower or k in name_lower for k in ["xeber", "haber", "news"]):
        return "Xeber", channel_name, ""
        
    if any(k in group_lower or k in name_lower for k in ["usaq", "çocuk", "kids", "senedli", "belgesel"]):
        return "Usaq ve Senedli", channel_name, ""

    if "azerbaycan" in group_lower or "azerbaijan" in group_lower or "az" in group_lower:
        return "Azerbaycan", channel_name, ""
        
    if "turkiye" in group_lower or "turkey" in group_lower or "tr" in group_lower:
        return "Turkiye - Esas", channel_name, ""

    # 3. Kateqoriyası dəqiq bilinməyən digər sağlam kanallar "Digər Kanallar" altına yığılır
    return "Digər Kanallar", channel_name, ""

def fetch_source_content(source_url):
    try:
        req = urllib.request.Request(source_url, headers={'User-Agent': 'VLC/3.0.18'})
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Mənbə oxunmadı ({source_url}): {e}")
        return ""

def main():
    sources = load_sources()
    print(f"Aktiv mənbə sayı: {len(sources)}")

    all_entries = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        contents = list(executor.map(fetch_source_content, sources))
        
    for content in contents:
        if content:
            entries = re.findall(r'(#EXTINF:[^\n]+\n)(https?://[^\s]+)', content)
            all_entries.extend(entries)

    print(f"Tapıldı: {len(all_entries)} xam kanal emal olunur...")

    final_playlist = ["#EXTM3U\n"]
    added_keys = set()

    for extinf, stream_url in all_entries:
        channel_name = extinf.split(',')[-1].strip()
        group_match = re.search(r'group-title="([^"]+)"', extinf)
        raw_group = group_match.group(1) if group_match else ""

        classification = classify_channel(channel_name, raw_group)
        if not classification:
            continue

        group, name, tvg_id = classification
        unique_key = name.lower() + "_" + stream_url

        if unique_key not in added_keys:
            if tvg_id:
                extinf_line = f'#EXTINF:-1 tvg-id="{tvg_id}" tvg-group="{group}" group-title="{group}",{name}\n'
            else:
                extinf_line = f'#EXTINF:-1 tvg-group="{group}" group-title="{group}",{name}\n'
                
            final_playlist.append(f"{extinf_line}{stream_url}\n")
            added_keys.add(unique_key)

    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.writelines(final_playlist)
    
    print(f"Yenilənmə tamamlandı! Cəmi {len(added_keys)} kanal kateqoriyalara və 'Digər Kanallar' bölməsinə ayrılaraq yazıldı.")

if __name__ == "__main__":
    main()
