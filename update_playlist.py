import urllib.request
import urllib.error
import json
import re
import os
from concurrent.futures import ThreadPoolExecutor

MASTER_CHANNELS = {
    "aztv": {
        "name": "AzTV",
        "group": "Azerbaycan",
        "tvg_id": "AzTV.az",
        "exact_matches": ["aztv", "az tv", "azerbaijan tv"]
    },
    "itv": {
        "name": "İTV HD",
        "group": "Azerbaycan",
        "tvg_id": "ITV.az",
        "exact_matches": ["itv", "itv hd", "ictimai tv", "ictimai"]
    },
    "baku tv": {
        "name": "Baku TV",
        "group": "Azerbaycan",
        "tvg_id": "BakuTV.az",
        "exact_matches": ["baku tv", "bakutv", "baku.tv", "baku-tv"]
    },
    "xəzər tv": {
        "name": "Xəzər TV",
        "group": "Azerbaycan",
        "tvg_id": "KhazarTV.az",
        "exact_matches": ["xəzər tv", "khazar tv", "xezer tv", "xezertv", "xəzər"]
    },
    "arb tv": {
        "name": "ARB TV",
        "group": "Azerbaycan",
        "tvg_id": "ARBTv.az",
        "exact_matches": ["arb tv", "azad azərbaycan", "arb"]
    },
    "arb 24": {
        "name": "ARB 24",
        "group": "Xeber",
        "tvg_id": "ARB24.az",
        "exact_matches": ["arb 24", "arb24"]
    },
    "arb günəş": {
        "name": "ARB Günəş",
        "group": "Usaq ve Senedli",
        "tvg_id": "ARBGunesh.az",
        "exact_matches": ["arb günəş", "arb gunes"]
    },
    "space tv": {
        "name": "Space TV",
        "group": "Azerbaycan",
        "tvg_id": "SpaceTV.az",
        "exact_matches": ["space tv", "spacetv", "space"]
    },
    "lider tv": {
        "name": "Lider TV",
        "group": "Azerbaycan",
        "tvg_id": "LiderTV.az",
        "exact_matches": ["lider tv", "lidertv", "lider"]
    },
    "mədəniyyət tv": {
        "name": "Mədəniyyət TV",
        "group": "Azerbaycan",
        "tvg_id": "MedeniyyetTV.az",
        "exact_matches": ["mədəniyyət tv", "medeniyyet tv", "mədəniyyət"]
    },
    "dunya tv": {
        "name": "Dünya TV",
        "group": "Azerbaycan",
        "tvg_id": "DunyaTV.az",
        "exact_matches": ["dunya tv", "dünya tv", "dunyatv"]
    },
    "cbc az": {
        "name": "CBC Azerbaijan",
        "group": "Azerbaycan",
        "tvg_id": "CBCAzerbaijan.az",
        "exact_matches": ["cbc az", "cbc azerbaijan", "cbcaz"]
    },
    "cbc sport": {
        "name": "CBC Sport",
        "group": "Idman",
        "tvg_id": "CBCSport.az",
        "exact_matches": ["cbc sport", "cbcsport"]
    },
    "idman az": {
        "name": "İdman Azərbaycan",
        "group": "Idman",
        "tvg_id": "IdmanAzerbaijan.az",
        "exact_matches": ["idman az", "idmanazerbaijan", "idman tv"]
    },
    "trt 1": {
        "name": "TRT 1",
        "group": "Turkiye - Esas",
        "tvg_id": "TRT1.tr",
        "exact_matches": ["trt 1", "trt1"]
    },
    "kanal d": {
        "name": "Kanal D",
        "group": "Turkiye - Esas",
        "tvg_id": "KanalD.tr",
        "exact_matches": ["kanal d", "kanald", "euro d"]
    },
    "show tv": {
        "name": "Show TV",
        "group": "Turkiye - Esas",
        "tvg_id": "ShowTV.tr",
        "exact_matches": ["show tv", "showtv", "show hd"]
    },
    "star tv": {
        "name": "Star TV",
        "group": "Turkiye - Esas",
        "tvg_id": "StarTV.tr",
        "exact_matches": ["star tv", "startv"]
    },
    "atv tr": {
        "name": "ATV",
        "group": "Turkiye - Esas",
        "tvg_id": "ATV.tr",
        "exact_matches": ["atv", "atv türkiye", "atv turkiye", "atv hd", "tr: atv", "a2 tv"]
    },
    "tv8": {
        "name": "TV8",
        "group": "Turkiye - Esas",
        "tvg_id": "TV8.tr",
        "exact_matches": ["tv8"]
    },
    "tv8.5": {
        "name": "TV8.5",
        "group": "Idman",
        "tvg_id": "TV85.tr",
        "exact_matches": ["tv8.5", "tv85", "tv 8.5"]
    },
    "now tv": {
        "name": "NOW TV",
        "group": "Turkiye - Esas",
        "tvg_id": "NowTV.tr",
        "exact_matches": ["now tv", "nowtv", "fox tv", "fox", "now hd"]
    },
    "kanal 7": {
        "name": "Kanal 7",
        "group": "Turkiye - Esas",
        "tvg_id": "Kanal7.tr",
        "exact_matches": ["kanal 7", "kanal7"]
    },
    "beyaz tv": {
        "name": "Beyaz TV",
        "group": "Turkiye - Esas",
        "tvg_id": "BeyazTV.tr",
        "exact_matches": ["beyaz tv", "beyaztv"]
    },
    "teve2": {
        "name": "Teve2",
        "group": "Turkiye - Esas",
        "tvg_id": "Teve2.tr",
        "exact_matches": ["teve2", "teve 2"]
    },
    "trt haber": {
        "name": "TRT Haber",
        "group": "Xeber",
        "tvg_id": "TRTHaber.tr",
        "exact_matches": ["trt haber", "trthaber"]
    },
    "trt spor": {
        "name": "TRT Spor",
        "group": "Idman",
        "tvg_id": "TRTSpor.tr",
        "exact_matches": ["trt spor", "trtspor", "trt spor yıldız"]
    },
    "a haber": {
        "name": "A Haber",
        "group": "Xeber",
        "tvg_id": "AHaber.tr",
        "exact_matches": ["a haber", "ahaber"]
    },
    "cnnturk": {
        "name": "CNN Türk",
        "group": "Xeber",
        "tvg_id": "CNNTurk.tr",
        "exact_matches": ["cnn türk", "cnn turk", "cnntürk"]
    },
    "haberturk": {
        "name": "Habertürk",
        "group": "Xeber",
        "tvg_id": "Haberturk.tr",
        "exact_matches": ["habertürk", "haberturk"]
    },
    "tgrt haber": {
        "name": "Tgrt Haber",
        "group": "Xeber",
        "tvg_id": "",
        "exact_matches": ["tgrt haber", "tgrthaber"]
    },
    "haber global": {
        "name": "Haber Global",
        "group": "Xeber",
        "tvg_id": "",
        "exact_matches": ["haber global"]
    },
    "halk tv": {
        "name": "Halk TV",
        "group": "Xeber",
        "tvg_id": "",
        "exact_matches": ["halk tv", "halktv"]
    },
    "ntv": {
        "name": "NTV",
        "group": "Xeber",
        "tvg_id": "",
        "exact_matches": ["ntv", "ntv hd"]
    }
}

