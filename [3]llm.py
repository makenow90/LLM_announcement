from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.chat_models import ChatOllama
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough, RunnableParallel, RunnableMap
from langchain.chains import RetrievalQA
from langsmith import traceable
from dotenv import load_dotenv
import os
from datetime import datetime
import json
import torch
import time
import pdfplumber

# .env에 있는 langsmith 환경변수 가져옴
load_dotenv()
langchain_api_key = os.getenv('LANGCHAIN_API_KEY')

print(torch.cuda.is_available())
print(torch.version.cuda)

# json으로 저장
def save_to_json(file_path, titles):
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(titles, json_file, ensure_ascii=False, indent=4)

## 경로설정
path_current = os.getcwd()
path_download = os.path.join(path_current, 'downloads')
current_datetime = datetime.now()
current_date = current_datetime.strftime('%y%m%d')
path_daily_download = os.path.join(path_download, current_date)
path_announcements_file = os.path.join(path_daily_download,"announcements.json")
path_download_file = os.path.join(path_daily_download,"downloads.json")
path_down_announce_file = os.path.join(path_daily_download, 'down_announce.json')
path_llm = os.path.join(path_daily_download,"llm_content.json")
path_template_file = os.path.join(path_download,"template.json")

with open(path_template_file, 'r', encoding='utf-8') as json_file:
    template = json.load(json_file)

word=['연간', '예산', '사업비', '지원금', '지원 내용', '지원 규모']
nword=['액수가 없음','무형적인 이득']

# queries = [
#     "어떤 목적의 연구 또는 어떤 목적의 사업이야?",
#     "연구목적을 위한 구체적인 연구나 사업 분야의 키워드를 모두 찾아줘. 그 중에 연구나 사업의 목적을 명확히 드러내는 키워드만 5개로 뽑아줘.",
#     "예산 or 연구비 or 사업비 or 지원금 or 지원내용 or 지원규모를 알고 싶습니다. 대부분 근처에 '연간' 또는 '지원' 이라는 단어가 붙을꺼야.",
#     "공고 또는 신청 마감일 알려줘. 공고 마감일은 오늘 이후의 날짜야. 분야별로 날짜가 다를수 있어, 각각 알려줘"
# ]

queries = [
    ("신청기간 or 접수기간 알려줘.","all")
]

with open(path_download_file, 'r', encoding='utf-8') as json_file:
    downloads = json.load(json_file)

with open(path_down_announce_file, 'r', encoding='utf-8') as json_file:
    down_announce = json.load(json_file)

# 오늘 날짜를 가져옴
today_date = datetime.today().isoformat()

# PDF에서 텍스트와 표를 추출하는 함수
def extract_text_and_tables_from_pdf(pdf_path):
    text_content = []
    tables_text = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # 페이지에서 텍스트를 먼저 추출
            text = page.extract_text()
            if text:
                text_content.append(text)  # 텍스트 내용을 text_content에 추가
            # 페이지에서 표를 추출
            tables = page.extract_tables()
            
            for table in tables:
                if table:
                    # 표의 데이터를 마크다운 형식으로 변환
                    cleaned_table = []
                    for row in table:
                        cleaned_row = [str(cell).replace("\n", " ").strip() if cell else '' for cell in row]
                        cleaned_table.append(" | ".join(cleaned_row))
                    # 표를 마크다운 형식으로 변환하여 추가
                    tables_text.append("\n".join(cleaned_table))
            
    # 텍스트와 표의 내용을 결합하여 반환
    combined_content = "\n\n".join(text_content + tables_text)
    return combined_content

@traceable
def announcement_summary(num, pdf_file_name):
    embeddings = None
    try:
        # model = ChatOllama(model="EEVE-Korean-10.8B:latest", temperature=0, max_length=135)
        model = ChatOllama(model="llama3.1", temperature=0.5, max_length=135)
        print('Model loaded successfully')
    except Exception as e:
        print(f'Error loading model: {e}')
        return None

    try:
        combined_content = extract_text_and_tables_from_pdf(os.path.join(path_daily_download, pdf_file_name))
        output = [f'{num+1}번 공고명']
        print('PDF content extracted successfully')
    except Exception as e:
        combined_content = ""
        output = [f'{num+1}번 공고명']
        print(f'Error extracting content from PDF: {e}')
        return None

    for num2, (query, page_range) in enumerate(queries):
        # if page_range == "first3":
        #     combined_content = "\n".join(combined_content.split("\n")[:3])
        #     print('3페이지 로드')
        # 각 문서마다 개별적인 컬렉션을 생성
        collection_name = f"collection_{num}_{current_date}"
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=20)
        docs = text_splitter.split_text(combined_content)
        print(f'Documents split into {len(docs)} chunks')

        embeddings = HuggingFaceEmbeddings(
            model_name='jhgan/ko-sroberta-nli',
            model_kwargs={'device': 'cuda'},
            encode_kwargs={'normalize_embeddings': True},
        )
        
        vectorstore = Chroma.from_texts(docs, embeddings, collection_name=collection_name)
        retriever = vectorstore.as_retriever(
            search_type="similarity_score_threshold", 
            search_kwargs={'k': len(docs), "score_threshold": 0.2}
            )

        # 새로운 체인 빌드
        def _build_chain(input_text):
            context_chain = RunnableMap({
                'context': retriever,
                'question': RunnablePassthrough(),
                'today': RunnablePassthrough()
            })

            prompt = ChatPromptTemplate.from_template(template[num2])
            rag_chain = (
                context_chain
                | prompt
                | model
                | StrOutputParser()
            )
            return rag_chain

        chain = _build_chain(combined_content)
        print(f'Executing RAG chain for query: {query}')
        try:
            result = chain.invoke(query)
            print(f'Result for query {num2}: {result}')
            output.append(result[:150])
        except Exception as e:
            print(f'Error during RAG chain execution for query {num2}: {e}')

    combined_output = '\n\n'.join(output)
    # print(f'Combined output:\n{combined_output}')
    return combined_output

start_time = time.time()
results = []

for index, download in enumerate(downloads):
    summary = announcement_summary(index, download)
    if summary:
        results.append(summary)

save_to_json(path_llm, results)

end_time = time.time()
elapsed_time = end_time - start_time
print(f"Elapsed time: {elapsed_time} seconds")