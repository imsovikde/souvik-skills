<#
.SYNOPSIS
    Automated Skill & Plugin Installer for Anti-Gravity IDE (Windows / PowerShell)
.DESCRIPTION
    Clones and installs skills and native plugins 1:1 into Antigravity IDE:
    - Global Skills (~/.gemini/config/skills/)
    - Local Workspace Skills (.agents/skills/)
    - Antigravity Skills (~/.gemini/antigravity/skills/)
    - User Agent Skills (~/.agents/skills/)
    - Authoritative Plugins (~/.gemini/config/plugins/<name>/ and .agents/plugins/<name>/)
    - Auto-registers in ~/.gemini/config/config.json under "plugins.<name>.enabled = true"
      for full toggle control inside the Antigravity Customization Settings UI (Ponytail Standard).
#>

param (
    [Parameter(Mandatory=$true, Position=0)]
    [string]$SourceUrlOrPath,

    [Parameter(Mandatory=$false)]
    [string]$SkillName = "",

    [Parameter(Mandatory=$false)]
    [string]$WorkspaceRoot = "$PWD",

    [Parameter(Mandatory=$false)]
    [switch]$AsPlugin,

    [Parameter(Mandatory=$false)]
    [string]$PluginName = ""
)

$ErrorActionPreference = "Stop"

$globalSkills = [System.IO.Path]::Combine($HOME, ".gemini", "config", "skills")
$localSkills = [System.IO.Path]::Combine($WorkspaceRoot, ".agents", "skills")
$antigravitySkills = [System.IO.Path]::Combine($HOME, ".gemini", "antigravity", "skills")
$userAgentSkills = [System.IO.Path]::Combine($HOME, ".agents", "skills")

$globalPlugins = [System.IO.Path]::Combine($HOME, ".gemini", "config", "plugins")
$localPlugins = [System.IO.Path]::Combine($WorkspaceRoot, ".agents", "plugins")
$configJsonPath = [System.IO.Path]::Combine($HOME, ".gemini", "config", "config.json")

$tempCloneDir = [System.IO.Path]::Combine($env:TEMP, "agy-skill-clone-" + [System.Guid]::NewGuid().ToString().Substring(0,8))

# Ensure target directories exist
if (-not (Test-Path $globalSkills)) { New-Item -ItemType Directory -Path $globalSkills -Force | Out-Null }
if (-not (Test-Path $localSkills)) { New-Item -ItemType Directory -Path $localSkills -Force | Out-Null }
if (-not (Test-Path $antigravitySkills)) { New-Item -ItemType Directory -Path $antigravitySkills -Force | Out-Null }
if (-not (Test-Path $userAgentSkills)) { New-Item -ItemType Directory -Path $userAgentSkills -Force | Out-Null }
if (-not (Test-Path $globalPlugins)) { New-Item -ItemType Directory -Path $globalPlugins -Force | Out-Null }
if (-not (Test-Path $localPlugins)) { New-Item -ItemType Directory -Path $localPlugins -Force | Out-Null }

Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "  Anti-Gravity IDE Skill & Plugin Installer" -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "Source:        $SourceUrlOrPath"
Write-Host "Global Skills: $globalSkills"
Write-Host "Local Skills:  $localSkills"
Write-Host "AG Skills:     $antigravitySkills"
Write-Host "Agent Skills:  $userAgentSkills"
Write-Host "Global Plugin: $globalPlugins"
Write-Host "Local Plugin:  $localPlugins"
Write-Host "Config JSON:   $configJsonPath"
Write-Host ""

$sourceDir = ""
$isCloned = $false

