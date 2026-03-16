<#
PowerShell script to remove numeric or letter prefixes from filenames in a directory.
- Matches:
-  - Two-digit numbers with optional prefix punctuation: 01、, 01. , 01-
-  - Single letters S., W., T. followed by a dot
-  - Keeps the rest of the filename intact
#>
param(
    [Parameter(Mandatory = $true)]
    [string]$Path,
    [switch]$DryRun
)

# Validate path
if (-Not (Test-Path -Path $Path)) {
    Write-Error "Path not found: $Path"
    exit 1
}

# Enumerate only files (not directories)
$items = Get-ChildItem -Path $Path -File -ErrorAction Stop

$prefixPattern = '^(?:\d{2}[\u3001.,]?|[SWT]\.)'

foreach ($item in $items) {
    $name = $item.Name
    if ($name -match $prefixPattern) {
        $newName = ($name -replace $prefixPattern, '').Trim()
        if ($DryRun.IsPresent) {
            Write-Host "$name -> $newName" -ForegroundColor Yellow
        } else {
            Rename-Item -LiteralPath $item.FullName -NewName $newName
            Write-Host "$name -> $newName" -ForegroundColor Green
        }
    }
}
