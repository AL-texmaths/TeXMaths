#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
detect_proxy_windows.py

Détecte la présence d'un proxy sur Windows en combinant :
- variables d'environnement (HTTP_PROXY, HTTPS_PROXY, ...)
- paramètres WinINet (registre : ProxyEnable, ProxyServer, AutoConfigURL)
- paramètres WinHTTP (commande `netsh winhttp show proxy`)

Usage:
  python -m src.detect_proxy_windows
  ou
  python src\\detect_proxy_windows.py

Renvoie un JSON sur stdout contenant les sections `env`, `wininet`, `winhttp` et
une clé `detected` indiquant si un proxy a été détecté.
"""

import os
import platform
import subprocess
import json
import re
import unicodedata
import urllib.request
import urllib.parse
from urllib.error import URLError, HTTPError
from typing import Any, Dict, List, Optional, Union, Tuple


def _try_decode_bytes(raw_bytes: bytes, encodings: Optional[List[str]] = None) -> Tuple[str, str]:
    if encodings is None:
        encodings = ["utf-8", "cp1252", "cp850", "latin-1"]
    for enc in encodings:
        try:
            return raw_bytes.decode(enc), enc
        except Exception:
            try:
                return raw_bytes.decode(enc, errors="replace"), enc
            except Exception:
                continue
    return raw_bytes.decode("utf-8", errors="replace"), "utf-8"


def _normalize_string(s: str) -> str:
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join(c for c in nfkd if unicodedata.category(c) != "Mn").lower()


def _unique_proxies(entries: List[Dict[str, Optional[Union[str, int]]]]) -> List[Dict[str, Optional[Union[str, int]]]]:
    seen = set()
    unique: List[Dict[str, Optional[Union[str, int]]]] = []
    for e in entries:
        key = f"{e.get('scheme') or ''}|{e.get('host') or ''}|{e.get('port') or ''}"
        if key not in seen:
            seen.add(key)
            unique.append(e)
    return unique


def parse_proxy_string_with_scheme(token: str, scheme_override: Optional[str]) -> List[Dict[str, Optional[Union[str, int]]]]:
    token = token.strip().strip('"\'')
    try:
        if '://' in token:
            parsed = urllib.parse.urlparse(token)
        else:
            parsed = urllib.parse.urlparse('http://' + token)
        host = parsed.hostname
        port = parsed.port
        scheme = scheme_override or (parsed.scheme if parsed.scheme else None)
        return [{'scheme': scheme, 'host': host, 'port': port, 'raw': token}]
    except Exception:
        return [{'scheme': scheme_override, 'host': token, 'port': None, 'raw': token}]


def parse_proxy_string(s: str) -> List[Dict[str, Optional[Union[str, int]]]]:
    entries: List[Dict[str, Optional[Union[str, int]]]] = []
    if not s:
        return entries
    s = s.strip()
    s = s.strip('"\'')
    # scheme-specific list like "http=proxy:80;https=proxy2:443"
    if ';' in s and '=' in s:
        for part in s.split(';'):
            part = part.strip()
            if not part:
                continue
            if '=' in part:
                scheme, hostpart = part.split('=', 1)
                entries.extend(parse_proxy_string_with_scheme(hostpart.strip(), scheme.strip()))
            else:
                entries.extend(parse_proxy_string(part))
        return _unique_proxies(entries)

    # split by common separators
    parts = re.split(r'[,\s]+', s)
    for part in parts:
        if not part:
            continue
        if '=' in part:
            scheme, hostpart = part.split('=', 1)
            entries.extend(parse_proxy_string_with_scheme(hostpart.strip(), scheme.strip()))
            continue
        entries.extend(parse_proxy_string_with_scheme(part.strip(), None))

    return _unique_proxies(entries)


def parse_pac(content: str) -> List[Dict[str, Optional[Union[str, int]]]]:
    entries: List[Dict[str, Optional[Union[str, int]]]] = []
    if not content:
        return entries
    # chaînes entre guillemets qui contiennent PROXY/SOCKS
    for s in re.findall(r'["\']([^"\']*?)["\']', content, flags=re.I):
        if 'PROXY' in s.upper() or 'SOCKS' in s.upper():
            for m in re.findall(r"(?:PROXY|SOCKS|SOCKS5)\s+([^\s;]+)", s, flags=re.I):
                entries.extend(parse_proxy_string(m))
    # fallback: chercher n'importe où PROXY token
        for m in re.findall(r'(?:PROXY|SOCKS|SOCKS5)\s+([^\s;\'"]+)', content, flags=re.I):
            entries.extend(parse_proxy_string(m))
    return _unique_proxies(entries)


def fetch_autoconfig(url: str, timeout: int = 5) -> Dict[str, Any]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "texmaths-probe/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            decoded, encoding = _try_decode_bytes(raw)
            proxies = parse_pac(decoded)
            return {"url": url, "content": decoded, "encoding": encoding, "proxies": proxies}
    except Exception as e:
        return {"url": url, "error": str(e)}


def check_env_proxies() -> Dict[str, Any]:
    keys = [
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "http_proxy",
        "https_proxy",
        "ALL_PROXY",
        "all_proxy",
        "NO_PROXY",
        "no_proxy",
    ]
    found: Dict[str, str] = {}
    parsed: Dict[str, List[Dict[str, Optional[Union[str, int]]]]] = {}
    for k in keys:
        v = os.environ.get(k)
        if v:
            found[k] = v
            parsed[k] = parse_proxy_string(v)
    return {"raw": found, "parsed": parsed}


def get_wininet_settings() -> Dict[str, Any]:
    if platform.system() != "Windows":
        return {"error": "Not Windows"}
    try:
        import winreg  # type: ignore
    except Exception as e:
        return {"error": f"winreg import failed: {e}"}

    path = r"Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings"
    res: Dict[str, Any] = {}
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, path)
    except Exception:
        return {"error": "Registry key not accessible"}

    def q(name: str):
        try:
            v, _ = winreg.QueryValueEx(key, name)
            return v
        except Exception:
            return None

    try:
        proxy_enable = q("ProxyEnable")
        if proxy_enable is not None:
            # ProxyEnable stored as DWORD (0/1)
            try:
                res["ProxyEnable"] = bool(int(proxy_enable))
            except Exception:
                res["ProxyEnable"] = proxy_enable

        proxy_server = q("ProxyServer")
        if proxy_server:
            res["ProxyServer"] = proxy_server

        auto_config = q("AutoConfigURL")
        if auto_config:
            res["AutoConfigURL"] = auto_config

        proxy_override = q("ProxyOverride")
        if proxy_override:
            res["ProxyOverride"] = proxy_override
    finally:
        try:
            winreg.CloseKey(key)
        except Exception:
            pass

    # Ajouter parsing de ProxyServer s'il existe
    try:
        proxy_server = res.get("ProxyServer")
        if proxy_server:
            res["ProxyServerParsed"] = parse_proxy_string(proxy_server)
    except Exception:
        pass

    # Récupérer et parser AutoConfigURL (WPAD/PAC) si présent
    try:
        ac = res.get("AutoConfigURL")
        if ac:
            fetched = fetch_autoconfig(ac)
            # inclure contenu ou erreur
            if "content" in fetched:
                res["AutoConfigURLContent"] = fetched.get("content")
                res["AutoConfigURLEncoding"] = fetched.get("encoding")
                res["AutoConfigURLProxies"] = fetched.get("proxies")
            else:
                res["AutoConfigURLError"] = fetched.get("error")
    except Exception:
        pass

    return res


def get_winhttp_settings() -> Dict[str, Any]:
    if platform.system() != "Windows":
        return {"error": "Not Windows"}
    try:
        proc = subprocess.run(
            ["netsh", "winhttp", "show", "proxy"],
            capture_output=True,
            text=False,
            timeout=5,
        )
    except FileNotFoundError:
        return {"error": "netsh not found"}
    except Exception as e:
        return {"error": str(e)}

    raw_bytes = proc.stdout or proc.stderr or b""

    out, used_encoding = _try_decode_bytes(raw_bytes)
    out = (out or "").strip()

    norm = _normalize_string(out)

    # motifs indiquant "pas de proxy"
    no_proxy_keywords = [
        "direct access",
        "no proxy",
        "aucun",
        "acces direct",
        "sans serveur proxy",
        "sans proxy",
    ]

    # motifs indiquant la présence d'un proxy
    proxy_keywords = [
        r"proxy server(s)",
        r"proxy server",
        r"proxy:",
        r"serveur proxy",
        r"http=",
        r"https=",
    ]

    has_no_proxy = any(k in norm for k in no_proxy_keywords)
    has_proxy_kw = any(re.search(k, norm, re.I) for k in proxy_keywords)

    # Priorité : si on voit un indicateur d'accès direct, on considère pas de proxy.
    if has_no_proxy:
        has_proxy = False
    else:
        has_proxy = bool(has_proxy_kw)

    # Extraire les adresses trouvées dans la sortie
    parsed_proxies: List[Dict[str, Optional[Union[str, int]]]] = []
    try:
        # parcourir les lignes et parse celles contenant "proxy"
        for line in out.splitlines():
            if 'proxy' in line.lower():
                # récupérer après le ':' s'il y en a
                if ':' in line:
                    part = line.split(':', 1)[1]
                else:
                    part = line
                parsed_proxies.extend(parse_proxy_string(part))

        # fallback: trouver des tokens host:port
        if not parsed_proxies:
            hostport_tokens = re.findall(r"\[[^\]]+\]:\d+|[A-Za-z0-9\.-]+:\d+", out)
            for token in hostport_tokens:
                parsed_proxies.extend(parse_proxy_string(token))
    except Exception:
        parsed_proxies = []

    parsed_proxies = _unique_proxies(parsed_proxies)

    return {"raw": out, "encoding": used_encoding, "has_proxy": has_proxy, "parsed": parsed_proxies}


def detect_proxy_windows() -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    result["env"] = check_env_proxies()
    result["wininet"] = get_wininet_settings()
    result["winhttp"] = get_winhttp_settings()

    detected = False
    # Variables d'environnement
    # `env` now contient {'raw': {...}, 'parsed': {...}}
    if result.get("env") and result["env"].get("raw"):
        detected = True
    # WinINet : ProxyEnable + ProxyServer/AutoConfigURL
    try:
        wi = result.get("wininet", {}) or {}
        if isinstance(wi, dict):
            if wi.get("ProxyEnable"):
                if wi.get("ProxyServer") or wi.get("AutoConfigURL"):
                    detected = True
            elif wi.get("AutoConfigURL"):
                detected = True
    except Exception:
        pass

    # WinHTTP
    try:
        wh = result.get("winhttp", {}) or {}
        if isinstance(wh, dict) and wh.get("has_proxy"):
            detected = True
    except Exception:
        pass

    result["detected"] = detected
    return result


def main() -> None:
    res = detect_proxy_windows()
    print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