# Handle GitHub URLs vs GitHub shorthand (user/repo) vs Local Paths
if ($SourceUrlOrPath -match "^https?://") {
    Write-Host "[1/4] Cloning repository..." -ForegroundColor Yellow
    git clone --depth 1 $SourceUrlOrPath $tempCloneDir --quiet
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to clone repository: $SourceUrlOrPath"
    }
    $sourceDir = $tempCloneDir
    $isCloned = $true
} elseif ($SourceUrlOrPath -match "^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$") {
    $fullUrl = "https://github.com/$SourceUrlOrPath"
    Write-Host "[1/4] Cloning GitHub shorthand ($fullUrl)..." -ForegroundColor Yellow
    git clone --depth 1 $fullUrl $tempCloneDir --quiet
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to clone repository: $fullUrl"
    }
    $sourceDir = $tempCloneDir
    $isCloned = $true
} elseif (Test-Path $SourceUrlOrPath) {
    Write-Host "[1/4] Using local path..." -ForegroundColor Yellow
    $sourceDir = (Resolve-Path $SourceUrlOrPath).Path
} else {
    Write-Error "Source path or URL does not exist: $SourceUrlOrPath"
}

Write-Host "[2/4] Analyzing repository structure & customization profile..." -ForegroundColor Yellow

$installedSkills = @()
$secScript = [System.IO.Path]::Combine($PSScriptRoot, "security-scan.cjs")

# Function to safely register a plugin in ~/.gemini/config/config.json using Node.js
function Register-AntigravityPluginConfig {
    param (
        [string]$ConfigPath,
        [string[]]$PluginNames
    )
    $parentDir = Split-Path $ConfigPath
    if (-not (Test-Path $parentDir)) {
        New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
    }
    
    $nodeScript = @"
const fs = require('fs');
const p = process.argv[2];
const names = process.argv.slice(3);
try {
    let cfg = {};
    if (fs.existsSync(p)) {
        cfg = JSON.parse(fs.readFileSync(p, 'utf8'));
    }
    if (!cfg.plugins) {
        cfg.plugins = {};
    }
    for (const name of names) {
        if (!name) continue;
        cfg.plugins[name] = { enabled: true };
    }
    fs.writeFileSync(p, JSON.stringify(cfg, null, 2) + '\n', 'utf8');
    console.log('Registered plugin(s) in config.json: ' + names.join(', '));
} catch (e) {
    console.error('Failed to update config.json:', e);
    process.exit(1);
}
"@
    $tmpJs = [System.IO.Path]::Combine($env:TEMP, "update-config-" + [System.Guid]::NewGuid().ToString().Substring(0,8) + ".js")
    $utf8NoBom = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText($tmpJs, $nodeScript, $utf8NoBom)
    & node $tmpJs $ConfigPath $PluginNames
    Remove-Item -Force $tmpJs -ErrorAction SilentlyContinue
}

