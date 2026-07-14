# BeTrip-Backend

## Git 커밋 메시지 규칙

### 커밋 타입

| 타입 | 설명 | 사용 예시 |
|------|------|-----------|
| `feat` | 새로운 기능 추가 | 로그인 기능 추가, 자산 조회 API 구현 |
| `fix` | 버그 수정 | 차트 렌더링 오류 수정, 로그인 실패 문제 해결 |
| `refactor` | 기능 변화 없는 코드 구조 개선 | 컴포넌트 분리, 서비스 레이어 구조 개선 |
| `docs` | 문서 수정 | API 명세 수정, README 업데이트 |
| `style` | 코드 스타일 수정 | prettier 적용, 마진 조정 |
| `test` | 테스트 코드 추가 및 수정 | 단위 테스트 추가, Mock 테스트 작성 |
| `chore` | 설정·빌드·패키지 등 유지보수 | eslint 설정, dependency 업데이트 |
| `hotfix` | 운영 환경 긴급 수정 | 운영 서버 장애 수정, 긴급 배포 대응 |

### 커밋 메시지 형식

```
type: subject

# 본문 (선택) - 무엇을 왜 변경했는지, 한 줄 72자 이내 권장
- 로그인 실패 시 예외 처리 추가
- JWT 만료 검증 로직 수정

# Footer (선택) - 관련 이슈
Closes #이슈번호
Related to #이슈번호
```

### 작성 규칙

- 제목은 50자 이내
- 제목과 본문 사이 한 줄 공백
- 제목 끝에 마침표(.) 금지
- 명령문 형태 사용 (예: 수정한다 X → 수정 O)
- 하나의 커밋에는 하나의 작업만 포함
- 커밋 내용은 **한국어**, 이슈 번호는 `(#Number)` 형식으로 Footer에 작성

---

## 시작하기

### 1. 가상환경 생성

```bash
python -m venv venv
```

### 2. 가상환경 활성화

**Mac / Linux**
```bash
source venv/bin/activate
```

**Windows**
```bash
venv\Scripts\activate
```

### 3. 패키지 설치

**개발 환경** (운영 패키지 포함)
```bash
pip install -r requirements-dev.txt
```

**운영 환경**
```bash
pip install -r requirements.txt
```

### 4. 환경변수 설정

```bash
cp .env.example .env
```

`.env` 파일을 열어 실제 값으로 채워주세요.

```
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/betrip
OPENAI_API_KEY=sk-...
```

### 5. pre-commit 설정
`pre-commit` 패키지가 설치된 후 Git Hook을 등록합니다.

```bash
pre-commit install
```

설치 후 커밋할 때마다 자동으로 lint + format이 실행됩니다.

### 6. 서버 실행

```bash
uvicorn app.main:app --reload
```

서버가 뜨면 아래 주소로 접속할 수 있습니다.

- API: http://localhost:8000
- Swagger: http://localhost:8000/docs

---

## Ruff

커밋 시 pre-commit이 자동으로 실행하지만, 수동으로 실행할 수도 있습니다.

**자동 수정**
```bash
ruff check . --fix
ruff format .
```

**검사만**
```bash
ruff check .
ruff format --check .
```
