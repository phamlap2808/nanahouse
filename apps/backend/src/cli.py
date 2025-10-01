import asyncio
import subprocess
import sys


def run_cmd(cmd, **kwargs):
    """Run a command and handle errors"""
    print(f"Running: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, **kwargs)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        sys.exit(e.returncode)


def server_dev():
    import uvicorn

    uvicorn.run("interfaces.rest.server:app", host="0.0.0.0", port=8000, reload=True)


def server_prod():
    import uvicorn

    from interfaces.rest.server import app

    uvicorn.run(app, host="0.0.0.0", port=8000)


def lint():
    run_cmd("ruff check .")


def test():
    run_cmd("pytest")



def migrate_db(name: str = "init"):
    """Tạo migration và áp dụng vào DB (Prisma)."""
    run_cmd(f"prisma migrate dev --name {name}")


def db_push():
    """Đồng bộ schema vào DB mà không tạo migration (Prisma)."""
    run_cmd("prisma db push")

