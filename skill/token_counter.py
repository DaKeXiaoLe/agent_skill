"""
Token 计数技能 - 用于统计对话中的 token 数量并在 AI 回复中显示使用百分比
"""
import os
import json
from typing import Dict, List, Optional, Any
from .skill_base import SkillBase, SkillResult


class TokenCounter(SkillBase):
    """Token 计数技能，用于统计对话 token 数量并显示使用百分比"""
    
    def __init__(self):
        super().__init__(
            name="token_counter",
            description="统计对话中的 token 数量，并在 AI 回复中显示使用百分比（如 [50%]）"
        )
        self.parameters = {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "要计算 token 数量的文本"
                },
                "session_id": {
                    "type": "string",
                    "description": "会话 ID，用于跟踪特定会话的 token 使用情况"
                },
                "reset": {
                    "type": "boolean",
                    "description": "是否重置指定会话的 token 计数"
                }
            }
        }
        self.required = []  # 所有参数都是可选的
        
        # 初始化 tokenizer
        self.tokenizer = self._load_tokenizer()
        
        # 会话 token 计数器
        self.session_tokens: Dict[str, int] = {}
        
        # 默认 token 限制（可根据模型调整）
        self.token_limit = 128000
        
    def _load_tokenizer(self):
        """加载本地 tokenizer"""
        try:
            import transformers
            tokenizer_dir = os.path.join(os.path.dirname(__file__), "tokenizer")
            tokenizer = transformers.AutoTokenizer.from_pretrained(
                tokenizer_dir, trust_remote_code=True
            )
            return tokenizer
        except Exception as e:
            print(f"警告：无法加载 tokenizer: {e}")
            return None
    
    def count_tokens(self, text: str) -> int:
        """计算文本的 token 数量"""
        if not self.tokenizer or not text:
            return 0
        
        try:
            tokens = self.tokenizer.encode(text)
            return len(tokens)
        except Exception as e:
            print(f"警告：token 计数失败: {e}")
            return 0
    
    def get_session_token_count(self, session_id: str = "default") -> int:
        """获取指定会话的累计 token 数量"""
        return self.session_tokens.get(session_id, 0)
    
    def add_to_session(self, text: str, session_id: str = "default") -> int:
        """将文本 token 添加到会话计数中"""
        token_count = self.count_tokens(text)
        current = self.session_tokens.get(session_id, 0)
        self.session_tokens[session_id] = current + token_count
        return token_count
    
    def get_usage_percentage(self, session_id: str = "default") -> float:
        """获取当前会话的 token 使用百分比"""
        current_tokens = self.get_session_token_count(session_id)
        if self.token_limit <= 0:
            return 0.0
        return min(100.0, (current_tokens / self.token_limit) * 100)
    
    def format_ai_response(self, response_text: str, session_id: str = "default") -> str:
        """格式化 AI 响应，添加 token 使用百分比前缀"""
        percentage = self.get_usage_percentage(session_id)
        prefix = f"[{int(percentage)}%] "
        return f"{prefix}🤖 AI[{int(percentage)}%]: {response_text}"
    
    def execute(self, **kwargs) -> SkillResult:
        """执行 token 计数技能"""
        text = kwargs.get("text", "")
        session_id = kwargs.get("session_id", "default")
        reset = kwargs.get("reset", False)
        
        if reset:
            self.session_tokens[session_id] = 0
            return SkillResult(
                success=True,
                content=f"会话 '{session_id}' 的 token 计数已重置"
            )
        
        if text:
            token_count = self.add_to_session(text, session_id)
            total_tokens = self.get_session_token_count(session_id)
            percentage = self.get_usage_percentage(session_id)
            
            return SkillResult(
                success=True,
                content=(
                    f"文本 token 数量: {token_count}\n"
                    f"会话累计 token: {total_tokens}\n"
                    f"使用百分比: {percentage:.1f}% (限制: {self.token_limit})"
                )
            )
        else:
            # 如果没有提供文本，返回当前会话状态
            total_tokens = self.get_session_token_count(session_id)
            percentage = self.get_usage_percentage(session_id)
            
            return SkillResult(
                success=True,
                content=(
                    f"会话 '{session_id}' 状态:\n"
                    f"累计 token: {total_tokens}\n"
                    f"使用百分比: {percentage:.1f}% (限制: {self.token_limit})"
                )
            )
    
    def get_info(self) -> Dict[str, Any]:
        """获取技能信息"""
        info = super().get_info()
        info["token_limit"] = self.token_limit
        info["active_sessions"] = len(self.session_tokens)
        return info


# 全局 token 计数器实例
_token_counter_instance = None

def get_token_counter() -> TokenCounter:
    """获取全局 token 计数器实例"""
    global _token_counter_instance
    if _token_counter_instance is None:
        _token_counter_instance = TokenCounter()
    return _token_counter_instance


def count_tokens(text: str) -> int:
    """快速计算文本 token 数量"""
    counter = get_token_counter()
    return counter.count_tokens(text)


def format_ai_response(response_text: str, session_id: str = "default") -> str:
    """格式化 AI 响应，添加 token 使用百分比前缀"""
    counter = get_token_counter()
    return counter.format_ai_response(response_text, session_id)


def add_to_session(text: str, session_id: str = "default") -> int:
    """将文本 token 添加到会话计数中"""
    counter = get_token_counter()
    return counter.add_to_session(text, session_id)


def get_usage_percentage(session_id: str = "default") -> float:
    """获取当前会话的 token 使用百分比"""
    counter = get_token_counter()
    return counter.get_usage_percentage(session_id)
