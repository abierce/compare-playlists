#!/bin/bash

# NOTE: Remembert o make it executable with `chmod +x compare.sh`
# Run it with ./compare_music.sh "/mnt/e/Musica/playlist.xspf" 

# --- Check for arguments ---
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <playlist_file.xspf>"
    exit 1
fi

# The first argument ($1) is the path to the playlist file
XSPF_FILE="$1"

# Extract the directory of the playlist file
MUSIC_FOLDER=$(dirname "$XSPF_FILE")

# List of folders to exclude
EXCLUDE_FOLDERS="Clasica|Discogs|Electronica|Española|Films|Game|Jazz|Medieval|Relax|Sould|v|Varios"

# Construct the find command's exclusion part
EXCLUSION_PATTERN=""
for folder in ${EXCLUDE_FOLDERS//|/ }; do
    # Use -path and -prune to prevent descending into the folders
    EXCLUSION_PATTERN+=" -path \"$MUSIC_FOLDER/$folder\" -prune -o"
done

echo "Comparing music in: $MUSIC_FOLDER"
echo "Using playlist file: $XSPF_FILE"
echo "Excluding folders: ${EXCLUDE_FOLDERS//|/, }"

# 1. List all files in the music folder and subfolders, excluding .xspf files and specific folders
#    We use `eval` to run the dynamically constructed `find` command.
#    `! -name "*.xspf"` excludes xspf files.
#    The `!` at the beginning of the `find` expression is crucial here.
eval find \""$MUSIC_FOLDER"\" $EXCLUSION_PATTERN -type f ! -name "*.xspf" -print0 | sort -z > /tmp/folder_files.txt

# 2. Extract file paths from the XSPF file
grep -oP '<location>\K[^<]+' "$XSPF_FILE" \
| sed 's|file:///||g; s|%20| |g' \
| sort > /tmp/xspf_files.txt

# 3. Compare the two lists and show files only in the folder list
comm -23 /tmp/folder_files.txt /tmp/xspf_files.txt

# Clean up temporary files
rm /tmp/folder_files.txt /tmp/xspf_files.txt