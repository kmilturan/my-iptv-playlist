import urllib.request
import urllib.error
import json
import re
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

# Master Mapping: Əsas xüsusi nəzarətdə olan kanallarımız
MASTER_CHANNELS = {
    "baku tv": {
        "name": "Baku TV",
        "group": "🇦🇿 Azərbaycan",
        "tvg_id": "BakuTV.az",
        "aliases": ["baku tv", "bakutv", "baku-tv", "baku"]
    },
    "itv": {
        "name": "İTV HD",
        "group": "🇦🇿 Azərbaycan",
        "tvg_id": "ITV.az",
        "aliases": ["ictimai", "itv", "ictimai tv"]
    },
    "aztv": {
        "name": "AzTV",
        "group": "🇦🇿 Azərbaycan",
        "tvg_id": "AzTV.az",
        "aliases": ["aztv", "azerbaijan tv", "az tv"]
    },
    "xəzər tv": {
        "name": "Xəzər TV",
        "group": "🇦🇿 Azərbaycan",
        "tvg_id": "KhazarTV.az",
        "aliases": ["xəzər", "khazar", "xezer tv", "xezertv"]
    },
    "arb tv": {
        "name": "ARB TV",
        "group": "🇦🇿 Azərbaycan",
        "tvg_id": "ARBTv.az",
        "aliases": ["arb tv", "arb", "azad azərbaycan"]
    },
    "arb 24": {
        "name": "ARB 24",
        "group": "📰 Xəbər",
        "tvg_id": "ARB24.az",
        "aliases": ["arb 24", "arb24"]
    },
    "arb günəş": {
        "name": "ARB Günəş",
        "group": "🧸 Uşaq & Sənədli",
        "tvg_id": "ARBGunesh.az",
        "aliases": ["arb günəş", "arb gunes", "gunes tv"]
    },
    "space tv": {
        "name": "Space TV",
        "group": "🇦🇿 Azərbaycan",
        "tvg_id": "SpaceTV.az",
        "aliases": ["space", "space tv", "spacetv"]
    },
    "lider tv": {
        "name": "Lider TV",
        "group": "🇦🇿 Azərbaycan",
        "tvg_id": "LiderTV.az",
        "aliases": ["lider", "lider tv", "lidertv"]
    },
    "mədəniyyət tv": {
        "name": "Mədəniyyət TV",
        "group": "🇦🇿 Azərbaycan",
        "tvg_id": "MedeniyyetTV.az",
        "aliases": ["mədəniyyət", "medeniyyet", "medeniyyet tv"]
    },
    "dunya tv": {
        "name": "Dünya TV",
        "group": "🇦🇿 Azərbaycan",
        "tvg_id": "DunyaTV.az",
        "aliases": ["dunya tv", "dünya tv", "dunyatv"]
    },
    "cbc az": {
        "name": "CBC Azerbaijan",
        "group": "🇦🇿 Azərbaycan",
        "tvg_id": "CBCAzerbaijan.az",
        "aliases": ["cbc az", "cbc azerbaijan", "cbcaz"]
    },
    "cbc sport": {
        "name": "CBC Sport",
        "group": "⚽ İdman",
        "tvg_id": "CBCSport.az",
        "aliases": ["cbc sport", "cbcsport"]
    },
    "idman az": {
        "name": "İdman Azərbaycan",
        "group": "⚽ İdman",
        "tvg_id": "IdmanAzerbaijan.az",
        "aliases": ["idman az", "idmanazerbaijan", "idman tv"]
    },
    "trt 1": {
        "name": "TRT 1",
        "group": "🇹🇷 Türkiyə - Əsas",
        "tvg_id": "TRT1.tr",
        "aliases": ["trt 1", "trt1"]
    },
    "kanal d": {
        "name": "Kanal D",
        "group": "🇹🇷 Türkiyə - Əsas",
        "tvg_id": "KanalD.tr",
        "aliases": ["kanal d", "kanald"]
    },
    "show tv": {
        "name": "Show TV",
        "group": "🇹🇷 Türkiyə - Əsas",
        "tvg_id": "ShowTV.tr",
        "aliases": ["show tv", "showtv"]
    },
    "star tv": {
        "name": "Star TV",
        "group": "🇹🇷 Türkiyə - Əsas",
        "tvg_id": "StarTV.tr",
        "aliases": ["star tv", "startv"]
    },
    "atv tr": {
        "name": "ATV",
        "group": "🇹🇷 Türkiyə - Əsas",
        "tvg_id": "ATV.tr",
        "aliases": ["atv", "atv türkiye", "atv turkiye"]
    },
    "tv8": {
        "name": "TV8",
        "group": "🇹🇷 Türkiyə - Əsas",
        "tvg_id": "TV8.tr",
        "aliases": ["tv8"]
    },
    "tv8.5": {
        "name": "TV8.5",
        "group": "⚽ İdman",
        "tvg_id": "TV85.tr",
        "aliases": ["tv8.5", "tv85", "tv 8.5"]
    },
    "now tv": {
        "name": "NOW TV",
        "group": "🇹🇷 Türkiyə - Əsas",
        "tvg_id": "NowTV.tr",
        "aliases": ["now tv", "nowtv", "fox tv", "fox"]
    },
    "kanal 7": {
        "name": "Kanal 7",
        "group": "🇹🇷 Türkiyə - Əsas",
        "tvg_id": "Kanal7.tr",
        "aliases": ["kanal 7", "kanal7"]
    },
    "beyaz tv": {
        "name": "Beyaz TV",
        "group": "🇹🇷 Türkiyə - Əsas",
        "tvg_id": "BeyazTV.tr",
        "aliases": ["beyaz tv", "beyaztv"]
    },
    "teve2": {
        "name": "Teve2",
        "group": "🇹🇷 Türkiyə - Əsas",
        "tvg_id": "Teve2.tr",
        "aliases": ["teve2", "teve 2"]
    },
    "trt haber": {
        "name": "TRT Haber",
        "group": "📰 Xəbər",
        "tvg_id": "TRTHaber.tr",
        "aliases": ["trt haber", "trthaber"]
    },
    "trt spor": {
        "name": "TRT Spor",
        "group": "⚽ İdman",
        "tvg_id": "TRTSpor.tr",
        "aliases": ["trt spor", "trtspor"]
    },
    "a haber": {
        "name": "A Haber",
        "group": "📰 Xəbər",
        "tvg_id": "AHaber.tr",
        "aliases": ["a haber", "ahaber"]
    },
    "cnnturk": {
        "name": "CNN Türk",
        "group": "📰 Xəbər",
        "tvg_id": "CNNTurk.tr",
        "aliases": ["cnn türk", "cnn turk", "cnntürk"]
    },
    "haberturk": {
        "name": "Habertürk",
        "group": "📰 Xəbər",
        "tvg_id": "Haberturk.tr",
        "aliases": ["habertürk", "haberturk"]
    }
}

