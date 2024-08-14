import requests
from bs4 import BeautifulSoup
import json
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import sys
from datetime import datetime
import re
import logging

logging.basicConfig(level=logging.INFO)

# 터미널 출력 인코딩 설정
sys.stdout.reconfigure(encoding='utf-8')

# 현재 날짜와 시간 6자리 형식으로 매일 폴더가 만들어지게 함 -> 다운 파일을 일 단위로 보관 
current_datetime = datetime.now()
current_date = current_datetime.strftime('%y%m%d')
logging.info(f"{current_datetime}")

## 경로 정의 및 폴더 생성
# 다운로드 폴더
path_current = os.getcwd()
path_download = os.path.join(path_current, 'downloads')
os.makedirs(path_download, exist_ok=True)

# 날짜별 폴더
path_daily_download = os.path.join(path_download, current_date)
os.makedirs(path_daily_download, exist_ok=True)

# JSON 파일(기존 공고, 매일 공고, 새 공고)
path_existing_titles = os.path.join(path_download, 'announcements.json')
path_announcements_file = os.path.join(path_daily_download, 'announcements.json')
path_download_file = os.path.join(path_daily_download, 'downloads.json')
path_down_announce_file = os.path.join(path_daily_download, 'down_announce.json')

# 로깅 설정
log_file = os.path.join(path_daily_download, 'execution.log')
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,  # 로그 레벨 설정 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logging.info(f"{current_date}")

logger = logging.getLogger(__name__)

# JSON 파일에서 내용 빼기(load)
def load_titles_from_json(path):
    logger.info('\n\n1. JSON 파일에서 제목 목록을 불러옵니다.')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
            logger.info('기존 제목 목록을 성공적으로 불러왔습니다.')
            return data
    else:
        logger.warning('기존 제목 목록 파일이 없습니다. 빈 목록을 반환합니다.')
        return []

# JSON 파일에 내용(리스트) 저장하기
def save_to_json(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)
    logger.info(f'{file_path} 파일에 데이터를 저장했습니다.')

# 웹 페이지 공고 데이터 크롤링, 제목 추출
def fetch_announcements():
    logger.info('\n\n2. 웹 페이지에서 공고 데이터를 크롤링합니다.')
    url = 'https://www.iris.go.kr/contents/retrieveBsnsAncmBtinSituListView.do'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    announcements = []
    for tag in soup.find_all('a', onclick=True):
        if 'f_bsnsAncmBtinSituListForm_view' in tag['onclick']:
            title = tag.get_text(strip=True)
            announcements.append(title)
            logger.debug(f'발견된 공고 제목: {title}')
    logger.info('웹 페이지에서 공고 데이터를 성공적으로 추출했습니다.')
    return announcements

