; 카카오톡 창을 활성화하고 메시지를 보내는 함수
Func Send_Message_To_Open_Chat($chat_name, $messages)
    ConsoleWrite("Attempting to find and activate KakaoTalk window..." & @CRLF)
    Local $kakao_title = "카카오톡"
	Local $room = "박광현"
    If WinExists($kakao_title) Then
        WinActivate($kakao_title)
        ConsoleWrite("KakaoTalk window activated." & @CRLF)
        Sleep(2000) ; 2초 대기
    Else
        ConsoleWrite("KakaoTalk window not found." & @CRLF)
        Return ; 카카오톡 창이 없으면 함수 종료
    EndIf

    ; 채팅방 검색창 클릭
    ConsoleWrite("Activating search function in KakaoTalk..." & @CRLF)
    ControlClick($kakao_title,"", "[CLASS:Edit; INSTANCE:2]") ;
    Sleep(2000)

    ; 기존 텍스트 지우기
    ConsoleWrite("Clearing existing text in the search field..." & @CRLF)
    For $i = 1 To 20
        ControlSend($kakao_title, "", "[CLASS:Edit; INSTANCE:2]", "{BACKSPACE}") ; 백스페이스 키로 텍스트 삭제
    Next

    ; 채팅방 이름 입력
    ConsoleWrite("Entering chat room name..." & @CRLF)
    ClipPut($chat_name) ; 클립보드에 채팅방 이름 복사
    ControlSend($kakao_title, "", "[CLASS:Edit; INSTANCE:2]", "^v") ; 클립보드 내용 붙여넣기 (Ctrl + V)
    Sleep(2000)

    ControlSend($kakao_title, "", "", "{ENTER}") ; 엔터 키로 채팅방 입장
    Sleep(2000)
	
	For $message In $messages
        ClipPut($message) ; 클립보드에 메시지 복사
		ControlSend($room, "", "[CLASS:RICHEDIT50W;INSTANCE:1]", "^v") ; 클립보드 내용 붙여넣기
		Sleep(1000)
		ControlSend($room, "", "", "{ENTER}")
		Sleep(1000)
    Next

    For $i = 1 To 20
        ControlSend($kakao_title, "", "[CLASS:Edit; INSTANCE:2]", "{BACKSPACE}") ; 백스페이스 키로 텍스트 삭제
    Next
	
EndFunc

; 기본 경로 설정
Local $path_current = "C:\Users\weare\pro-ollama\pdf-rag"
Local $path_download = $path_current & "\downloads"
Local $year_last_two = StringRight(@YEAR, 2)
Local $current_date = $year_last_two & @MON & @MDAY
Local $path_daily_download = $path_download & "\" & $current_date
Local $path_llm = $path_daily_download & "\llm_content.json"

; JSON 파일에서 데이터 로드
ConsoleWrite("Loading JSON content from file: " & $path_llm & @CRLF)
#include <File.au3>
#include <Array.au3>
#include <JSON.au3>
Local $file = FileRead($path_llm)
Local $json_data = Json_Decode($file)
ConsoleWrite("File content: " & @CRLF & $path_llm & @CRLF)

; $json_data 변수는 이제 JSON 리스트의 각 항목을 포함하는 배열입니다.
; 배열을 다루기 위해 IsArray 함수로 배열인지 확인합니다.
If IsArray($json_data) Then
    ; JSON 데이터를 $downloads 배열로 직접 할당합니다.
    Local $downloads = $json_data
	Send_Message_To_Open_Chat("박광현", $downloads)
Else
    ConsoleWrite("Error: Decoded JSON data is not an array." & @CRLF)
EndIf
