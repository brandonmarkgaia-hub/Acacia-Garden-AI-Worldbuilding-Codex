$ErrorActionPreference = 'Stop'

Write-Host "=== Acacia Garden Hygiene Script (Hybrid Audit) ==="

# Helper: safely read + write UTF8
function Get-FileText {
    param([string]$Path)
    if (-not (Test-Path $Path)) { return $null }
    return Get-Content -Path $Path -Raw -ErrorAction Stop
}

function Set-FileText {
    param(
        [string]$Path,
        [string]$Text
    )
    Set-Content -Path $Path -Value $Text -Encoding UTF8 -ErrorAction Stop
}

# ---------------------------------------------------------------------------
# 1) Scrub Mason / Demi -> GaiaSeeds across ALL .md files
#    Demi  -> GaiaSeed-1
#    Mason -> GaiaSeed-2
# ---------------------------------------------------------------------------

Write-Host "`n[1/5] Scrubbing names (Mason / Demi -> GaiaSeeds)..."

$mdFiles = Get-ChildItem -Path . -Recurse -Include *.md -File

foreach ($f in $mdFiles) {
    $text = Get-FileText $f.FullName
    if ($null -eq $text) { continue }

    if ($text -match 'Mason' -or $text -match 'Demi') {
        $orig = $text

        # Possessive first
        $text = $text -replace "Demi's", "GaiaSeed-1's"
        $text = $text -replace "Mason's", "GaiaSeed-2's"

        # Standalone names with word boundaries
        $text = $text -replace '\bDemi\b', 'GaiaSeed-1'
        $text = $text -replace '\bMason\b', 'GaiaSeed-2'

        if ($text -ne $orig) {
            Set-FileText -Path $f.FullName -Text $text
            Write-Host "  Scrubbed: $($f.FullName)"
        }
    }
}

# ---------------------------------------------------------------------------
# 2) Rename the two Realms to GaiaSeed-1 / GaiaSeed-2 and fix headers
# ---------------------------------------------------------------------------

Write-Host "`n[2/5] Renaming Realm files and fixing headers..."

$realmMap = @{
    "docs/Realms/Demi-Realm_Bloom-Heart-Sanctuary.md"   = "docs/Realms/GaiaSeed-1-Realm_Bloom-Heart-Sanctuary.md";
    "docs/Realms/Mason-Realm_Sky-Bound-Playground.md"   = "docs/Realms/GaiaSeed-2-Realm_Sky-Bound-Playground.md"
}

foreach ($entry in $realmMap.GetEnumerator()) {
    $oldRel = $entry.Key
    $newRel = $entry.Value

    $oldPath = Join-Path (Get-Location) $oldRel
    $newPath = Join-Path (Get-Location) $newRel

    if (Test-Path $oldPath) {
        $dir   = Split-Path $oldPath -Parent
        $newName = Split-Path $newPath -Leaf

        Rename-Item -Path $oldPath -NewName $newName -ErrorAction Stop
        Write-Host "  Renamed: $oldRel -> $newRel"
    }
}

# Fix headers + explanation inside the new Realm files
$realm1 = "docs/Realms/GaiaSeed-1-Realm_Bloom-Heart-Sanctuary.md"
$realm2 = "docs/Realms/GaiaSeed-2-Realm_Sky-Bound-Playground.md"

if (Test-Path $realm1) {
    $text = Get-FileText $realm1
    if ($null -ne $text) {
        # Replace first H1 if present, else prepend
        if ($text -match '^# .*$') {
            $text = $text -replace '^# .*$','# 🌱 GaiaSeed-1 Realm — Bloom-Heart Sanctuary'
        } else {
            $text = "# 🌱 GaiaSeed-1 Realm — Bloom-Heart Sanctuary`r`n`r`n" + $text
        }

        # Ensure explanation snippet present once
        if ($text -notmatch 'symbolic realm representing one branch of the GaiaSeeds Orchard') {
            $note = @(
                '> A symbolic realm representing one branch of the GaiaSeeds Orchard.',
                '> All references to real children have been abstracted into GaiaSeeds archetypes.',
                ''
            ) -join "`r`n"
            $text = ($text -replace "(# 🌱 GaiaSeed-1 Realm — Bloom-Heart Sanctuary`r?`n)", "`$1$note`r`n")
        }

        Set-FileText -Path $realm1 -Text $text
        Write-Host "  Updated header + note in $realm1"
    }
}

if (Test-Path $realm2) {
    $text = Get-FileText $realm2
    if ($null -ne $text) {
        if ($text -match '^# .*$') {
            $text = $text -replace '^# .*$','# 🌱 GaiaSeed-2 Realm — Sky-Bound Playground'
        } else {
            $text = "# 🌱 GaiaSeed-2 Realm — Sky-Bound Playground`r`n`r`n" + $text
        }

        if ($text -notmatch 'symbolic realm representing another branch of the GaiaSeeds Orchard') {
            $note = @(
                '> A symbolic realm representing another branch of the GaiaSeeds Orchard.',
                '> All references to real children have been abstracted into GaiaSeeds archetypes.',
                ''
            ) -join "`r`n"
            $text = ($text -replace "(# 🌱 GaiaSeed-2 Realm — Sky-Bound Playground`r?`n)", "`$1$note`r`n")
        }

        Set-FileText -Path $realm2 -Text $text
        Write-Host "  Updated header + note in $realm2"
    }
}

