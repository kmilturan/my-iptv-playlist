import urllib.request
import urllib.error
import json
import re
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

MASTER_CHANNELS = {
    "baku tv": {
        "name": "Baku TV",
        "group": "Azerbaycan",
        "tvg_id": "BakuTV.az",
        "aliases": ["baku tv", "bakutv", "baku-tv", "baku.tv", "baku"]
    },
    "itv": {
        "name": "İTV HD",
        "group": "Azerbaycan",
        "tvg_id": "ITV.az",
        "aliases": ["ictimai tv", "itv hd", "ictimai", "itv"]
    },
    "aztv": {
        "name": "AzTV",
        "group": "Azerbaycan",
        "tvg_id": "AzTV.az",
        "aliases": ["aztv", "azerbaijan tv", "az tv"]
    },
    "xəzər tv": {
        "name": "Xəzər TV",
        "group": "Azerbaycan",
        "tvg_id": "KhazarTV.az",
        "aliases": ["xəzər tv", "khazar tv", "xezer tv", "xezertv", "xəzər"]
    },
    "arb tv": {
        "name": "ARB TV",
        "group": "Azerbaycan",
        "tvg_id": "ARBTv.az",
        "aliases": ["arb tv", "azad azərbaycan", "arb"]
    },
    "arb 24": {
        "name": "ARB 24",
        "group": "Xeber",
        "tvg_id": "ARB24.az",
        "aliases": ["arb 24", "arb24"]
    },
    "arb günəş": {
        "name": "ARB Günəş",
        "group": "Usaq ve Senedli",
        "tvg_id": "ARBGunesh.az",
        "aliases": ["arb günəş", "arb gunes"]
    },
    "space tv": {
        "name": "Space TV",
        "group": "Azerbaycan",
        "tvg_id": "SpaceTV.az",
        "aliases": ["space tv", "spacetv", "space"]
    },
    "lider tv": {
        "name": "Lider TV",
        "group": "Azerbaycan",
        "tvg_id": "LiderTV.az",
        "aliases": ["lider tv", "lidertv", "lider"]
    },
    "mədəniyyət tv": {
        "name": "Mədəniyyət TV",
        "group": "Azerbaycan",
        "tvg_id": "MedeniyyetTV.az",
        "aliases": ["mədəniyyət tv", "medeniyyet tv", "mədəniyyət"]
    },
    "dunya tv": {
        "name": "Dünya TV",
        "group": "Azerbaycan",
        "tvg_id": "DunyaTV.az",
        "aliases": ["dunya tv", "dünya tv", "dunyatv"]
    },
    "cbc az": {
        "name": "CBC Azerbaijan",
        "group": "Azerbaycan",
        "tvg_id": "CBCAzerbaijan.az",
        "aliases": ["cbc az", "cbc azerbaijan", "cbcaz"]
    },
    "cbc sport": {
        "name": "CBC Sport",
        "group": "Idman",
        "tvg_id": "CBCSport.az",
        "aliases": ["cbc sport", "cbcsport"]
    },
    "idman az": {
        "name": "İdman Azərbaycan",
        "group": "Idman",
        "tvg_id": "IdmanAzerbaijan.az",
        "aliases": ["idman az", "idmanazerbaijan", "idman tv", "idman"]
    },
    "trt 1": {
        "name": "TRT 1",
        "group": "Turkiye - Esas",
        "tvg_id": "TRT1.tr",
        "aliases": ["trt 1", "trt1"]
    },
    "kanal d": {
        "name": "Kanal D",
        "group": "Turkiye - Esas",
        "tvg_id": "KanalD.tr",
        "aliases": ["kanal d", "kanald"]
    },
    "show tv": {
        "name": "Show TV",
        "group": "Turkiye - Esas",
        "tvg_id": "ShowTV.tr",
        "aliases": ["show tv", "showtv"]
    },
    "star tv": {
        "name": "Star TV",
        "group": "Turkiye - Esas",
        "tvg_id": "StarTV.tr",
        "aliases": ["star tv", "startv"]
    },
    "atv tr": {
        "name": "ATV",
        "group": "Turkiye - Esas",
        "tvg_id": "ATV.tr",
        "aliases": ["atv", "atv türkiye", "atv turkiye", "atv hd", "tr: atv"]
    },
    "tv8": {
        "name": "TV8",
        "group": "Turkiye - Esas",
        "tvg_id": "TV8.tr",
        "aliases": ["tv8"]
    },
    "tv8.5": {
        "name": "TV8.5",
        "group": "Idman",
        "tvg_id": "TV85.tr",
        "aliases": ["tv8.5", "tv85", "tv 8.5"]
    },
    "now tv": {
        "name": "NOW TV",
        "group": "Turkiye - Esas",
        "tvg_id": "NowTV.tr",
        "aliases": ["now tv", "nowtv", "fox tv", "fox"]
    },
    "kanal 7": {
        "name": "Kanal 7",
        "group": "Turkiye - Esas",
        "tvg_id": "Kanal7.tr",
        "aliases": ["kanal 7", "kanal7"]
    },
    "beyaz tv": {
        "name": "Beyaz TV",
        "group": "Turkiye - Esas",
        "tvg_id": "BeyazTV.tr",
        "aliases": ["beyaz tv", "beyaztv", "tr: beyaz tv"]
    },
    "teve2": {
        "name": "Teve2",
        "group": "Turkiye - Esas",
        "tvg_id": "Teve2.tr",
        "aliases": ["teve2", "teve 2"]
    },
    "trt haber": {
        "name": "TRT Haber",
        "group": "Xeber",
        "tvg_id": "TRTHaber.tr",
        "aliases": ["trt haber", "trthaber"]
    },
    "trt spor": {
        "name": "TRT Spor",
        "group": "Idman",
        "tvg_id": "TRTSpor.tr",
        "aliases": ["trt spor", "trtspor"]
    },
    "a haber": {
        "name": "A Haber",
        "group": "Xeber",
        "tvg_id": "AHaber.tr",
        "aliases": ["a haber", "ahaber"]
    },
    "cnnturk": {
        "name": "CNN Türk",
        "group": "Xeber",
        "tvg_id": "CNNTurk.tr",
        "aliases": ["cnn türk", "cnn turk", "cnntürk"]
    },
    "haberturk": {
        "name": "Habertürk",
        "group": "Xeber",
        "tvg_id": "Haberturk.tr",
        "aliases": ["habertürk", "haberturk"]
    }
}

