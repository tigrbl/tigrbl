param(
    [string]$BaseUrl = "http://127.0.0.1:8765"
)

$ErrorActionPreference = "Stop"

$restCreate = [System.IO.File]::ReadAllText("E:\swarmauri_github\tigrbl\examples\rust_runtime_demo\rest-create.json")
$rpcCreate = [System.IO.File]::ReadAllText("E:\swarmauri_github\tigrbl\examples\rust_runtime_demo\rpc-create.json")
$rpcRead = [System.IO.File]::ReadAllText("E:\swarmauri_github\tigrbl\examples\rust_runtime_demo\rpc-read.json")
& curl.exe --silent "$BaseUrl/healthz"
Write-Host ""

& curl.exe --silent `
  --request POST `
  --header "Content-Type: application/json" `
  --data-raw $restCreate `
  "$BaseUrl/users"
Write-Host ""

& curl.exe --silent "$BaseUrl/users/u1"
Write-Host ""

& curl.exe --silent `
  --request POST `
  --header "Content-Type: application/json" `
  --data-raw $rpcCreate `
  "$BaseUrl/rpc"
Write-Host ""

& curl.exe --silent `
  --request POST `
  --header "Content-Type: application/json" `
  --data-raw $rpcRead `
  "$BaseUrl/rpc"
Write-Host ""
