$logFile = "C:\Users\weare\pro-ollama\pdf-rag\script_log.txt"

Function Write-Log {
    param ([string]$message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "$timestamp - $message"
    Add-Content -Path $logFile -Value $logMessage
}

# PsExec 경로를 정의합니다. PsExec.exe 파일이 해당 위치에 있어야 합니다.
$PsExecPath = "C:\Users\weare\pro-ollama\pdf-rag\PSTools\PsExec.exe"

# Python 스크립트의 절대 경로를 지정합니다.
$PythonScriptPath = "C:\Users\weare\pro-ollama\pdf-rag\[2]hwp_to_pdf.py"

# PsExec를 사용하여 관리자 권한으로 Python 스크립트를 실행합니다.
& $PsExecPath -i 1 -accepteula cmd /c "C:\Users\weare\pro-ollama\pdf-rag\.venv\Scripts\python.exe $PythonScriptPath"