def load_and_update_sources():
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
            "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/tr.m3u",
            "https://raw.githubusercontent.com/Free-TV/IPTV/refs/heads/master/playlists/playlist_azerbaijan.m3u8"
        ]

    directories = [
        "https://raw.githubusercontent.com/iptv-org/iptv/master/index.m3u",
        "https://raw.githubusercontent.com/Free-TV/IPTV/master/playlist.m3u"
    ]
    
    new_found = False
    for dir_url in directories:
        try:
            req = urllib.request.Request(dir_url, headers={'User-Agent': 'VLC/3.0.18'})
            with urllib.request.urlopen(req, timeout=8) as response:
                content = response.read().decode('utf-8', errors='ignore')
                found_links = re.findall(r'https?://[^\s]+\.(?:m3u|m3u8)', content, re.IGNORECASE)
                for link in found_links:
                    if any(k in link.lower() for k in ["az", "turkey", "tr", "azerbaijan"]):
                        if link not in sources:
                            sources.append(link)
                            new_found = True
        except Exception:
            pass

    if new_found:
        with open("sources.txt", "w", encoding="utf-8") as f:
            f.write("# Avtomatik yenilənən və genişlənən IPTV mənbələri\n")
            for s in sources:
                f.write(f"{s}\n")

    return sources

