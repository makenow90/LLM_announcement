import os
import win32com.client as win32
import json
from datetime import datetime
import logging
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))
# 터미널 출력 인코딩 설정
sys.stdout.reconfigure(encoding='utf-8')

# 현재 날짜와 시간 6자리 형식으로 매일 폴더가 만들어지게 함 -> 다운 파일을 일 단위로 보관 
current_datetime = datetime.now()
current_date = current_datetime.strftime('%y%m%d')

## 경로 정의 및 폴더 생성
# 다운로드 폴더
path_current = os.getcwd()
path_download = os.path.join(path_current, 'downloads')

# 날짜별 폴더
path_daily_download = os.path.join(path_download, current_date)

# JSON 파일(기존 공고, 매일 공고, 새 공고)
path_announcements_file = os.path.join(path_daily_download, 'announcements.json')
path_download_file = os.path.join(path_daily_download, 'downloads.json')

# 로깅 설정
log_file = os.path.join(path_daily_download, 'execution.log')
logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,  # 로그 레벨 설정 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logging.debug('스크립트 시작: hwp_to_pdf.py')

# 각종 변수 정리
downloads = []
pdf_lists = []

# 각종 경로 정리
path_current = os.getcwd()  # 현재 경로
logging.debug('1. 현재 경로: %s', path_current)

# 다운폴더 경로, 없다면 만들기
path_download = os.path.join(path_current, 'downloads')
logging.debug('2. 다운로드 경로: %s', path_download)

# 날짜를 6자리 형식으로 매일 폴더가 만들어지게 함 -> 다운 파일을 일 단위로 보관
current_datetime = datetime.now()
current_date = current_datetime.strftime('%y%m%d')
path_daily_download = os.path.join(path_download, current_date)
logging.debug('3. 일별 다운로드 경로: %s', path_daily_download)

# 그 폴더 안에 공고와 다운로드에 관한 데이터 입력
# path_announcements_file = os.path.join(path_daily_download, "announcements.json")
# path_download_file = os.path.join(path_daily_download, "downloads.json")
logging.debug('4. 공고 파일 경로: %s', path_announcements_file)
logging.debug('5. 다운로드 파일 경로: %s', path_download_file)

# 파일이 존재하는지 확인하고 생성
if not os.path.exists(path_download_file):
    logging.error('다운로드 파일이 존재하지 않습니다: %s', path_download_file)
    # 파일이 존재하지 않는 경우, 초기화된 데이터를 저장하여 파일을 생성합니다.
    with open(path_download_file, 'w', encoding='utf-8') as json_file:
        json.dump([], json_file, ensure_ascii=False, indent=4)
else:
    logging.debug('다운로드 파일이 존재합니다: %s', path_download_file)

# 새 공고 json에서 파일 이름 추출
logging.debug('7. 다운로드 파일에서 데이터 로드')
with open(path_download_file, 'r', encoding='utf-8') as json_file:
    downloads = json.load(json_file)
logging.debug('8. 다운로드 파일 내용: %s', downloads)

# json으로 저장
def save_to_json(file_path, titles):
    logging.debug('9. %s 파일로 저장', file_path)
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(titles, json_file, ensure_ascii=False, indent=4)
    logging.debug('10. %s 저장 완료', file_path)

# 한글 파일 pdf로 변환
def hwp_pdf(path, name):
    logging.debug(f'11. 한글 파일 PDF 변환 시작: {path}\{name}')
    # COM 객체 초기화
    # pythoncom.CoInitialize()
    hwp = win32.gencache.EnsureDispatch("HWPFrame.HwpObject")
    hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")  # 보안 경고 창 없애기
    # 한글 프로그램을 보이도록 설정
    hwp.XHwpWindows.Item(0).Visible = False

    # 파일 열기
    hwp.Open(os.path.join(path, name))

    # 파일 이름에서 확장자를 제거하고 이름 재설정
    base_name = os.path.splitext(name)[0]
    logging.debug('12. 기본 이름: %s', base_name)
    saveAsFilename = os.path.join(path, f"{base_name}.pdf")
    logging.debug('13. 저장 파일 이름: %s', saveAsFilename)

    # PDF로 변환 후 저장
    hwp.SaveAs(saveAsFilename, "PDF")
    pdf_lists.append(f"{base_name}.pdf")
    logging.debug('14. PDF 파일 저장 완료: %s', saveAsFilename)
    hwp.Quit()

# 뒤에 3글자로 확장자 판단, 한글 파일, PDF 섞여있던 새 공고를 갱신
logging.debug('15. 다운로드 파일 처리 시작')
for download in downloads:
    if download[-3:] == 'pdf':
        pdf_lists.append(download)
        logging.debug('16. PDF 파일 추가: %s', download)
    else:
        if download[-3:] in ['wpx', 'hwp']:
            hwp_pdf(path_daily_download, download)
            logging.debug('17. 한글 파일 PDF 변환 및 추가: %s', download)
    
save_to_json(path_download_file, pdf_lists)
logging.debug('18. 모든 처리 완료 및 저장')
logging.debug('스크립트 종료: hwp_to_pdf.py')
