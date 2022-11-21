from typing import Union

import httpx
from fastapi import FastAPI, HTTPException, Cookie, Depends
from pydantic import typing
from starlette import status
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse, RedirectResponse

app = FastAPI()

origins = ['http://localhost:8007', 'http://127.0.0.1:8007', 'https://127.0.0.1:8007', 'https://localhost:8007',
           'https://localhost:8010', 'https://127.0.0.1:8010', 'http://127.0.0.1:8010', 'http://localhost:8010']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=["*"],
)


async def check_http_cookies(x_http_h_a: Union[str, None] = Cookie(None)):
    if x_http_h_a is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized...",
            headers={"WWW-Authenticate": "HttpCookie"},
        )
    elif x_http_h_a == 'deleted':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized...",
            headers={"WWW-Authenticate": "HttpCookie"},
        )
    else:
        client = httpx.AsyncClient(http2=True)
        headers = {
            "x_http_h_a": x_http_h_a,
            "content-type": "application/json"
        }
        result = await client.get(url="http://127.0.0.1:8010/current_user", headers=headers)
        # result = requests.post(url=end_session_endpoint, data=data, headers=headers)
        if result.status_code == 200:
            return result.json()
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden...",
                headers={"WWW-Authenticate": "MiddlewareError"},
            )


@app.get("/")
async def root(response: Response, request: Request):
    x_http_h_a = request.headers.get("x_http_h_a")
    x_http_h_r = request.headers.get("x_http_h_r")
    response.status_code = status.HTTP_201_CREATED
    response = JSONResponse(content={
        "x_http_h_a": x_http_h_a,
        "x_http_h_r": x_http_h_r
    })
    response.set_cookie(
        key="x_http_h_a",
        value=x_http_h_a,
        httponly=True,
        secure=True,
        samesite='none',
        max_age=1800,
        expires=1800,
        path='/',
        domain=None
    )
    response.set_cookie(
        key="x_http_h_r",
        value=x_http_h_r,
        httponly=True,
        secure=True,
        samesite='none',
        max_age=1800,
        expires=1800,
        path='/',
        domain=None
    )
    return response


@app.get("/delete_cookies")
async def delete_cookie(user_data: typing.Any = Depends(check_http_cookies)):
    if user_data is not None:
        response = JSONResponse(content={
            "success": True
        })
        response.delete_cookie(
            key="x_http_h_a",
            httponly=True,
            secure=True,
            samesite="none",
            path='/',
            domain=None
        )
        response.delete_cookie(
            key="x_http_h_r",
            httponly=True,
            secure=True,
            samesite="none",
            path='/',
            domain=None
        )
        response.set_cookie(
            key="x_http_h_a",
            value='deleted',
            httponly=True,
            secure=True,
            samesite="none",
            max_age=4,
            expires=3,
            path='/',
            domain=None
        )
        response.set_cookie(
            key="x_http_h_r",
            value='deleted',
            httponly=True,
            secure=True,
            samesite="none",
            max_age=4,
            expires=3,
            path='/',
            domain=None
        )
        return response
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized...",
            headers={"WWW-Authenticate": "HttpCookie"},
        )


@app.get("/login")
async def login():
    return RedirectResponse('http://localhost:8010/', status_code=status.HTTP_303_SEE_OTHER)


@app.get("/jobs")
async def job_list(user_data: typing.Any = Depends(check_http_cookies)):
    jobs = [{"id": 1, "name": "Name one", "is_active": True}, {"id": 2, "name": "Name two", "is_active": False},
            {"id": 3, "name": "Name three", "is_active": True}, {"id": 4, "name": "Name four", "is_active": True}]
    return {
        "success": True,
        "jobs": jobs,
        "current_user": user_data
    }