def load_and_update_sources():
    """sources.txt faylından mənbələri oxuyur, skraypinq edib yeni tapdıqlarını da həmin fayla əlavə edir"""
    sources = []
    
    # 1. Mövcud sources.txt faylını oxuyuruq
    if os.path.exists("sources.txt"):
        with open("sources.txt", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and line not in sources:
                    sources.append(line)
                    
    # Əgər fayl hələ boşdursa, baza linkləri əlavə edirik
    if not sources:
        sources = [
            "https://qazim.github.io/IPTV/all_channels.m3u",
            "https://raw.githubusercontent.com/Free-TV/IPTV/refs/heads/master/playlists/playlist_azerbaijan.m3u8",
            "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/az.m3u",
            "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/tr.m3u"
        ]

    # 2. Açıq kataloqlardan yeni mənbələr skraypinq edirik
    print("Açıq kataloqlardan yeni mənbələr axtarılır...")
    directories = [
        "https://raw.githubusercontent.com/iptv-org/iptv/master/index.m3u",
        "https://raw.githubusercontent.com/Free-TV/IPTV/master/playlist.m3u"
    ]
    
    new_found = False
    for dir_url in directories:
        try:
            req = urllib.request.Request(dir_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                content = response.read().decode('utf-8', errors='ignore')
                found_links = re.findall(r'https?://[^\s]+\.(?:m3u|m3u8)', content, re.IGNORECASE)
                for link in found_links:
                    if any(k in link.lower() for k in ["az", "turkey", "tr", "azerbaijan"]):
                        if link not in sources:
                            sources.append(link)
                            print(f"Yeni mənbə tapıldı və əlavə olundu: {link}")
                            new_found = True
        except Exception:
            pass

    # 3. Əgər yeni mənbə tapılıbsa, onu sources.txt faylına yazırıq ki, yadda qalsın
    if new_found:
        with open("sources.txt", "w", encoding="utf-8") as f:
            f.write("# Avtomatik yenilənən və əlavə edilən IPTV mənbələri\n")
            for s in sources:
                f.write(f"{s}\n")
                
    return sources

def match_master_channel(channel_name):
    n = channel_name.lower()
    if "bein sports" in n or "s sport" in n or "exxen" in n:
        return "BLOCKED", None

    for key, data in MASTER_CHANNELS.items():
        for alias in data["aliases"]:
            if alias in n:
                return key, data
    return None, None

def is_stream_smart_checked(url):
    try:
        req = urllib.request.Request(
            url, 
            headers={
                'User-Agent': 'VLC/3.0.18 LibVLC/3.0.18',
                'Accept': '*/*'
            }
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            status = response.getcode()
            if status in [200, 301, 302]:
                content = response.read(512).decode('utf-8', errors='ignore').lower()
                if "<html" in content and "not found" in content:
                    return False
                return True
    except urllib.error.HTTPError as e:
        if e.code in [404, 410]:
            return False
    except Exception:
        pass

    if any(ext in url.lower() for ext in [".m3u8", ".ts", "/live/", "/hls/", "m3u"]):
        return True
        
    return False

def process_channel(entry):
    extinf, stream_url = entry
    channel_name = extinf.split(',')[-1].strip()
    
    master_key, channel_info = match_master_channel(channel_name)
    if master_key == "BLOCKED":
        return None
        
    if not is_stream_smart_checked(stream_url):
        return None

    if master_key and channel_info:
        return (master_key, channel_info["group"], channel_info["name"], channel_info["tvg_id"], stream_url)
    
    group_match = re.search(r'group-title="([^"]+)"', extinf)
    group_title = group_match.group(1) if group_match else "🌐 Digər Kanallar"
    
    return (channel_name.lower(), group_title, channel_name, "", stream_url)

def main():
    sources = load_and_update_sources()
    print(f"Ümumi aktiv mənbə sayı: {len(sources)}")

    all_entries = []
    for source_url in sources:
        try:
            print(f"Mənbə oxunur: {source_url}")
            req = urllib.request.Request(source_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=12) as response:
                content = response.read().decode('utf-8', errors='ignore')

            entries = re.findall(r'(#EXTINF:[^\n]+\n)(https?://[^\s]+)', content)
            all_entries.extend(entries)
        except Exception as e:
            print(f"Mənbə oxunmadı ({source_url}): {e}")

    print(f"Ümumi tapıldı: {len(all_entries)} xam kanal. İşlənmə başlanır...")

    final_playlist = ["#EXTM3U\n"]
    added_keys = set()

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(process_channel, entry) for entry in all_entries]
        
        for future in as_completed(futures):
            result = future.result()
            if result:
                unique_key, group, name, tvg_id, stream_url = result
                if unique_key not in added_keys:
                    if tvg_id:
                        extinf_line = f'#EXTINF:-1 tvg-id="{tvg_id}" group-title="{group}",{name}\n'
                    else:
                        extinf_line = f'#EXTINF:-1 group-title="{group}",{name}\n'
                        
                    final_playlist.append(f"{extinf_line}{stream_url}\n")
                    added_keys.add(unique_key)

    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.writelines(final_playlist)
    
    print(f"Yenilənmə tamamlandı! Cəmi {len(added_keys)} kanal playlistə yazıldı.")

if __name__ == "__main__":
    main()
