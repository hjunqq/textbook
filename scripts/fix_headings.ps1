param(
  [string]$Root = "docs/chapters"
)

if (-not (Test-Path -LiteralPath $Root)) {
  Write-Error "Path not found: $Root"
  exit 1
}

$changed = @()

Get-ChildItem -LiteralPath $Root -Recurse -Filter *.md | ForEach-Object {
  $path = $_.FullName
  $original = Get-Content -LiteralPath $path -Raw
  # Split into lines while preserving empty trailing lines
  $linesIn = $original -split "`r?`n", -1
  $linesOut = New-Object System.Collections.Generic.List[string]
  $inCode = $false
  $i = 0
  while ($i -lt $linesIn.Count) {
    $line = $linesIn[$i]
    $trim = $line.Trim()

    # Toggle fenced code blocks (``` or ~~~)
    if ($trim -match '^(?:```|~~~)') {
      $inCode = -not $inCode
      $linesOut.Add($line)
      $i++
      continue
    }

    if (-not $inCode) {
      # Convert Setext H1 (==== underline) into ATX H2
      if (($i + 1) -lt $linesIn.Count) {
        $next = $linesIn[$i + 1]
        if ($next.Trim() -match '^[=]+$') {
          $text = $line.Trim()
          $linesOut.Add("## " + $text)
          $i += 2
          continue
        }
      }

      # Demote ATX H1 (single # followed by space) to H2
      if ($line -match '^(\s*)#(\s+)') {
        # Ensure it's exactly a single hash, not ## or ###
        if ($line -notmatch '^(\s*)##') {
          $newline = [Regex]::Replace($line, '^(\s*)#(\s+)', '$1##$2')
          $linesOut.Add($newline)
          $i++
          continue
        }
      }
    }

    # Default: keep line as-is
    $linesOut.Add($line)
    $i++
  }

  $newContent = [string]::Join("`r`n", $linesOut)
  if ($newContent -ne $original) {
    Set-Content -LiteralPath $path -Value $newContent -NoNewline
    $changed += $path
  }
}

if ($changed.Count -eq 0) {
  Write-Output "No heading fixes needed."
} else {
  Write-Output "Fixed headings in the following files:" 
  $changed | ForEach-Object { Write-Output "- $_" }
}

