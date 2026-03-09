# NanaHouse Backend

Backend API được xây dựng bằng **FastAPI** + **Python 3.12** + **PostgreSQL**.

## Yêu cầu

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- Docker & Docker Compose (cho PostgreSQL)

## Khởi động nhanh

```bash
# 1. Chạy PostgreSQL (từ thư mục root dự án)
cd ../.. && docker compose up -d

# 2. Cài dependencies
uv sync --extra dev

# 3. Chạy dev server
uv run uvicorn app.main:app --reload --port 8000

# 3.1 Chạy dev server ở powershell
$env:Path = "C:\Users\lappg\.local\bin;$env:Path"; $env:PYENV = "$env:USERPROFILE\.pyenv\pyenv-win"; $env:PATH = "$env:USERPROFILE\.pyenv\pyenv-win\bin;$env:USERPROFILE\.pyenv\pyenv-win\shims;$env:PATH"; uv run uvicorn app.main:app --reload --port 8000

# 4. Chạy tests
uv run pytest

# 5. Lint
uv run ruff check .
```

## Cấu hình Database

PostgreSQL được chạy qua Docker Compose với thông tin mặc định:

| Thông tin | Giá trị                                                   |
| --------- | --------------------------------------------------------- |
| Host      | `localhost`                                               |
| Port      | `5432`                                                    |
| Username  | `root`                                                    |
| Password  | `root`                                                    |
| Database  | `nanahouse`                                               |
| URL       | `postgresql+asyncpg://root:root@localhost:5432/nanahouse` |

Để tùy chỉnh, copy `.env.example` thành `.env` và sửa giá trị `NANA_DATABASE_URL`.

## API Docs

Sau khi khởi động server, truy cập:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Cấu trúc

```
app/
├── main.py              # Entry point + lifespan
├── api/v1/router.py     # API v1 routes
├── core/
│   ├── config.py        # App settings (env-based)
│   └── database.py      # Database engine & session
└── models/              # ORM models
tests/
└── test_main.py         # API tests
```
