#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Run it with: python compare_music.py "E:\Musica\playlist.xspf"
# If running on Linux, use: python3 compare_music.py "/mnt/e/Musica/playlist.xspf"
# If running on git bash in vscode python compare_playlists_rock.py "E:\\Musica\\Rock50-00_5.0.xspf"
# If running on powershell python .\compare_playlists_rock.py "E:\Musica\Rock50-00_5.0.xspf" > test.txt 2>&1
# If using WSL in windows and the version runs an old version of Python do this first: 
#       sudo apt install python3 -y
#       sudo update-alternatives --install /usr/bin/python python /usr/bin/python3 2
#       sudo update-alternatives --config python

"""
compare_playlists_rock_legacy.py
Run with:
    python compare_playlists_rock_legacy.py "E:\\Musica\\Rock50-00_5.0.xspf"
    or
    python compare_playlists_rock_legacy.py /mnt/e/Musica/Rock50-00_5.0.xspf
Works on Python 2.7 → 3.x
"""

from __future__ import print_function, unicode_literals
import os
import sys
import xml.etree.ElementTree as ET
import re
import time

# ▲ NEW — full URL-decoder & Unicode normaliser (replaces the old "%20" hack)
try:
    from urllib.parse import unquote          # Py3
except ImportError:
    from urllib import unquote                # Py2

import unicodedata

def url_to_path(url):
    """
    Convert a file:// URL to a normal absolute path.
        * strips scheme (file:// or file:///)
        * decodes ALL %xx escapes (%28 → (), %27 → ', …)
        * NFC-normalises Unicode so Windows/macOS names match
    """
    if url.lower().startswith('file://'):
        url = url[7:]
        if url.startswith('/'):
            url = url.lstrip('/')
    path = unquote(url)
    path = unicodedata.normalize('NFC', path)
    return os.path.abspath(os.path.normpath(path))

# ▲ NEW — safe_print avoids UnicodeEncodeError on CP-1252 consoles
def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        enc = getattr(sys.stdout, "encoding", None) or "utf-8"
        safe = text.encode(enc, "replace").decode(enc, "replace")
        print(safe)

# ---------------------------------------------------------------------------

def get_files_in_folder(folder_path, exclude_extensions=None, exclude_folders=None):
    """
    Recursively list all files under *folder_path*, skipping:
        • ext in exclude_extensions
        • dir name in exclude_folders (case-insensitive)
    Returns a set of absolute paths.
    """
    if exclude_extensions is None:
        exclude_extensions = []
    if exclude_folders is None:
        exclude_folders = []

    ex_ext = [e.lower() for e in exclude_extensions]
    ex_dir = [d.lower() for d in exclude_folders]

    all_files = set()
    for root, dirs, files in os.walk(folder_path):
        dirs[:] = [d for d in dirs if d.lower() not in ex_dir]
        for name in files:
            _, ext = os.path.splitext(name)
            if ext.lower() in ex_ext:
                continue
            all_files.add(os.path.abspath(os.path.join(root, name)))
    return all_files

def get_files_from_xspf(xspf_path):
    """
    Parse an .xspf playlist and return a set of absolute file paths.
    """
    playlist_files = set()
    try:
        ET.register_namespace('', 'http://xspf.org/ns/0/')
        tree = ET.parse(xspf_path)
        ns = {'xspf': 'http://xspf.org/ns/0/'}

        # ▲ CHANGED — use url_to_path() instead of old %20 replacement
        for loc in tree.findall('.//xspf:location', ns):
            if loc.text:
                playlist_files.add(url_to_path(loc.text))

    except (IOError, OSError):
        safe_print("Error: XSPF file not found at {0}".format(xspf_path))
    except ET.ParseError as e:
        safe_print("Error parsing XSPF file: {0}".format(e))
    return playlist_files

# ---------------------------------------------------------------------------

if len(sys.argv) < 2:
    safe_print("Usage: python compare_playlists_rock_legacy.py <playlist_file.xspf>")
    sys.exit(1)

xspf_file    = sys.argv[1]
music_folder = os.path.dirname(os.path.abspath(xspf_file))

exclude_extensions = [
    '.xspf',      
    '.jpg', '.jpeg',
    '.png',
    '.txt',
    '.log',
    '.cue',
    '.accurip',
    '.m3u', '.m3u8'
]
exclude_folders = [
    'Clasica', 'Discogs', 'Electronica', 'Española', 'Films',
    'Game', 'HeartLand Rock', 'Jazz', 'Medieval', 'Relax', 'Soul', 'v', 'Varios'
]

safe_print("Comparing music in: {0}".format(music_folder))
safe_print("Using playlist file: {0}".format(xspf_file))
safe_print("Excluding folders: {0}".format(', '.join(exclude_folders)))

folder_files   = get_files_in_folder(music_folder,
                                     exclude_extensions=exclude_extensions,
                                     exclude_folders=exclude_folders)
playlist_files = get_files_from_xspf(xspf_file)

missing = folder_files - playlist_files

# Missing files sorted by relative path
""" if missing:
    safe_print("\nFiles in the folder (after exclusions) but *not* in the playlist:")
    for p in sorted(missing):
        try:
            rel = os.path.relpath(p, music_folder)
            safe_print("- {0}".format(rel))
        except ValueError:      # relpath may fail across drives
            safe_print("- {0}".format(p))
else:
    safe_print("\nAll relevant files are already in the playlist.") """

# Missing files sorted by modification time
if missing:
    safe_print("\nMissing files, newest → oldest:")
    # sort by modification time (newest first)
    missing_sorted = sorted(missing, key=os.path.getmtime, reverse=True)

    for p in missing_sorted:
        try:
            rel = os.path.relpath(p, music_folder)
        except ValueError:
            rel = p

        mtime = os.path.getmtime(p)                    # seconds since epoch
        timestamp = time.strftime("%Y-%m-%d %H:%M",    # human-readable
                                  time.localtime(mtime))
        safe_print(u"- {0}   ({1})".format(rel, timestamp))
else:
    safe_print("\nAll relevant files are already in the playlist.")