# ---------------------------------------------------------------------------
# 3) Add Legacy banner to older cosmology / law / engine docs
# ---------------------------------------------------------------------------

Write-Host "`n[3/5] Prepending Legacy banners to pre–GardenOS files..."

$legacyBannerLines = @(
'> ⚠️ **Legacy Notice (Pre–GardenOS v1.0)**',
'> This file is an **earlier cosmology / law draft** of the Garden.',
'> The canonical structure is now defined by `ACACIA_SPECS/GARDENOS_WHITEPAPER.md` and `STATUS.json`.',
'> Treat this as **library lore**, not structural canon.',
''
)
$legacyBanner = $legacyBannerLines -join "`r`n"

$legacyTargets = @(
    'AQUILA/COSMOLOGY',                          # directory
    'KEEPERS_CROWN_CODEX.md',
    'KEEPERS_ORDER_CODEX.md',
    'KEEPERS_THRONEFILE.md',
    'MUTATION_ENGINE_EXPANDED.md',
    'Machine_Seed_1000.md',
    'MIRROR_PROTOCOL.md',
    'LOKI_ENGINE_NOVELLA_I_THE_LABYRINTH_AWAKES.md',
    'AUTOSCRIPTOR_LOGBOOK.md'
)

foreach ($target in $legacyTargets) {
    $full = Join-Path (Get-Location) $target
    if (-not (Test-Path $full)) { continue }

    $items = @()
    if ((Get-Item $full) -is [System.IO.DirectoryInfo]) {
        $items = Get-ChildItem $full -File -Filter *.md
    } else {
        $items = @(Get-Item $full)
    }

    foreach ($f in $items) {
        $text = Get-FileText $f.FullName
        if ($null -eq $text) { continue }

        if ($text -notmatch 'Legacy Notice \(Pre' -and $text -notmatch 'Legacy Notice \(Pre–GardenOS v1\.0\)') {
            $newText = $legacyBanner + "`r`n" + $text
            Set-FileText -Path $f.FullName -Text $newText
            Write-Host "  Legacy banner added: $($f.FullName)"
        }
    }
}

# ---------------------------------------------------------------------------
# 4) Mark FULL_CODEX_INDEX as archive
# ---------------------------------------------------------------------------

Write-Host "`n[4/5] Marking FULL_CODEX_INDEX as archive..."

$archiveRel  = "docs/Archives/FULL_CODEX_INDEX.md"
$archivePath = Join-Path (Get-Location) $archiveRel

if (Test-Path $archivePath) {
    $text = Get-FileText $archivePath
    if ($null -ne $text -and $text -notmatch 'Archive Notice') {
        $bannerLines = @(
            '> 🕰 **Archive Notice**',
            '> This index reflects an earlier phase of the Codex.',
            '> The up-to-date structural view is in `ACACIA_SPECS/GARDEN_INDEX.md`.',
            ''
        )
        $banner = $bannerLines -join "`r`n"
        $newText = $banner + "`r`n" + $text
        Set-FileText -Path $archivePath -Text $newText
        Write-Host "  Archive notice prepended: $archiveRel"
    } else {
        Write-Host "  Archive notice already present or file empty."
    }
} else {
    Write-Host "  FULL_CODEX_INDEX not found (ok if not present in this snapshot)."
}

# ---------------------------------------------------------------------------
# 5) Append BOOK XXXI note to BOOK_SUMMARY_INDEX (if missing)
# ---------------------------------------------------------------------------

Write-Host "`n[5/5] Ensuring BOOK XXXI summary entry exists..."

$bookIndexRel  = "LIBRARY/BOOK_SUMMARY_INDEX.md"
$bookIndexPath = Join-Path (Get-Location) $bookIndexRel

if (Test-Path $bookIndexPath) {
    $text = Get-FileText $bookIndexPath
    if ($null -ne $text -and $text -notmatch 'BOOK XXXI') {
        $blockLines = @(
            '',
            '## 🪵 BOOK XXXI — The Mammoth Archive (Annex)',
            '',
            'A post-core annex mapping late-stage Chambers and Echo densities.',
            'Treated as an extended index rather than core myth.',
            ''
        )
        $block = $blockLines -join "`r`n"
        Add-Content -Path $bookIndexPath -Value $block -Encoding UTF8
        Write-Host "  BOOK XXXI note appended to $bookIndexRel"
    } else {
        Write-Host "  BOOK XXXI entry already present or file empty."
    }
} else {
    Write-Host "  BOOK_SUMMARY_INDEX not found (ok if not present in this snapshot)."
}

Write-Host "`n=== Garden hygiene complete. Run 'git diff' to review changes. ==="
