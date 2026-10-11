
$ErrorActionPreference = "Continue"
$baseUrl = "http://127.0.0.1:8000"

$endpoints = @(
    @{ Name = "portfolio"; Path = "/api/portfolio"; Expected = @(200) },
    @{ Name = "analytics"; Path = "/api/analytics"; Expected = @(200) },
    @{ Name = "history"; Path = "/api/history?days=30"; Expected = @(200) },
    @{ Name = "positions"; Path = "/api/positions"; Expected = @(200) },
    @{ Name = "latest-report"; Path = "/api/reports/latest"; Expected = @(200, 404) }
)

New-Item -ItemType Directory -Force -Path "tmp\api-check" | Out-Null

$failed = $false

foreach ($endpoint in $endpoints) {
    $name = $endpoint.Name
    $url = "$baseUrl$($endpoint.Path)"

    try {
        $response = Invoke-WebRequest -Uri $url -Method Get
        $status = [int]$response.StatusCode
        $body = $response.Content
    }
    catch {
        $status = 0
        $body = ""

        if ($_.Exception.Response) {
            $status = [int]$_.Exception.Response.StatusCode
            $stream = $_.Exception.Response.GetResponseStream()

            if ($stream) {
                $reader = [System.IO.StreamReader]::new($stream)
                $body = $reader.ReadToEnd()
                $reader.Dispose()
            }
        }
        else {
            $body = $_.Exception.Message
        }
    }

    $file = "tmp\api-check\$name.json"

    if ($body) {
        $body | Set-Content -Path $file -Encoding utf8
    }

    $ok = $endpoint.Expected -contains $status
    $result = if ($ok) { "PASS" } else { "FAIL" }

    Write-Host "$result  $($endpoint.Path)  HTTP $status"

    if (-not $ok) {
        $failed = $true
        Write-Host $body
    }
}

if ($failed) {
    exit 1
}

Write-Host "`nAll endpoint status checks passed."
