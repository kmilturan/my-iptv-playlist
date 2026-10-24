import urllib.request
import urllib.error
import json
import re
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

BASE_SOURCES = [
    "https://qazim.github.io/IPTV/all_channels.m3u",
    "https://raw.githubusercontent.com/Free-TV/IPTV/refs/heads/master/playlists/playlist_azerbaijan.m3u8",
    "https://raw.githubusercontent.com/Hero355/iptv/refs/heads/master/Azerbaijan",
    "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/az.m3u",
    "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/tr.m3u"
]

def discover_dynamic_sources():
    dynamic_sources = []
    queries = ["azerbaijan extension:m3u", "turkey extension:m3u iptv"]
    
    for q in queries:
        try:
            api_url = f"https://api.github.com/search/code?q={urllib.parse.quote(q)}"
            req = urllib.request.Request(
                api_url, 
                headers={
                    'User-Agent': 'Mozilla/5.0',
                    'Accept': 'application/vnd.github.v3+json'
                }
            )
            with urllib.request.urlopen(req, timeout=8) as response:
                data = json.loads(response.read().decode('utf-8'))
                for item in data.get("items", [])[:3]:
                    html_url = item.get("html_url", "")
                    raw_url = html_url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
                    if raw_url not in dynamic_sources:
                        dynamic_sources.append(raw_url)
        except Exception:
            pass
    return dynamic_sources

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
    
    # Bloklanmış ödənişli kanalları atırıq
    master_key, channel_info = match_master_channel(channel_name)
    if master_key == "BLOCKED":
        return None
        
    # Sağlamlıq yoxlaması
    if not is_stream_smart_checked(stream_url):
        return None

    # Əgər master lüğətdə varsa, təmiz formatda qaytarırıq
    if master_key and channel_info:
        return (master_key, channel_info["group"], channel_info["name"], channel_info["tvg_id"], stream_url)
    
    # Əgər master lüğətdə yoxdursa, amma işləkdirsə, orijinal ad və qrupu ilə saxlayırıq!
    group_match = re.search(r'group-title="([^"]+)"', extinf)
    group_title = group_match.group(1) if group_match else "🌐 Digər Kanallar"
    
    # Unikal açar kimi kanal adını istifadə edirik
    return (channel_name.lower(), group_title, channel_name, "", stream_url)

def main():
    sources = BASE_SOURCES.copy()
    print("Dinamik mənbələr əlavə edilir...")
    for d_url in discover_dynamic_sources():
        if d_url not in sources:
            sources.append(d_url)

    all_entries = []
    for source_url in sources:
        try:
            req = urllib.request.Request(source_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=12) as response:
                content = response.read().decode('utf-8', errors='ignore')

            entries = re.findall(r'(#EXTINF:[^\n]+\n)(https?://[^\s]+)', content)
            all_entries.extend(entries)
        except Exception:
            pass

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
