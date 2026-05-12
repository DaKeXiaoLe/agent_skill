"""
Agent SKILL系统中所有技能的基类。
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class SkillResult:
    """技能执行结果。"""
    success: bool
    tool_call_id: str = ""
    content: str = ""


class SkillBase(ABC):
    """所有技能的抽象基类。"""
    
    def __init__(self, name: str, description: str, version: str = "1.0.0"):
        self.name = name
        self.description = description
        self.required: List[str] = []
        self.parameters: Dict[Dict] = {}
        
    @abstractmethod
    def execute(self, **kwargs) -> SkillResult:
        """
        使用给定参数执行技能。
        
        返回:
            SkillResult: 执行结果。
        """
        pass
    
    def validate_params(self, **kwargs) -> bool:
        """
        验证是否提供了所有必需参数。
        
        返回:
            bool: 如果所有必需参数都存在则返回True。
        """
        for param in self.required:
            if param not in kwargs:
                return False
        return True
    
    def get_info(self) -> Dict[str, Any]:
        """获取此技能的信息。"""
        return {
            "name": self.name,
            "description": self.description,
        }
    
    def to_tool_dict(self) -> dict:
        """将技能转换为OpenAI工具定义格式"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
                "required": self.required
            }
        }
    
    def __str__(self) -> str:
        return f"Skill(name={self.name}, description={self.description})"
    