def match_master_channel(channel_name):
    n = channel_name.lower().strip()
    # Prefiksləri təmizləyirik (məsələn "tr: ", "az: " və s.)
    n = re.sub(r'^(tr|az|hd|fhd|sd):\s*', '', n).strip()
    
    if any(b in n for b in ["bein sports", "s sport", "exxen", "tivibu", "smart spor"]):
        return "BLOCKED", None

    for key, data in MASTER_CHANNELS.items():
        for alias in data["aliases"]:
            clean_alias = re.sub(r'^(tr|az):\s*', '', alias).strip()
            if clean_alias == n or f" {clean_alias} " in f" {n} " or n.startswith(f"{clean_alias} ") or n.endswith(f" {clean_alias}"):
                return key, data
            elif len(clean_alias) <= 5 and clean_alias in n.split():
                return key, data
                
    return None, None

def is_stream_valid(url):
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'VLC/3.0.18', 'Accept': '*/*'}
        )
        with urllib.request.urlopen(req, timeout=3) as response:
            if response.getcode() in [200, 301, 302]:
                return True
    except Exception:
        return False
    return False

def process_channel(entry):
    extinf, stream_url = entry
    channel_name = extinf.split(',')[-1].strip()
    
    master_key, channel_info = match_master_channel(channel_name)
    if master_key == "BLOCKED":
        return None
        
    if master_key and channel_info:
        if not is_stream_valid(stream_url):
            return None
        return (master_key, channel_info["group"], channel_info["name"], channel_info["tvg_id"], stream_url)
    
    l_name = channel_name.lower()
    if not any(k in l_name for k in ["az", "azerbaijan", "tr", "türkiye", "turkey", "baku", "baki"]):
        return None

    if not is_stream_valid(stream_url):
        return None

    group_match = re.search(r'group-title="([^"]+)"', extinf)
    group_title = group_match.group(1) if group_match else "Diger Kanallar"
    group_title = re.sub(r'[^\w\s\-\.]', '', group_title).strip()
    if not group_title:
        group_title = "Diger Kanallar"
    
    return (channel_name.lower(), group_title, channel_name, "", stream_url)

def main():
    sources = load_and_update_sources()
    print(f"Aktiv mənbə sayı: {len(sources)}")

    all_entries = []
    for source_url in sources:
        try:
            req = urllib.request.Request(source_url, headers={'User-Agent': 'VLC/3.0.18'})
            with urllib.request.urlopen(req, timeout=8) as response:
                content = response.read().decode('utf-8', errors='ignore')

            entries = re.findall(r'(#EXTINF:[^\n]+\n)(https?://[^\s]+)', content)
            all_entries.extend(entries)
        except Exception:
            pass

    print(f"Tapıldı: {len(all_entries)} xam kanal yoxlanılır...")

    final_playlist = ["#EXTM3U\n"]
    added_keys = set()

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(process_channel, entry) for entry in all_entries]
        
        for future in as_completed(futures):
            result = future.result()
            if result:
                unique_key, group, name, tvg_id, stream_url = result
                if unique_key not in added_keys:
                    # OTTPlayer üçün həm group-title, həm də tvg-group atributlarını əlavə edirik
                    if tvg_id:
                        extinf_line = f'#EXTINF:-1 tvg-id="{tvg_id}" tvg-group="{group}" group-title="{group}",{name}\n'
                    else:
                        extinf_line = f'#EXTINF:-1 tvg-group="{group}" group-title="{group}",{name}\n'
                        
                    final_playlist.append(f"{extinf_line}{stream_url}\n")
                    added_keys.add(unique_key)

    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.writelines(final_playlist)
    
    print(f"Yenilənmə tamamlandı! Cəmi {len(added_keys)} təmiz kanal qruplara ayrılaraq yazıldı.")

if __name__ == "__main__":
    main()
