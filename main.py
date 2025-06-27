#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大模型测评系统主应用
功能：FastAPI应用，提供模型测评的RESTful API接口
作者：AI助手
创建时间：2024年
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

# 导入API路由模块
from api import models_router, tasks_router, datasets_router, evaluations_router
from api.dependencies import init_dependencies

# 创建FastAPI应用实例
app = FastAPI(
    title="大模型测评系统",
    description="一个完整的大模型测评和评估系统",
    version="1.0.0"
)

# 静态文件和模板配置
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 初始化依赖组件
init_dependencies()

# 添加全局异常处理器
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """处理请求验证错误"""
    print(f"请求验证错误: {exc}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": f"请求数据验证失败: {str(exc)}",
            "errors": exc.errors()
        }
    )

# 注册API路由
app.include_router(models_router)
app.include_router(tasks_router)
app.include_router(datasets_router)
app.include_router(evaluations_router)

@app.get("/")
async def home(request: Request):
    """主页路由"""
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 