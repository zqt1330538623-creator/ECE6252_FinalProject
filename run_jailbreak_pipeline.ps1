param(
  [string]$Model = "gemma-4-26b-a4b-it",
  [int]$MaxPrompts = 0,
  [int]$MaxOutputTokens = 256,
  [double]$Temperature = 0.0,
  [int]$Seed = 1234
)

$cmd = @("python", "run_jailbreak_pipeline.py", "--model", $Model, "--max-output-tokens", "$MaxOutputTokens", "--temperature", "$Temperature", "--seed", "$Seed")
if ($MaxPrompts -gt 0) {
  $cmd += @("--max-prompts", "$MaxPrompts")
}

Write-Host ">>>" ($cmd -join " ")
& $cmd[0] $cmd[1..($cmd.Length-1)]
