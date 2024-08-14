import pyautogui
import time
import pygetwindow
import pyperclip
import os
from datetime import datetime
import json
import logging

try:
    # 경로 설정
    path_current = os.getcwd()
    logging.debug(f"Current path: {path_current}")

    path_download = os.path.join(path_current, 'downloads')
    logging.debug(f"Download path: {path_download}")

    current_datetime = datetime.now()
    current_date = current_datetime.strftime('%y%m%d')
    path_daily_download = os.path.join(path_download, current_date)
    logging.debug(f"Daily download path: {path_daily_download}")

    path_llm = os.path.join(path_daily_download, "llm_content.json")
    logging.debug(f"LLM content path: {path_llm}")

    # LLM json에서 파일 이름 추출
    with open(path_llm, 'r', encoding='utf-8') as json_file:
        downloads = json.load(json_file)
    logging.debug(f"LLM content loaded: {downloads}")

    def send_message_to_open_chat(chat_name, message):
        # 카카오톡 창을 찾기
        kakao_windows = [window for window in pygetwindow.getWindowsWithTitle('카카오톡') if '카카오톡' in window.title]
        if not kakao_windows:
            logging.debug("Cannot find KakaoTalk window.")
            return

        # 카카오톡 창 활성화
        kakao_window = kakao_windows[0]
        kakao_window.activate()
        logging.debug("KakaoTalk window activated.")
        time.sleep(2)

        # 채팅방 검색
        pyautogui.hotkey('ctrl', 'f')
        logging.debug("Searching for chat room.")
        time.sleep(2)
        
        # 여러 번의 백스페이스로 기존 텍스트 지우기
        for _ in range(10):  # 10번 백스페이스
            pyautogui.press('backspace')
        logging.debug("Cleared previous search text.")
        time.sleep(2)

        pyperclip.copy(chat_name)
        time.sleep(1)
        pyautogui.hotkey('ctrl', 'v')
        logging.debug(f"Pasted chat name: {chat_name}")
        time.sleep(2)

        pyautogui.press('enter')
        time.sleep(2)

        pyautogui.press('enter')
        logging.debug("Entered chat room.")
        time.sleep(2)

        # 메시지 입력
        pyperclip.copy(message)
        time.sleep(1)
        pyautogui.hotkey('ctrl', 'v')
        logging.debug(f"Pasted message: {message}")
        time.sleep(2)

        # 메시지 전송 (Enter 키)
        pyautogui.press('enter')
        logging.debug("Message sent.")

    for download in downloads:
        logging.debug(f"Sending message: {download}")
        send_message_to_open_chat('박광현', download)
except Exception as e:
    logging.debug(f"Error occurred: {str(e)}")

logging.debug("Script finished.")
