"""
模型管理API路由
处理模型的增删查改操作
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any

from .dependencies import get_model_manager
from .schemas import ModelConfig, APIResponse
from models.model_manager import ModelManager

router = APIRouter(prefix="/api/models", tags=["models"])

@router.get("")
async def get_models(model_manager: ModelManager = Depends(get_model_manager)) -> Dict[str, Any]:
    """获取可用模型列表"""
    try:
        models = model_manager.list_models()
        return {
            "success": True,
            "data": models,
            "message": "模型列表获取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取模型列表失败: {str(e)}")

@router.post("")
async def add_model(
    config: ModelConfig, 
    model_manager: ModelManager = Depends(get_model_manager)
) -> Dict[str, Any]:
    """添加新模型配置"""
    try:
        print(f"收到模型配置: {config}")
        
        # 验证必需字段
        if not config.name.strip():
            raise ValueError("模型名称不能为空")
        if not config.provider.strip():
            raise ValueError("提供商不能为空")
        if not config.model_id.strip():
            raise ValueError("模型ID不能为空")
        
        model_manager.add_model(
            name=config.name,
            provider=config.provider,
            api_key=config.api_key,
            base_url=config.base_url,
            model_id=config.model_id,
            max_tokens=config.max_tokens,
            temperature=config.temperature
        )
        return {
            "success": True,
            "message": f"模型 {config.name} 添加成功"
        }
    except ValueError as e:
        print(f"验证错误: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        print(f"添加模型失败: {str(e)}")
        raise HTTPException(status_code=400, detail=f"添加模型失败: {str(e)}")

@router.delete("/{model_name}")
async def delete_model(
    model_name: str, 
    model_manager: ModelManager = Depends(get_model_manager)
) -> Dict[str, Any]:
    """删除模型配置"""
    try:
        print(f"=== 删除模型API被调用 ===")
        print(f"接收到的模型名称: '{model_name}'")
        print(f"当前所有模型: {list(model_manager.models.keys())}")
        
        # 检查模型是否存在
        has_model = model_manager.has_model(model_name)
        print(f"模型是否存在: {has_model}")
        
        if not has_model:
            print(f"模型 '{model_name}' 不存在，返回404")
            raise HTTPException(status_code=404, detail=f"模型 {model_name} 不存在")
        
        # 删除模型
        print(f"开始删除模型: {model_name}")
        success = model_manager.remove_model(model_name)
        print(f"删除结果: {success}")
        
        if success:
            print(f"模型 {model_name} 删除成功")
            return {
                "success": True,
                "message": f"模型 {model_name} 删除成功"
            }
        else:
            print(f"删除模型 {model_name} 失败")
            raise HTTPException(status_code=400, detail=f"删除模型 {model_name} 失败")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"删除模型异常: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除模型失败: {str(e)}") 