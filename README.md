# FX Mate Backend

기업의 외화 계약 정보를 바탕으로 환율 리스크를 분석하고, 헤지 전략·금융상품·상담 신청을 연결하는 FastAPI 백엔드입니다.

## 기술 구성

- Python 3.11, FastAPI, SQLAlchemy async
- PostgreSQL + pgvector, Alembic
- 외부 AI 분석 서비스 연동(`AI_SERVICE_BASE_URL`)
- Jinja2 + Playwright PDF 리포트 생성

## 실행 전 준비

Python 3.11과 Docker Desktop이 필요합니다. 기존 `.venv`가 삭제된 Python 경로를 참조한다면 새로 생성합니다.

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
AI_SERVICE_BASE_URL=http://localhost:8001
AI_SERVICE_MOCK_MODE=true
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
3. `POST /api/v1/settlement-items/{settlementId}/risk-assessment`로 환율 리스크를 분석합니다.
4. `PUT /api/v1/settlement-items/{settlementId}/risk-profile`로 성향 답변을 저장합니다.
5. `POST /api/v1/product-matches`로 금융상품 적합도를 산출합니다.
6. `POST /api/v1/strategy-recommendations`으로 전략을 추천하고, `GET /api/v1/strategy-recommendations/{recommendationId}/report`로 PDF를 받습니다.
7. `POST /api/v1/consultation-requests`로 KB 상담을 신청합니다.

## API 목록

| 기능 | 메서드 | 경로 |
|---|---|---|
| 기업 정보 | POST/GET/PUT | `/api/v1/profiles`, `/api/v1/profiles/{profileId}` |
| 계약 | POST/GET/PUT | `/api/v1/contracts` |
| 결제 일정 | POST | `/api/v1/contracts/{contractId}/settlement-items` |
| 리스크 분석 | POST/GET | `/api/v1/settlement-items/{settlementId}/risk-assessment` |
| 성향 분석 | PUT/GET | `/api/v1/settlement-items/{settlementId}/risk-profile` |
| 상품 | GET | `/api/v1/products?strategy_group=FX_HEDGING` |
| 상품 매칭 | POST/GET | `/api/v1/product-matches` |
| 전략 추천/PDF | POST/GET | `/api/v1/strategy-recommendations` |
| 국가 목록 | GET | `/api/v1/countries` |
| 상담 | POST/GET/PATCH | `/api/v1/consultation-requests` |

## 데이터베이스와 migration

스키마 변경 후 Alembic migration을 추가하고 반드시 빈 DB에서 검증합니다.

```powershell
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

CI는 pgvector가 활성화된 PostgreSQL에서 `alembic upgrade head`와 앱 import를 검증합니다.

## 운영 전 확인 사항

- 운영 환경에서는 `AI_SERVICE_MOCK_MODE=false`를 사용하고 실제 AI 서비스 URL을 설정합니다.
- `CORS_ORIGINS`에는 실제 프론트 도메인만 지정합니다. `*`는 사용하지 않습니다.
- 현재 API에는 인증/소유권 검증이 없으므로, 운영 전 Cognito/JWT 기반 인증과 리소스 소유권 검증을 추가해야 합니다.
- PDF 재다운로드를 운영 수준으로 제공하려면 private S3 저장 및 presigned URL 방식을 사용합니다.

## CI

GitHub Actions 워크플로는 push와 pull request마다 문법 검사, migration, FastAPI 앱 import를 실행합니다. 자세한 내용은 `.github/workflows/ci.yml`을 참고하세요.

## 컨테이너 이미지

`Dockerfile`은 Playwright Chromium과 함께 서버를 실행하고, 컨테이너 시작 시 migration을 적용합니다. 운영 환경에서는 여러 컨테이너가 동시에 migration을 실행하지 않도록 배포 파이프라인에서 migration을 한 번만 실행하는 방식으로 전환해야 합니다.
