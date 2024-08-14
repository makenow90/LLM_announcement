$logFile = "C:\Users\weare\pro-ollama\pdf-rag\script_log.txt"

Function Write-Log {
    param ([string]$message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "$timestamp - $message"
    Add-Content -Path $logFile -Value $logMessage
}

# # PsExec 경로를 정의합니다. PsExec.exe 파일이 해당 위치에 있어야 합니다.
$PsExecPath = "C:\Users\weare\pro-ollama\pdf-rag\PSTools\PsExec.exe"
$ScriptPath = "C:\Users\weare\pro-ollama\pdf-rag\[4]auto_message.exe"
try {
    # PsExec를 사용하여 Python 스크립트를 실행합니다.
    & $PsExecPath -i 1 -accepteula cmd /c $ScriptPath
    # & $PsExecPath -i 1 -accepteula cmd /c "C:\Users\weare\pro-ollama\pdf-rag\[4]auto_message.exe"
    # 실행 완료 기록
    Write-Log "Python script executed successfully."
}
catch {
    # 오류 발생 시 기록
    Write-Log "Error occurred: $_"
}

