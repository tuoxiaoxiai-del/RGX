# RGX 操盘系统 · 一键安装脚本（Windows / PowerShell）
# 用法： irm https://raw.githubusercontent.com/tuoxiaoxiai-del/RGX/master/install.ps1 | iex
$ErrorActionPreference = "Stop"
$Repo  = "tuoxiaoxiai-del/RGX"
$Branch = "master"

Write-Host "RGX 操盘系统 一键安装" -ForegroundColor Cyan
Write-Host "======================"

# 1) 定位 WorkBuddy skills 目录（支持环境变量覆盖）
if ($env:WORKBUDDY_SKILLS_DIR) {
    $SkillsDir = $env:WORKBUDDY_SKILLS_DIR
} else {
    $SkillsDir = Join-Path $env:USERPROFILE ".workbuddy\skills"
}
if (-not (Test-Path $SkillsDir)) {
    New-Item -ItemType Directory -Path $SkillsDir -Force | Out-Null
}

# 2) 下载仓库到临时目录
$Tmp = Join-Path $env:TEMP ("RGX_" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $Tmp -Force | Out-Null
try {
    if (Get-Command git -ErrorAction SilentlyContinue) {
        git clone --depth 1 --branch $Branch "https://github.com/$Repo.git" (Join-Path $Tmp "repo")
    } else {
        $Url = "https://github.com/$Repo/archive/refs/heads/$Branch.tar.gz"
        $Zip = Join-Path $Tmp "repo.tar.gz"
        Write-Host "==> 下载 RGX ($Repo@$Branch) ..."
        Invoke-WebRequest -Uri $Url -OutFile $Zip -UseBasicParsing
        Expand-Archive -Path $Zip -DestinationPath $Tmp -Force
        $Extracted = Get-ChildItem $Tmp -Directory | Where-Object { $_.Name -ne 'repo' } | Select-Object -First 1
        Move-Item -Path $Extracted.FullName -Destination (Join-Path $Tmp "repo") -Force
    }

    # 3) 复制技能
    $Src = Join-Path $Tmp "repo\skills"
    if (-not (Test-Path $Src)) { throw "未找到 skills 目录" }
    $count = 0
    Get-ChildItem $Src -Directory | ForEach-Object {
        Copy-Item -Path $_.FullName -Destination (Join-Path $SkillsDir $_.Name) -Recurse -Force
        $count++
    }
    Write-Host "==> 完成：已将 $count 个 RGX 技能安装到 $SkillsDir" -ForegroundColor Green
    Write-Host "==> 重启 WorkBuddy 后，输入「RGX」即可启动。" -ForegroundColor Green
} finally {
    Remove-Item $Tmp -Recurse -Force -ErrorAction SilentlyContinue
}
