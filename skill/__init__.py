"""
Agent SKILL项目的技能包。
包含所有技能实现。
"""

from .skill_base import SkillBase
from .skill_registry import SkillRegistry, registry

# 为方便访问导入技能

try:
    from .get_weather_by_city import get_weather_by_city
except ImportError:
    get_weather_by_city = None

try:
    from .get_local_time import get_local_time
except ImportError:
    get_local_time = None

try:
    from .get_chat_history import get_chat_history
except ImportError:
    get_chat_history = None

try:
    from .token_counter import TokenCounter
except ImportError:
    TokenCounter = None

try:
    from .document_manager import document_manager
except ImportError:
    document_manager = None

try:
    from .process_resume import ProcessResume
except ImportError:
    ProcessResume = None

# 自动注册所有可用的技能
def register_all_skills():
    """注册所有可用的技能到全局注册表"""
    registered = False
    
    if get_weather_by_city:
        registry.register(get_weather_by_city)
        registered = True
    
    if get_local_time:
        registry.register(get_local_time)
        registered = True
    
    if get_chat_history:
        registry.register(get_chat_history)
        registered = True
    
    if TokenCounter:
        registry.register(TokenCounter)
        registered = True
    
    if document_manager:
        registry.register(document_manager)
        registered = True
    
    if ProcessResume:
        registry.register(ProcessResume)
        registered = True

    return registered

# 导入时自动注册技能
register_all_skills()

__all__ = [
    'SkillBase',
    'SkillRegistry',
    'register_all_skills',
    'registry',

    
    'get_weather_by_city',
    'get_local_time',
    'get_chat_history',
    'TokenCounter',
    'document_manager',
    'ProcessResume'
]