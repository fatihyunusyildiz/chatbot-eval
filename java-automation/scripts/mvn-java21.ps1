param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $MavenArgs = @("test")
)

$ErrorActionPreference = "Stop"

$javaProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$repoRoot = Resolve-Path (Join-Path $javaProjectRoot "..")

$jdkCandidates = @()
if ($env:JAVA_HOME) {
    $jdkCandidates += $env:JAVA_HOME
}

$adoptiumRoot = "C:/Program Files/Eclipse Adoptium"
if (Test-Path $adoptiumRoot) {
    $jdkCandidates += Get-ChildItem $adoptiumRoot -Directory -Filter "jdk-21*" |
        Sort-Object Name -Descending |
        Select-Object -ExpandProperty FullName
}

$jdkHome = $null
foreach ($candidate in $jdkCandidates | Select-Object -Unique) {
    $javaExecutable = Join-Path $candidate "bin/java.exe"
    if (-not (Test-Path $javaExecutable)) {
        continue
    }

    $productVersion = (Get-Item $javaExecutable).VersionInfo.ProductVersion
    if ($productVersion -match '^21([.]|$)') {
        $jdkHome = $candidate
        break
    }
}

if (-not $jdkHome) {
    throw "JDK 21 not found. Set JAVA_HOME to a JDK 21 installation."
}

$mavenHome = $null
$mavenCommand = $null
if ($env:MAVEN_HOME -and (Test-Path (Join-Path $env:MAVEN_HOME "bin/mvn.cmd"))) {
    $mavenHome = $env:MAVEN_HOME
    $mavenCommand = Join-Path $mavenHome "bin/mvn.cmd"
} else {
    $portableMaven = Join-Path $repoRoot ".tools/apache-maven-3.9.16"
    if (Test-Path (Join-Path $portableMaven "bin/mvn.cmd")) {
        $mavenHome = $portableMaven
        $mavenCommand = Join-Path $mavenHome "bin/mvn.cmd"
    } else {
        $systemMaven = Get-Command mvn.cmd -ErrorAction SilentlyContinue
        if (-not $systemMaven) {
            $systemMaven = Get-Command mvn -ErrorAction SilentlyContinue
        }
        if ($systemMaven) {
            $mavenCommand = $systemMaven.Source
        }
    }
}

if (-not $mavenCommand) {
    throw "Maven not found. Set MAVEN_HOME, add mvn to PATH, or install portable Maven as documented."
}

$env:JAVA_HOME = $jdkHome
$javaBin = Join-Path $env:JAVA_HOME "bin"
$env:Path = "$javaBin;$env:Path"
if ($mavenHome) {
    $env:MAVEN_HOME = $mavenHome
    $mavenBin = Join-Path $env:MAVEN_HOME "bin"
    $env:Path = "$mavenBin;$env:Path"
}

$exitCode = 1
Push-Location $javaProjectRoot
try {
    & $mavenCommand @MavenArgs
    $exitCode = $LASTEXITCODE
} finally {
    Pop-Location
}
exit $exitCode