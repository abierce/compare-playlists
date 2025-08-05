import os
import xml.etree.ElementTree as ET
import re
import sys

# Run it with: python compare_music.py "E:\Musica\playlist.xspf"

def get_files_in_folder(folder_path, exclude_extensions=None):
    """
    Recursively lists all files in a folder, optionally excluding certain extensions.
    Returns a set of absolute file paths.
    """
    if exclude_extensions is None:
        exclude_extensions = []
    
    all_files = set()
    for root, _, files in os.walk(folder_path):
        for file in files:
            _, file_extension = os.path.splitext(file)
            
            if file_extension.lower() not in [ext.lower() for ext in exclude_extensions]:
                full_path = os.path.join(root, file)
                all_files.add(os.path.abspath(full_path))
    return all_files

def get_files_from_xspf(xspf_path):
    """
    Parses an XSPF file and returns a set of file paths.
    """
    playlist_files = set()
    try:
        ET.register_namespace('', 'http://xspf.org/ns/0/')
        tree = ET.parse(xspf_path)
        root = tree.getroot()
        ns = {'xspf': 'http://xspf.org/ns/0/'}
        for location_elem in root.findall('.//xspf:location', ns):
            location_path = location_elem.text
            if location_path:
                clean_path = re.sub(r'^file://', '', location_path)
                clean_path = re.sub(r'^file:///', '', clean_path)
                clean_path = re.sub(r'%20', ' ', clean_path)
                normalized_path = os.path.normpath(clean_path)
                playlist_files.add(os.path.abspath(normalized_path))
    except FileNotFoundError:
        print(f"Error: XSPF file not found at {xspf_path}")
    except ET.ParseError as e:
        print(f"Error parsing XSPF file: {e}")
    return playlist_files

# --- Script Execution ---
if len(sys.argv) < 2:
    print("Usage: python your_script_name.py <playlist_file.xspf>")
    sys.exit(1)

# The first argument (sys.argv[1]) is the path to the playlist file
xspf_file = sys.argv[1]

# The music folder is derived from the playlist file's directory
music_folder = os.path.dirname(os.path.abspath(xspf_file))
excluded_extensions = ['.xspf']

print(f"Comparing music in: {music_folder}")
print(f"Using playlist file: {xspf_file}")

# Get all files from the music folder, excluding .xspf files
folder_files = get_files_in_folder(music_folder, exclude_extensions=excluded_extensions)
# Get all files from the playlist
playlist_files = get_files_from_xspf(xspf_file)

# Find the difference
not_in_playlist = folder_files - playlist_files

if not_in_playlist:
    print("\nThe following files are in the music folder but not in the playlist:")
    for file_path in sorted(list(not_in_playlist)):
        try:
            relative_path = os.path.relpath(file_path, music_folder)
            print(f"- {relative_path}")
        except ValueError:
            print(f"- {file_path}")
else:
    print("\nAll relevant files in the music folder are included in the playlist.")