# compare-playlists

**Purpose**  
Scan `E:\Musica` (or `/mnt/e/Musica` in WSL) and list every file **that is _not_ already referenced** in a given `.xspf` playlist.  
Output is sorted by newest-to-oldest modification date.

## Notes

* **Ignored file-extensions**  
  `.xspf`, `.jpg`, `.jpeg`, `.png`, `.txt`, `.log`, `.cue`, `.accurip`, `.m3u`, `.m3u8`
* **Ignored folder names** (case-insensitive)  
  `Clasica`, `Discogs`, `Electronica`, `Española`, `Films`, `Game`, `Jazz`,  
  `Medieval`, `Relax`, `Sould`, `v`, `Varios`
* Works on Python 2.7 → 3.x.  
* Windows ↔ WSL outputs match **only if both terminals run in UTF-8**.

---

## Run on Windows / PowerShell

```powershell
# 0) Open a *new* PowerShell window (your profile should set UTF-8)
# 1) Go to the folder that holds the script
cd C:\Users\Loco_\ReactProjects\compare_playlists_python

# 2) Run the script and send the list to UTF-8 text
python -X utf8 .\compare_playlists_rock.py "E:\Musica\Rock50-00_5.0.xspf" | Out-File -Encoding utf8 missing_windows.txt
# Generate the Windows file without BOM and with Unix line-ends
python -X utf8 .\compare_playlists_rock.py "E:\Musica\Rock50-00_5.0.xspf" > missing_windows.txt
```

## Run on WSL / Linux

```bash
# 0) Open a *new* WSL terminal (locale should be UTF-8, e.g. es_ES.UTF-8)
# 1) Go to the same project folder (under /mnt)
cd /mnt/c/Users/Loco_/ReactProjects/compare_playlists_python

# 2) Run with Python 3 and save the list
python3 compare_playlists_rock.py "/mnt/e/Musica/Rock50-00_5.0.xspf" > missing_linux.txt
```

### Compare the two outputs

```bash
# run this in WSL from the project folder
diff -u missing_linux.txt missing_windows.txt
```