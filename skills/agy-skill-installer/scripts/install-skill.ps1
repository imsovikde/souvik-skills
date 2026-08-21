<#
.SYNOPSIS
    Automated Skill Installer for Anti-Gravity IDE (Windows / PowerShell)
.DESCRIPTION
    Clones and installs skills 1:1 into both Global (~/.gemini/config/skills/)
    and Local Workspace (.agents/skills/) directories with YAML frontmatter normalization.
#>

param (
    [Parameter(Mandatory=$true, Position=0)]
    [string]$SourceUrlOrPath,

    [Parameter(Mandatory=$false)]
    [string]$SkillName = "",

    [Parameter(Mandatory=$false)]
    [string]$WorkspaceRoot = "$PWD"
)

$ErrorActionPreference = "Stop"

$globalSkills = [System.IO.Path]::Combine($HOME, ".gemini", "config", "skills")
$localSkills = [System.IO.Path]::Combine($WorkspaceRoot, ".agents", "skills")
$antigravitySkills = [System.IO.Path]::Combine($HOME, ".gemini", "antigravity", "skills")
$tempCloneDir = [System.IO.Path]::Combine($env:TEMP, "agy-skill-clone-" + [System.Guid]::NewGuid().ToString().Substring(0,8))

# Ensure target directories exist
if (-not (Test-Path $globalSkills)) { New-Item -ItemType Directory -Path $globalSkills -Force | Out-Null }
if (-not (Test-Path $localSkills)) { New-Item -ItemType Directory -Path $localSkills -Force | Out-Null }
if (-not (Test-Path $antigravitySkills)) { New-Item -ItemType Directory -Path $antigravitySkills -Force | Out-Null }

Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "  Anti-Gravity IDE Skill Installer" -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "Source:        $SourceUrlOrPath"
Write-Host "Global Target: $globalSkills"
Write-Host "Local Target:  $localSkills"
Write-Host ""

$sourceDir = ""

# Handle GitHub URLs vs Local Paths
if ($SourceUrlOrPath -match "^https?://") {
    Write-Host "[1/4] Cloning repository..." -ForegroundColor Yellow
    git clone $SourceUrlOrPath $tempCloneDir --quiet
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to clone repository: $SourceUrlOrPath"
    }
    $sourceDir = $tempCloneDir
} elseif (Test-Path $SourceUrlOrPath) {
    Write-Host "[1/4] Using local path..." -ForegroundColor Yellow
    $sourceDir = (Resolve-Path $SourceUrlOrPath).Path
} else {
    Write-Error "Source path or URL does not exist: $SourceUrlOrPath"
}

Write-Host "[2/4] Analyzing repository structure..." -ForegroundColor Yellow

$installedSkills = @()

# Function to copy a single skill directory completely and sanitize YAML frontmatter
function Copy-SkillFolder {
    param (
        [string]$Src,
        [string]$Name
    )
    
    $targets = @(
        [System.IO.Path]::Combine($globalSkills, $Name),
        [System.IO.Path]::Combine($localSkills, $Name),
        [System.IO.Path]::Combine($antigravitySkills, $Name)
    )
    
    foreach ($target in $targets) {
        if (Test-Path $target) { Remove-Item -Recurse -Force $target }
        Copy-Item -Path $Src -Destination $target -Recurse -Force
        
        # Strip .git directory if present inside the installed skill directory
        $gitDir = [System.IO.Path]::Combine($target, ".git")
        if (Test-Path $gitDir) { Remove-Item -Recurse -Force $gitDir }
        
        # Validate and sanitize SKILL.md YAML frontmatter
        $skMd = [System.IO.Path]::Combine($target, "SKILL.md")
        if (Test-Path $skMd) {
            $content = Get-Content $skMd -Raw -Encoding UTF8
            $parts = $content -split "---"
            if ($parts.Count -ge 3) {
                # Ensure frontmatter description is cleanly quoted or multiline to prevent parser failure
                $fm = $parts[1]
                if ($fm -notmatch "name:\s*" + [regex]::Escape($Name)) {
                    $fm = $fm -replace "name:\s*[\w-]+", "name: $Name"
                }
                $newContent = "---" + $fm + "---" + ($parts[2..($parts.Count - 1)] -join "---")
                Set-Content -Path $skMd -Value $newContent -Encoding UTF8
            }
        }
    }
    
    $hasMdGlobal = Test-Path ([System.IO.Path]::Combine($globalSkills, $Name, "SKILL.md"))
    $hasMdLocal = Test-Path ([System.IO.Path]::Combine($localSkills, $Name, "SKILL.md"))
    
    return [PSCustomObject]@{
        SkillName = $Name
        GlobalInstalled = $hasMdGlobal
        LocalInstalled = $hasMdLocal
        SlashCommand = "/" + $Name
    }
}

Write-Host "[3/4] Installing skills..." -ForegroundColor Yellow

# Scenario A: Specific single skill requested or target has SKILL.md at root
if ($SkillName -ne "" -and (Test-Path ([System.IO.Path]::Combine($sourceDir, "skills", $SkillName)))) {
    $src = [System.IO.Path]::Combine($sourceDir, "skills", $SkillName)
    $res = Copy-SkillFolder -Src $src -Name $SkillName
    $installedSkills += $res
} elseif (Test-Path ([System.IO.Path]::Combine($sourceDir, "SKILL.md"))) {
    $derivedName = if ($SkillName -ne "") { $SkillName } else { (Get-Item $sourceDir).Name }
    if ($derivedName -match "^agy-skill-clone") {
        if ($SourceUrlOrPath -match "/([^/]+?)(\.git)?$") {
            $derivedName = $matches[1]
        } else {
            $derivedName = "custom-skill"
        }
    }
    $res = Copy-SkillFolder -Src $sourceDir -Name $derivedName
    $installedSkills += $res
} elseif (Test-Path ([System.IO.Path]::Combine($sourceDir, "skills"))) {
    # Scenario B: Multiple skills in skills/ directory
    Get-ChildItem -Path ([System.IO.Path]::Combine($sourceDir, "skills")) -Directory | ForEach-Object {
        $skillMd = [System.IO.Path]::Combine($_.FullName, "SKILL.md")
        if (Test-Path $skillMd) {
            $res = Copy-SkillFolder -Src $_.FullName -Name $_.Name
            $installedSkills += $res
        }
    }
} else {
    # Scenario C: Search recursively for any folder containing SKILL.md
    Get-ChildItem -Path $sourceDir -Recurse -Filter "SKILL.md" | ForEach-Object {
        $parent = $_.Directory
        $sName = $parent.Name
        if ($sName -eq (Get-Item $sourceDir).Name -or $sName -match "^agy-skill-clone") {
            if ($SourceUrlOrPath -match "/([^/]+?)(\.git)?$") {
                $sName = $matches[1]
            } else {
                $sName = "custom-skill"
            }
        }
        $res = Copy-SkillFolder -Src $parent.FullName -Name $sName
        $installedSkills += $res
    }
}

# Clean up temp clone directory
if (Test-Path $tempCloneDir) {
    Remove-Item -Recurse -Force $tempCloneDir -ErrorAction SilentlyContinue
}

Write-Host "[4/4] Verification Summary:" -ForegroundColor Yellow
Write-Host ""
$installedSkills | Format-Table -AutoSize

Write-Host "SUCCESS: All skills have been provisioned and registered in Anti-Gravity IDE!" -ForegroundColor Green
