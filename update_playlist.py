import urllib.request
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

# Master Mapping: Genişləndirilmiş Azərbaycan və Türkiyə Kanalları Lüğəti
MASTER_CHANNELS = {
    # --- AZƏRBAYCAN KANALLARI ---
    "baku tv": {
        "name": "Baku TV",
        "group": "🇦🇿 Azərbaycan",
        "tvg_id": "BakuTV.az",
        "aliases": ["baku tv", "bakutv", "baku-tv"]
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

    # --- TÜRKİYƏ - ƏSAS KANALLAR ---
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

    # --- XƏBƏR VƏ İDMAN ---
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

# Əsas təməl mənbələr
BASE_SOURCES = [
    "https://raw.githubusercontent.com/Free-TV/IPTV/refs/heads/master/playlists/playlist_azerbaijan.m3u8",
    "https://raw.githubusercontent.com/Hero355/iptv/refs/heads/master/Azerbaijan",
    "https://qazim.github.io/IPTV/all_channels.m3u",
    "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/az.m3u",
    "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/tr.m3u"
]
import urllib.request
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

# Master Mapping: Genişləndirilmiş Azərbaycan və Türkiyə Kanalları Lüğəti
MASTER_CHANNELS = {
    # --- AZƏRBAYCAN KANALLARI ---
    "baku tv": {
        "name": "Baku TV",
        "group": "🇦🇿 Azərbaycan",
        "tvg_id": "BakuTV.az",
        "aliases": ["baku tv", "bakutv", "baku-tv"]
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

    # --- TÜRKİYƏ - ƏSAS KANALLAR ---
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

    # --- XƏBƏR VƏ İDMAN ---
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
    "https://raw.githubusercontent.com/Free-TV/IPTV/refs/heads/master/playlists/playlist_azerbaijan.m3u8",
    "https://raw.githubusercontent.com/Hero355/iptv/refs/heads/master/Azerbaijan",
    "https://qazim.github.io/IPTV/all_channels.m3u",
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
            with urllib.request.urlopen(req, timeout=10) as response:
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
        return None, None

    for key, data in MASTER_CHANNELS.items():
        for alias in data["aliases"]:
            if alias in n:
                return key, data
    return None, None

def is_stream_healthy(url):
    """
    Qüsursuzlaşdırılmış Sağlamlıq Yoxlaması:
    1. IPTV Pleyer User-Agent (VLC) istifadə edir (bloklanmanın qarşısını alır).
    2. HTML xəta səhifələrini ("Access Denied", "404" və s.) filtrləyir.
    3. HLS manifest daxilindəki rəsmi teqləri yoxlayır.
    """
    try:
        req = urllib.request.Request(
            url, 
            headers={
                'User-Agent': 'VLC/3.0.18 LibVLC/3.0.18',
                'Accept': '*/*'
            }
        )
        # Timeout müddətini 5 saniyə təyin edirik
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status != 200:
                return False
            
            content = response.read().decode('utf-8', errors='ignore').strip()
            
            # Əgər server cavab olaraq HTML xəta səhifəsi qaytarıbsa
            content_lower = content.lower()
            if "<html" in content_lower or "access denied" in content_lower or "forbidden" in content_lower:
                return False

            # Əgər .m3u8 manifestidirsə, içində HLS teqləri olmalıdır
            if ".m3u" in url or "m3u8" in url:
                if any(tag in content for tag in ["#EXTINF", "#EXT-X-STREAM-INF", "#EXT-X-TARGETDURATION"]):
                    return True
                return False
                
            # Digər birbaşa axın linkləri üçün cavabın boş olmadığını yoxlayırıq
            if len(content) > 0:
                return True
                
    except Exception:
        pass
    return False

def process_channel(entry):
    extinf, stream_url = entry
    channel_name = extinf.split(',')[-1].strip()
    
    master_key, channel_info = match_master_channel(channel_name)
    if master_key and channel_info:
        if is_stream_healthy(stream_url):
            return master_key, channel_info, stream_url
    return None

def main():
    sources = BASE_SOURCES.copy()
    print("Dinamik mənbələr axtarılır...")
    sources.extend(discover_dynamic_sources())

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

    print(f"Ümumi tapıldı: {len(all_entries)} xam kanal. Dəqiq sağlamlıq yoxlaması aparılır...")

    final_playlist = ["#EXTM3U\n"]
    added_keys = set()

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(process_channel, entry) for entry in all_entries]
        
        for future in as_completed(futures):
            result = future.result()
            if result:
                master_key, info, stream_url = result
                if master_key not in added_keys:
                    extinf_line = f'#EXTINF:-1 tvg-id="{info["tvg_id"]}" group-title="{info["group"]}",{info["name"]}\n'
                    final_playlist.append(f"{extinf_line}{stream_url}\n")
                    added_keys.add(master_key)
                    print(f"İşlək təsdiqləndi [{info['group']}]: {info['name']}")

    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.writelines(final_playlist)
    
    print(f"Yenilənmə tamamlandı! Cəmi {len(added_keys)} yoxlanılmış işlək kanal yazıldı.")

if __name__ == "__main__":
    main()
