import urllib.request
import urllib.error
import re
import os
from concurrent.futures import ThreadPoolExecutor

# Əsas kanallar və onların aid olduğu dəqiq qruplar
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
    
    # Türkiyə və Xəbər / İdman əsaslar
    "trt 1": {"name": "TRT 1", "group": "Turkiye - Esas", "tvg_id": "TRT1.tr", "matches": ["trt 1", "trt1"]},
    "kanal d": {"name": "Kanal D", "group": "Turkiye - Esas", "tvg_id": "KanalD.tr", "matches": ["kanal d", "kanald", "euro d"]},
    "show tv": {"name": "Show TV", "group": "Turkiye - Esas", "tvg_id": "ShowTV.tr", "matches": ["show tv", "showtv", "show hd"]},
    "star tv": {"name": "Star TV", "group": "Turkiye - Esas", "tvg_id": "StarTV.tr", "matches": ["star tv", "startv"]},
    "atv tr": {"name": "ATV", "group": "Turkiye - Esas", "tvg_id": "ATV.tr", "matches": ["atv türkiye", "atv turkiye", "tr: atv", "atv hd"]},
    "tv8": {"name": "TV8", "group": "Turkiye - Esas", "tvg_id": "TV8.tr", "matches": ["tv8"]},
    "tv8.5": {"name": "TV8.5", "group": "Idman", "tvg_id": "TV85.tr", "matches": ["tv8.5", "tv85", "tv 8.5"]},
    "now tv": {"name": "NOW TV", "group": "Turkiye - Esas", "tvg_id": "NowTV.tr", "matches": ["now tv", "nowtv", "fox tv", "fox hd"]},
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
    "ntv": {"name": "NTV", "group": "Xeber", "tvg_id": "", "matches": ["ntv", "ntv hd"]}
}

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
    
    # Blok olunan (ödənişli/premium) kanalları çıxarırıq
    if any(b in name_lower for b in ["bein sports", "s sport", "exxen", "tivibu", "smart spor", "d-smart"]):
        return None

    # 1. Master kanallar siyahısı ilə dəqiq yoxlama
    for key, data in MASTER_CHANNELS.items():
        for match in data["matches"]:
            # Tam ad uyğunluğu və ya söz içi dəqiq keçməsi
            if match == name_lower or f" {match} " in f" {name_lower} " or name_lower.startswith(f"{match} ") or name_lower.endswith(f" {match}"):
                return data["group"], data["name"], data["tvg_id"]

    # 2. Ağıllı Kateqoriya Təyini (Mənbə qrupuna və ya ada görə)
    group_lower = raw_group.lower() if raw_group else ""
    
    # İdman kanalları
    if any(k in group_lower or k in name_lower for k in ["idman", "sport", "futbol", "nba", "fight"]):
        return "Idman", channel_name, ""
        
    # Xəbər kanalları
    if any(k in group_lower or k in name_lower for k in ["xeber", "haber", "news"]):
        return "Xeber", channel_name, ""
        
    # Uşaq və Sənədli
    if any(k in group_lower or k in name_lower for k in ["usaq", "çocuk", "kids", "cartoon", "senedli", "belgesel", "discovery", "nat geo"]):
        return "Usaq ve Senedli", channel_name, ""

    # Azərbaycan kanalları (ümumi ad/qrup əsaslı)
    if any(k in group_lower or k in name_lower for k in ["azerbaycan", "azerbaijan", "az"]):
        return "Azerbaycan", channel_name, ""

    # Türkiyə kanalları
    if any(k in group_lower or k in name_lower for k in ["turkiye", "turkey", "tr"]):
        return "Turkiye - Esas", channel_name, ""

    # Digər qalanlar
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
        # Kanal adını və qrupunu çıxarırıq
        channel_name = extinf.split(',')[-1].strip()
        group_match = re.search(r'group-title="([^"]+)"', extinf)
        raw_group = group_match.group(1) if group_match else ""

        classification = classify_channel(channel_name, raw_group)
        if not classification:
            continue # Bloklanıbsa keç

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
    
    print(f"Yenilənmə tamamlandı! Cəmi {len(added_keys)} kanal kateqoriyalara ayrılaraq 'playlist.m3u' faylına yazıldı.")

if __name__ == "__main__":
    main()
