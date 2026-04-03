rule Suspicious_PowerShell_Command
{
    strings:
        $ps1 = "powershell -enc" nocase
        $ps2 = "Invoke-Expression" nocase
    condition:
        any of them
}
