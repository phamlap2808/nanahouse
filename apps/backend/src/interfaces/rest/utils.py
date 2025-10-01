import traceback
from dataclasses import dataclass
import inspect
from functools import wraps
from typing import Callable

from fastapi import APIRouter, HTTPException


@dataclass(kw_only=True)
class APIRoute:
    path: str
    methods: list[str]
    handler: Callable
    response_model: type | None = None

def err_handler_api(fn):
    @wraps(fn)
    async def handler(*args, **kwargs):
        try:
            result = fn(*args, **kwargs)
            if inspect.isawaitable(result):
                return await result
            return result
        except HTTPException as e:
            raise e
        except Exception as e:
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=str(e))
    return handler


def add_api_route(router: APIRouter, routes: list[APIRoute]):
    for route in routes:
        router.add_api_route(
            route.path,
            err_handler_api(route.handler),
            methods=route.methods,
            response_model=route.response_model,
        )