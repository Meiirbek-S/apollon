rule EICAR_Test_File {
  meta:
    description = "Detects the EICAR antivirus test string"
    author = "Apollon"
    severity = "high"
  strings:
    $eicar = "X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"
  condition:
    $eicar
}

rule Suspicious_PowerShell_Command {
  meta:
    description = "Simple heuristic rule for embedded PowerShell execution patterns"
    author = "Apollon"
    severity = "medium"
  strings:
    $ps1 = "powershell -enc" nocase
    $ps2 = "Invoke-Expression" nocase
    $ps3 = "IEX(" nocase
  condition:
    any of ($ps*)
}
