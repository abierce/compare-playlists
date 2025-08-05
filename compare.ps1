# NOTE: run it with `pwsh compare.ps1` or .\compare.ps1

# --- Configuration with Variables ---
$musicFolder = "E:\Musica"
$xspfFile = "E:\Musica\playlist.xspf"

# 1. Get all file paths in the folder and its subfolders, excluding .xspf files
#    -Recurse: search in subfolders
#    -File: only get files
#    -Exclude: exclude files matching the pattern
$folderFiles = Get-ChildItem -Path $musicFolder -Recurse -File -Exclude "*.xspf" | ForEach-Object { $_.FullName }

# 2. Parse the XSPF file to get the list of playlist files
[xml]$xspfContent = Get-Content -Path $xspfFile

$playlistLocations = $xspfContent.playlist.trackList.track.location

# 3. Process the playlist paths to make them comparable
$playlistFiles = New-Object System.Collections.Generic.HashSet[string]
foreach ($location in $playlistLocations) {
    $cleanedPath = $location -replace "file:///", ""
    $cleanedPath = $cleanedPath -replace "%20", " "
    $fullPath = [System.IO.Path]::GetFullPath($cleanedPath)
    [void]$playlistFiles.Add($fullPath)
}

# 4. Compare the lists and find files not in the playlist
Write-Host "The following files are in the music folder but not in the playlist:"
$isMatch = $false
foreach ($file in $folderFiles) {
    if (-not $playlistFiles.Contains($file)) {
        Write-Host "- $file"
        $isMatch = $true
    }
}

if (-not $isMatch) {
    Write-Host "All relevant files in the music folder are included in the playlist."
}