# 각 제목에 해당하는 링크 방문 및 파일 다운
def visit_announcement_links(new_titles):
    announce = []
    download = []

    chrome_options = Options()
    chrome_options.headless = True
    chrome_options.add_experimental_option('prefs', {
        "download.default_directory": path_daily_download,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })
    # 샌드박스 모드는 보안 기능이지만, 일부 환경에서는 충돌을 일으킬 수 있습니다. 
    # 이를 비활성화하여 충돌을 방지합니다.
    chrome_options.add_argument("--no-sandbox")

    # 기능: /dev/shm 디렉토리의 사용을 비활성화합니다.
    # 목적: 메모리 공유 문제를 방지하기 위함입니다.
    chrome_options.add_argument("--disable-dev-shm-usage")

    # 기능: GPU 가속을 비활성화합니다.
    # 목적: GPU 관련 문제를 방지하고 안정성을 높입니다.
    chrome_options.add_argument("--disable-gpu")

    # 기능: 소프트웨어 래스터라이저를 비활성화합니다.
    # 목적: 그래픽 렌더링 문제를 방지합니다.
    chrome_options.add_argument("--disable-software-rasterizer")
    
    #이거 주석하니 화면 보이기 시작함
    # 기능: 브라우저 확장 프로그램을 비활성화합니다.
    # 목적: 확장 프로그램으로 인한 성능 저하 및 오류를 방지합니다.
    #chrome_options.add_argument("--disable-extensions")

    # 기능: 브라우저 상단의 정보 표시줄을 비활성화합니다.
    # 목적: 정보 표시줄로 인한 UI 문제를 방지합니다.
    chrome_options.add_argument("--disable-infobars")
    # 기능: 원격 디버깅 포트를 설정합니다.
    # 목적: 디버깅과 문제 해결을 용이하게 합니다.
    chrome_options.add_argument("--remote-debugging-port=9222")
    # 기능: 사용자 데이터 디렉토리를 설정합니다.
    # 목적: 새로운 사용자 프로필을 사용하여 기존 데이터와의 충돌을 방지합니다.
    chrome_options.add_argument("--user-data-dir=C:\\Temp\\ChromeProfile")
    # 기능: 백그라운드 타이머 스로틀링을 비활성화합니다.
    # 목적: 백그라운드 탭의 타이머 제한을 해제합니다.
    chrome_options.add_argument("--disable-background-timer-throttling")
    # 기능: 가려진 창의 백그라운드 실행을 비활성화합니다.
    # 목적: 가려진 창이 백그라운드에서 비활성화되는 것을 방지합니다.
    chrome_options.add_argument("--disable-backgrounding-occluded-windows")
    # 기능: 렌더러 백그라운드 실행을 비활성화합니다.
    # 목적: 백그라운드 탭의 렌더링 중단을 방지합니다.
    chrome_options.add_argument("--disable-renderer-backgrounding")
    # 기능: 로그 레벨을 설정합니다.
    # 목적: 불필요한 로그를 줄이고 중요한 로그만 기록합니다.
    chrome_options.add_argument("--log-level=3")
    # 기능: 로그 파일 경로를 설정합니다.
    # 목적: ChromeDriver 로그를 파일로 기록하여 디버깅에 사용합니다.
    chrome_options.add_argument("--log-path=C:\\Temp\\chromedriver.log")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    base_url = 'https://www.iris.go.kr/contents/retrieveBsnsAncmBtinSituListView.do'
    driver.get(base_url)
    
    for title in new_titles:
        try:
            link = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, f"//a[contains(text(), '{title}')]"))
            )
            link.click()
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            
            links = driver.find_elements(By.XPATH, "//a[contains(., '공고') and contains(@href, 'javascript:f_bsnsAncm_downloadAtchFile')]")
            if not links:
                links = driver.find_elements(By.XPATH, "//a[contains(., '공모') and contains(@href, 'javascript:f_bsnsAncm_downloadAtchFile')]")
            if links:
                driver.execute_script("arguments[0].click();", links[0])
                time.sleep(5)
                pixed_name = re.sub(r'\s*\(\d+(\.\d+)?\w+\)$', '', links[0].text)
                if pixed_name[-3:] in ['pdf', 'wpx', 'hwp']:
                    download.append(pixed_name)
                    announce.append(title)
                    logger.info(f'\n{title} 공고의 파일 {links[0].text}을(를) 다운로드했습니다.')
                else:
                    logger.warning(f'\n{pixed_name[-3:]} 형식의 파일이라 다운 안했습니다.')
            else:
                logger.warning(f'\n{title} 공고에 다운로드 링크가 없습니다.')
                
            driver.back()
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            
        except Exception as e:
            logger.error(f'\n{title} 공고 처리 중 오류 발생: {e}')
            continue
    save_to_json(path_download_file, download)
    save_to_json(path_down_announce_file, announce)
    logger.info('다운로드한 파일명과 공고 제목을 JSON 파일로 저장했습니다.')

if not os.path.exists(path_existing_titles):
    save_to_json(path_existing_titles, [])

new_announcements = []

logger.info('\n\n3. 전체 공고 제목을 추출하여 리스트에 저장합니다.')
announcements = fetch_announcements()

logger.info('\n\n4. 기존 공고 제목을 JSON 파일에서 불러옵니다.')
existing_titles = load_titles_from_json(path_existing_titles)

logger.info('\n\n5. 전체 공고 중에서 기존에 없던 새 공고를 찾아 리스트에 추가합니다.')
for announcement in announcements:
    if announcement not in existing_titles:
        logger.info(f'새로운 공고 발견: {announcement}')
        new_announcements.append(announcement)

logger.info('\n\n6. 전체 공고를 JSON 파일에 저장합니다.')
save_to_json(path_announcements_file, announcements)

logger.info('\n\n7. 기존 공고 목록을 JSON 파일에 업데이트합니다.')
save_to_json(path_existing_titles, announcements)

if new_announcements:
    logger.info('\n\n8. 새 공고가 발견되어, 해당 링크를 방문하고 파일을 다운로드합니다.')
    visit_announcement_links(new_announcements)
else:
    save_to_json(path_download_file, [])
    logger.info('\n\n8. 새로운 공고가 없습니다.')