# Function to sanitize YAML frontmatter cleanly
function Sanitize-SkillFrontmatter {
    param (
        [string]$FilePath,
        [string]$SkillName
    )
    if (-not (Test-Path $FilePath)) { return }
    $content = Get-Content $FilePath -Raw -Encoding UTF8
    if (-not $content.StartsWith("---")) { return }
    
    $endIdx = $content.IndexOf("`n---", 3)
    if ($endIdx -lt 0) { return }
    
    $rawFm = $content.Substring(3, $endIdx - 3).Trim()
    $body = $content.Substring($endIdx + 4).TrimStart("`r", "`n")
    
    $lines = $rawFm -split "`r?`n"
    $newLines = @()
    $nameUpdated = $false
    
    for ($i = 0; $i -lt $lines.Count; $i++) {
        $line = $lines[$i]
        if ($line -match "^name:\s*") {
            $newLines += "name: $SkillName"
            $nameUpdated = $true
        } elseif ($line -match "^description:\s*(.*)") {
            $descVal = $matches[1].Trim()
            if ($descVal -match '^".*"$' -or $descVal -match "^'.*'$" -or $descVal -eq ">-" -or $descVal -eq "|") {
                $newLines += $line
            } elseif ($descVal -match ":\s+") {
                $escaped = $descVal.Replace('"', '\"')
                $newLines += "description: `"$escaped`""
            } else {
                $newLines += $line
            }
        } else {
            $newLines += $line
        }
    }
    
    if (-not $nameUpdated) {
        $newLines = @("name: $SkillName") + $newLines
    }
    
    $repairedFm = $newLines -join "`n"
    $newContent = "---`n$repairedFm`n---`n$body"
    $utf8NoBom = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText($FilePath, $newContent, $utf8NoBom)
}

# Function to copy a single skill directory completely and sanitize YAML frontmatter
function Copy-SkillFolder {
    param (
        [string]$Src,
        [string]$Name
    )
    
    $targets = @(
        [System.IO.Path]::Combine($globalSkills, $Name),
        [System.IO.Path]::Combine($localSkills, $Name),
        [System.IO.Path]::Combine($antigravitySkills, $Name),
        [System.IO.Path]::Combine($userAgentSkills, $Name)
    )
    
    $stageDir = [System.IO.Path]::Combine($env:TEMP, "agy-stage-" + [System.Guid]::NewGuid().ToString().Substring(0,8))
    Copy-Item -Path $Src -Destination $stageDir -Recurse -Force
    
    foreach ($target in $targets) {
        if (Test-Path $target) { Remove-Item -Recurse -Force $target }
        Copy-Item -Path $stageDir -Destination $target -Recurse -Force
        
        $gitDir = [System.IO.Path]::Combine($target, ".git")
        if (Test-Path $gitDir) { Remove-Item -Recurse -Force $gitDir }
        
        $skMd = [System.IO.Path]::Combine($target, "SKILL.md")
        Sanitize-SkillFrontmatter -FilePath $skMd -SkillName $Name
        
        if (Test-Path $secScript) {
            & node $secScript $target | Out-Null
        }
    }
    
    Remove-Item -Recurse -Force $stageDir -ErrorAction SilentlyContinue
    
    $hasMdGlobal = Test-Path ([System.IO.Path]::Combine($globalSkills, $Name, "SKILL.md"))
    $hasMdLocal = Test-Path ([System.IO.Path]::Combine($localSkills, $Name, "SKILL.md"))
    
    return [PSCustomObject]@{
        SkillName = $Name
        GlobalInstalled = $hasMdGlobal
        LocalInstalled = $hasMdLocal
        SlashCommand = "/" + $Name
    }
}

# Helper to find declared name in SKILL.md
function Get-SkillDeclaredName {
    param ([string]$SkillMdPath)
    if (Test-Path $SkillMdPath) {
        $content = Get-Content $SkillMdPath -Raw -Encoding UTF8
        if ($content -match "(?m)^name:\s*([^\r\n]+)") {
            return $matches[1].Trim().Trim('"').Trim("'")
        }
    }
    return ""
}

# Check if target is a Native Antigravity Plugin
$isPlugin = $false
$targetPluginName = ""

$hasPluginJson = Test-Path ([System.IO.Path]::Combine($sourceDir, "plugin.json"))
$hasGeminiExt = Test-Path ([System.IO.Path]::Combine($sourceDir, "gemini-extension.json"))
$hasAgPlugin = Test-Path ([System.IO.Path]::Combine($sourceDir, ".antigravity-plugin", "plugin.json"))

if ($AsPlugin -or ($SkillName -eq "" -and ($hasPluginJson -or $hasGeminiExt -or $hasAgPlugin))) {
    $isPlugin = $true
}

if ($isPlugin) {
    Write-Host "[3/4] Installing Native Antigravity Plugin (Ponytail Standard)..." -ForegroundColor Yellow
    
    if ($PluginName -ne "") {
        $targetPluginName = $PluginName
    } elseif ($SkillName -ne "") {
        $targetPluginName = $SkillName
    } elseif ($hasPluginJson) {
        try {
            $pJson = Get-Content ([System.IO.Path]::Combine($sourceDir, "plugin.json")) -Raw | ConvertFrom-Json
            if ($pJson.name) { $targetPluginName = $pJson.name }
        } catch {}
    } elseif ($hasGeminiExt) {
        try {
            $gJson = Get-Content ([System.IO.Path]::Combine($sourceDir, "gemini-extension.json")) -Raw | ConvertFrom-Json
            if ($gJson.name) { $targetPluginName = $gJson.name }
        } catch {}
    }
    
    $repoBaseName = ""
    if ($SourceUrlOrPath -match "/([^/]+?)(\.git)?$") {
        $repoBaseName = $matches[1]
    }
    
    if (-not $targetPluginName) {
        $targetPluginName = if ($repoBaseName) { $repoBaseName } else { "custom-plugin" }
    }
    
    Write-Host "Plugin Name:    $targetPluginName" -ForegroundColor Cyan
    
    $pluginTargets = @(
        [System.IO.Path]::Combine($globalPlugins, $targetPluginName),
        [System.IO.Path]::Combine($localPlugins, $targetPluginName)
    )
    
    $aliasNames = @($targetPluginName)
    if ($repoBaseName -and $repoBaseName -ne $targetPluginName) {
        $aliasNames += $repoBaseName
        $pluginTargets += [System.IO.Path]::Combine($globalPlugins, $repoBaseName)
        $pluginTargets += [System.IO.Path]::Combine($localPlugins, $repoBaseName)
    }
    
    # Stage into isolated temp folder
    $stageDir = [System.IO.Path]::Combine($env:TEMP, "agy-stage-plugin-" + [System.Guid]::NewGuid().ToString().Substring(0,8))
    Copy-Item -Path $sourceDir -Destination $stageDir -Recurse -Force
    
    # Ensure plugin.json exists at root of stage
    $stagePluginJson = [System.IO.Path]::Combine($stageDir, "plugin.json")
    if (-not (Test-Path $stagePluginJson)) {
        $pjContent = @{ name = $targetPluginName } | ConvertTo-Json
        $utf8NoBom = New-Object System.Text.UTF8Encoding $false
        [System.IO.File]::WriteAllText($stagePluginJson, $pjContent, $utf8NoBom)
    }
    
    # Ensure AGENTS.md exists at root if rules/AGENTS.md exists
    $stageAgentsMd = [System.IO.Path]::Combine($stageDir, "AGENTS.md")
    $stageRulesAgentsMd = [System.IO.Path]::Combine($stageDir, "rules", "AGENTS.md")
    if (-not (Test-Path $stageAgentsMd) -and (Test-Path $stageRulesAgentsMd)) {
        Copy-Item -Path $stageRulesAgentsMd -Destination $stageAgentsMd -Force
    }
    
    # Deploy plugin to all plugin targets
    foreach ($pt in $pluginTargets) {
        if (Test-Path $pt) { Remove-Item -Recurse -Force $pt }
        Copy-Item -Path $stageDir -Destination $pt -Recurse -Force
        $gitDir = [System.IO.Path]::Combine($pt, ".git")
        if (Test-Path $gitDir) { Remove-Item -Recurse -Force $gitDir }
        
        # Sanitize any SKILL.md inside plugin
        Get-ChildItem -Path $pt -Recurse -Filter "SKILL.md" | ForEach-Object {
            $dec = Get-SkillDeclaredName -SkillMdPath $_.FullName
            $sName = if ($dec) { $dec } else { $_.Directory.Name }
            Sanitize-SkillFrontmatter -FilePath $_.FullName -SkillName $sName
        }
    }
    Remove-Item -Recurse -Force $stageDir -ErrorAction SilentlyContinue
    
    # Register in config.json
    Register-AntigravityPluginConfig -ConfigPath $configJsonPath -PluginNames $aliasNames
    
    Write-Host "Config registered: plugins.$targetPluginName.enabled = true in $configJsonPath" -ForegroundColor Green
    
    # Now provision all bundled skills across 4 discovery roots
    $bundledSkillsDir = [System.IO.Path]::Combine($sourceDir, "skills")
    if (Test-Path $bundledSkillsDir) {
        Get-ChildItem -Path $bundledSkillsDir -Directory | ForEach-Object {
            $skFile = [System.IO.Path]::Combine($_.FullName, "SKILL.md")
            if (Test-Path $skFile) {
                $dec = Get-SkillDeclaredName -SkillMdPath $skFile
                $sName = if ($dec) { $dec } else { $_.Name }
                $res = Copy-SkillFolder -Src $_.FullName -Name $sName
                $installedSkills += $res
            }
        }
    }
} else {
    Write-Host "[3/4] Installing skills across 4 Antigravity discovery roots..." -ForegroundColor Yellow
    
    # Find all SKILL.md files recursively
    $allSkillFiles = Get-ChildItem -Path $sourceDir -Recurse -Filter "SKILL.md" | Where-Object {
        $_.FullName -notmatch "[\\/](\.git|node_modules|dist|build)[\\/]"
    }

    if ($SkillName -ne "") {
        $matched = $allSkillFiles | Where-Object {
            $dec = Get-SkillDeclaredName -SkillMdPath $_.FullName
            $_.Directory.Name -eq $SkillName -or $dec -eq $SkillName
        }
        
        if ($matched) {
            $targetSkill = $matched | Select-Object -First 1
            $res = Copy-SkillFolder -Src $targetSkill.Directory.FullName -Name $SkillName
            $installedSkills += $res
        } else {
            Write-Error "Skill '$SkillName' not found in $sourceDir"
        }
    } else {
        $seenNames = @{}
        
        foreach ($sf in $allSkillFiles) {
            $dir = $sf.Directory
            $decName = Get-SkillDeclaredName -SkillMdPath $sf.FullName
            $sName = if ($decName -ne "") { $decName } else { $dir.Name }
            
            if ($dir.FullName -eq (Resolve-Path $sourceDir).Path) {
                if ($SourceUrlOrPath -match "/([^/]+?)(\.git)?$") {
                    $sName = $matches[1]
                } else {
                    $sName = "custom-skill"
                }
            }
            
            if ($seenNames.ContainsKey($sName)) {
                $parentPlugin = $dir.Parent.Parent.Name
                if ($parentPlugin -and $parentPlugin -ne "skills" -and $parentPlugin -ne "") {
                    $sName = "$parentPlugin-$sName"
                } else {
                    $sName = "$($dir.Parent.Name)-$sName"
                }
            }
            $seenNames[$sName] = $true
            
            $res = Copy-SkillFolder -Src $dir.FullName -Name $sName
            $installedSkills += $res
            
            if ($sName -match "^([a-z0-9_-]+)-(access|configure)$") {
                $baseName = $matches[2]
                if (-not $seenNames.ContainsKey($baseName)) {
                    $seenNames[$baseName] = $true
                    $resBase = Copy-SkillFolder -Src $dir.FullName -Name $baseName
                    $installedSkills += $resBase
                }
            }
        }
    }
}

# Clean up temp clone directory if created
if ($isCloned -and (Test-Path $tempCloneDir)) {
    Remove-Item -Recurse -Force $tempCloneDir -ErrorAction SilentlyContinue
}

Write-Host "[4/4] Verification Summary:" -ForegroundColor Yellow
Write-Host ""
if ($isPlugin) {
    Write-Host "Plugin Targets:" -ForegroundColor Cyan
    Write-Host "  Global: ~/.gemini/config/plugins/$targetPluginName"
    Write-Host "  Local:  .agents/plugins/$targetPluginName"
    Write-Host "  Status: ENABLED in $configJsonPath (Toggleable in Antigravity Customization Settings UI)" -ForegroundColor Green
    Write-Host ""
}
$installedSkills | Format-Table -AutoSize

Write-Host "SUCCESS: Provisioned $($installedSkills.Count) skills $(if ($isPlugin) { "and native plugin '$targetPluginName'" }) across all Anti-Gravity IDE discovery roots!" -ForegroundColor Green
