# BeTrip-Backend

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

### 5. 서버 실행

```bash
uvicorn app.main:app --reload
```

서버가 뜨면 아래 주소로 접속할 수 있습니다.

- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
