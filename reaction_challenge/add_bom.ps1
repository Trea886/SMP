$content = [System.IO.File]::ReadAllText('D:\gitfork\code\smp\reaction_challenge\generate_fonts.ps1')
[System.IO.File]::WriteAllText('D:\gitfork\code\smp\reaction_challenge\generate_fonts.ps1', $content, [System.Text.UTF8Encoding]::new($true))
Write-Host 'BOM added'