def load_sources():
    sources = []
    # sources.txt faylına toxunulmur, olduğu kimi oxunur
    if os.path.exists("sources.txt"):
        with open("sources.txt", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and line not in sources:
                    sources.append(line)
                    
    # Əgər sources.txt boşdursa və ya yoxdursa standart ehtiyat siyahı
    if not sources:
        sources = [
            "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/az.m3u",
            "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/tr.m3u"
        ]

    return sources

def match_master_channel(channel_name):
    n = channel_name.lower().strip()
    n = re.sub(r'^(tr|az|hd|fhd|sd|hevc|4k):\s*', '', n).strip()
    
    if any(b in n for b in ["bein sports", "s sport", "exxen", "tivibu", "smart spor"]):
        return "BLOCKED", None

    for key, data in MASTER_CHANNELS.items():
        for exact in data["exact_matches"]:
            if exact == n or f" {exact} " in f" {n} " or n.startswith(f"{exact} ") or n.endswith(f" {exact}"):
                return key, data
                
    return None, None

def fetch_source_content(source_url):
    try:
        req = urllib.request.Request(source_url, headers={'User-Agent': 'VLC/3.0.18'})
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Mənbə oxunmadı ({source_url}): {e}")
        return ""

def process_channel(entry):
    extinf, stream_url = entry
    channel_name = extinf.split(',')[-1].strip()
    
    master_key, channel_info = match_master_channel(channel_name)
    if master_key == "BLOCKED":
        return None
        
    # 1. Əgər master kanaldırsa, öz təyin olunmuş qrupuna yazılır
    if master_key and channel_info:
        tvg_id = channel_info.get("tvg_id", "")
        return (master_key, channel_info["group"], channel_info["name"], tvg_id, stream_url)
    
    # 2. Master olmayan digər kanallar mənbədə hansı qrupdadırsa o şəkildə qalır
    group_match = re.search(r'group-title="([^"]+)"', extinf)
    group_title = group_match.group(1) if group_match else "Digər Kanallar"
    
    if not group_title or group_title.lower() in ["diger kanallar", "other", "unsorted"]:
        group_title = "Digər Kanallar"

    return (channel_name.lower() + "_" + stream_url, group_title, channel_name, "", stream_url)

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

    for entry in all_entries:
        result = process_channel(entry)
        if result:
            unique_key, group, name, tvg_id, stream_url = result
            if unique_key not in added_keys:
                if tvg_id:
                    extinf_line = f'#EXTINF:-1 tvg-id="{tvg_id}" tvg-group="{group}" group-title="{group}",{name}\n'
                else:
                    extinf_line = f'#EXTINF:-1 tvg-group="{group}" group-title="{group}",{name}\n'
                    
                final_playlist.append(f"{extinf_line}{stream_url}\n")
                added_keys.add(unique_key)

    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.writelines(final_playlist)
    
    count = len(added_keys)
    print(f"Yenilənmə tamamlandı! Cəmi {count} kanal uğurla 'playlist.m3u' faylına yazıldı.")

if __name__ == "__main__":
    main()
