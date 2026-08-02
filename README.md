# FX Mate Backend

계약 한 건만 입력하면, 결제일까지의 환노출 위험을 진단하고 헤지 전략·금융상품·KB 상담까지 한 번에 연결하는 수출입 중소기업 전용 환리스크 관리 서비스입니다.

- 추천 근거가 전부 설명 가능합니다. 블랙박스 추천이 아니라, 상품 자격 판정·리스크 등급·헤지 전략 전부 규칙 기반으로 산정되고 그 근거가 응답에 그대로 노출됩니다.

- 실제로 배포되어 있습니다. AWS Lightsail + RDS에 라이브로 떠 있고, 계약 등록 → 리스크 진단 → 성향분석 → 상품매칭 → PDF 리포트 → KB 상담 신청까지 전 구간이 실제로 동작합니다. 슬라이드가 아니라 라이브 데모로 확인 가능합니다.

- 라이브 데모
  - API: http://15.165.251.217:8000 
  - Swagger: http://15.165.251.217:8000/docs

| 구성요소 | 저장소 | 역할 |
|---|---|---|
| 백엔드 | `kb_ai-server` | 도메인 로직, 오케스트레이션, DB, PDF, 상담 연동 |
| AI 예측 | `dong-k-k/ai/fx-chronos` | USD/KRW 환율 예측(Random Walk·Chronos-2), 환위험 시나리오 계산 |
| 상품 추천 | `dong-k-k/ai/financial-product-rag` | 규칙 기반 KB·K-SURE 상품 매칭(LLM 미사용) |

## 기술 구성

- Python 3.11, FastAPI, SQLAlchemy async
- PostgreSQL(AWS RDS) + pgvector, Alembic
- 외부 실데이터: 한국수출입은행 환율 API, 한국은행 ECOS API
- 외부 AI 연동: `fx-chronos`(환위험 예측), `financial-product-rag`(상품 추천)
- Jinja2 + Playwright PDF 리포트 생성
- AWS Lightsail 배포, GitHub Actions CI/CD

## 실행 전 준비

Python 3.11과 Docker Desktop이 필요합니다.
 
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
docker compose up -d db
```
 
프로젝트 루트에 `.env`를 만들고 다음 값을 설정합니다.
 
```env
DATABASE_URL=postgresql+asyncpg://postgres:devpassword@localhost:5435/fxmeta
AI_SERVICE_BASE_URL=http://localhost:8000
AI_SERVICE_MOCK_MODE=true
RAG_BASE_URL=http://localhost:8001
EXIM_API_KEY=
ECOS_API_KEY=
CORS_ORIGINS=http://localhost:5173
```
 
개발 DB를 생성하고 서버를 실행합니다.
 
```powershell
alembic upgrade head
uvicorn app.main:app --reload
```
 
- API 문서: `http://127.0.0.1:8000/docs`
- 상태 확인: `GET /health`


## 주요 API 흐름

1. `POST /api/v1/profiles`로 기업 정보를 생성합니다.
2. `POST /api/v1/contracts`로 계약과 결제 일정을 생성합니다.
3. `POST /api/v1/settlement-items/{settlementId}/risk-assessment`로 환율 리스크를 분석합니다. (`fx-chronos` 예측 우선 시도 → 지원범위 밖이거나 무응답이면 ECOS 실데이터 기반 자체 통계로 폴백)
4. `GET /api/v1/settlement-items/{settlementId}/rate-history`로 과거 환율 시계열과 신뢰구간을 조회합니다.
5. `PUT /api/v1/settlement-items/{settlementId}/risk-profile`로 성향 답변을 저장합니다. (규칙 기반 채점 → 목표 헤지비율 산출)
6. `POST /api/v1/product-matches`로 `financial-product-rag`를 호출해 실제 KB·K-SURE 상품 적합도를 산출합니다.
7. `POST /api/v1/strategy-recommendations`으로 전략을 추천하고, `GET /api/v1/strategy-recommendations/{recommendationId}/report`로 PDF를 받습니다.
8. `POST /api/v1/consultation-requests`로 KB 상담을 신청합니다.


## API 목록

| 기능 | 메서드 | 경로 |
|---|---|---|
| 기업 정보 | POST/GET/PUT | `/api/v1/profiles`, `/api/v1/profiles/{profileId}` |
| 계약 | POST/GET/PUT | `/api/v1/contracts` |
| 결제 일정 | POST | `/api/v1/contracts/{contractId}/settlement-items` |
| 리스크 분석 | POST/GET | `/api/v1/settlement-items/{settlementId}/risk-assessment` |
| 과거 환율 시계열 | GET | `/api/v1/settlement-items/{settlementId}/rate-history` |
| 성향 분석 | PUT/GET | `/api/v1/settlement-items/{settlementId}/risk-profile` |
| 상품 매칭(RAG 연동) | POST/GET | `/api/v1/product-matches` |
| 전략 추천/PDF | POST/GET | `/api/v1/strategy-recommendations` |
| 국가 목록 | GET | `/api/v1/countries` |
| 상담 | POST/GET/PATCH | `/api/v1/consultation-requests` |
 
> `/api/v1/admin/products`, `/api/v1/products`는 v2에서 제거되었습니다 — 상품 데이터는 더 이상 자체 DB가 아니라 `financial-product-rag`가 단일 소스로 관리합니다.


## 외부 연동
 
| 연동 대상 | 용도 | 비고 |
|---|---|---|
| 한국수출입은행 Open API | 실시간(당일) 매매기준율 | 영업일 11시 전후 갱신, 일 1,000회 제한 |
| 한국은행 ECOS API (731Y001) | 과거 원/달러 일별 시계열 | ES·변동성 계산의 원천 데이터 |
| `fx-chronos` | Random Walk·Chronos-2 앙상블 예측, 환위험 시나리오 | 현재 USD, 20영업일 이내만 지원 — 범위 밖은 자동 폴백 |
| `financial-product-rag` | KB·K-SURE 실제 상품 27종 규칙 기반 매칭 | LLM 미사용, fitScore 산정 기준 전체 공개 |
 
 
## 구현 현황
 
| STEP | 기능 | 상태 |
|---|---|---|
| STEP 0 | 기업 프로필·계약·결제일정 등록 | ✅ 완료 |
| STEP 1 | 환노출 위험 진단 (순노출액·BEP·97.5% ES) | ✅ 완료 — AI 예측 우선, 실데이터 통계 폴백 |
| STEP 2 | 리스크 대응 성향 진단 (Q1~Q3 → 목표 헤지비율) | ✅ 완료 — 규칙 기반 |
| STEP 3 | 전략 결정·상품 매칭·PDF 리포트 | ✅ 완료 — 전략 결정은 규칙 기반, 상품은 RAG 실데이터 |
| STEP 4 | KB 상담 신청·상태 관리 | ✅ 완료 |
| 실시간 환율 | 한국수출입은행 Open API 연동 | ✅ 완료 |
| 과거 환율 시계열 | 한국은행 ECOS API 연동 | ✅ 완료 |
| 배포 | AWS Lightsail + RDS, GitHub Actions CD | ✅ 완료 |