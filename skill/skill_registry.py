"""
技能管理和发现的注册表。
"""

from typing import Dict, List, Optional, Type, Any
from .skill_base import SkillBase


class SkillRegistry:
    """技能管理注册表。"""
    
    def __init__(self):
        self._skills: Dict[str, Type[SkillBase]] = {}
        
    def register(self, skill_class: Type[SkillBase]) -> None:
        """注册一个技能类。"""
        skill_instance = skill_class()
        self._skills[skill_instance.name] = skill_class
        
    def register_all(self, skill_classes: List[Type[SkillBase]]) -> None:
        """注册多个技能类。"""
        for skill_class in skill_classes:
            self.register(skill_class)
    
    def get_skill(self, name: str) -> Optional[Type[SkillBase]]:
        """按名称获取技能类。"""
        return self._skills.get(name)
    
    def create_skill(self, name: str, **kwargs) -> Optional[SkillBase]:
        """按名称创建技能实例。"""
        skill_class = self.get_skill(name)
        if skill_class:
            return skill_class(**kwargs)
        return None
    
    def list_skills(self) -> List[Dict[str, Any]]:
        """列出所有已注册技能及其信息。"""
        skills_info = []
        for name, skill_class in self._skills.items():
            skill_instance = skill_class()
            skills_info.append(skill_instance.get_info())
        return skills_info
    
    def skill_names(self) -> List[str]:
        """获取所有已注册技能的名称。"""
        return list(self._skills.keys())
    
    def get_skills_dict(self,) -> List[dict]:
        """获取所有已注册技能的定义。"""
        tools = []
        for name, skill_class in self._skills.items():
            skill_instance = skill_class()
            tools.append(skill_instance.to_tool_dict())
        return tools
    
    def clear(self) -> None:
        """清除所有已注册技能。"""
        self._skills.clear()


# 全局注册表实例
registry = SkillRegistry()


def register_skill(skill_class: Type[SkillBase]) -> Type[SkillBase]:
    """注册技能类的装饰器。"""
    registry.register(skill_class)
    return skill_class