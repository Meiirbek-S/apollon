rule EICAR_Test_File {
    meta:
        description = "EICAR test signature"
        severity = "high"
        source = "apollon-default-rules"

    strings:
        $eicar = "EICAR-STANDARD-ANTIVIRUS-TEST-FILE!"

    condition:
        $eicar
}

rule Suspicious_PowerShell_EncodedCommand {
    meta:
        description = "PowerShell encoded command pattern"
        severity = "medium"
        source = "apollon-default-rules"

    strings:
        $ps = /powershell(\\.exe)?\\s+(-enc|-encodedcommand)\\s+[A-Za-z0-9+\\/=]{20,}/ nocase

    condition:
        $ps
}

rule Suspicious_Cmd_Download_Execute {
    meta:
        description = "cmd.exe pattern downloading and executing payload"
        severity = "medium"
        source = "apollon-default-rules"

    strings:
        $cmd = /cmd(\\.exe)?\\s+.*(curl|bitsadmin|certutil).*(http|https).*(start|powershell|rundll32)/ nocase

    condition:
        $cmd
}
