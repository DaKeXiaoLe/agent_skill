import json
import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from .skill_base import SkillBase, SkillResult


class get_chat_history(SkillBase):
    """读取和分析对话记录"""
    
    def __init__(self):
        super().__init__(
            name="get_chat_history",
            description="获取当前用户与助手的历史对话记录。可以按日期筛选，并提供AI总结功能。"
        )
        self.parameters = {
            "type": "object",
            "properties": {
                "date_filter": {
                    "type": "string",
                    "description": "日期过滤条件，格式为'YYYYMMDD'（如'20250216'）或'今天'、'昨天'、'最近7天'等。如果为空，则处理所有会话。"
                },
                "summary": {
                    "type": "boolean",
                    "description": "是否使用AI对会话内容进行总结。默认为False，只返回会话列表；为True时返回AI总结。"
                }
            }
        }
        self.required = []  # 参数都是可选的
        
        # 对话记录目录
        self.conversations_dir = "conversations"
        
        # OpenAI客户端配置（用于AI总结）
        try:
            from openai import OpenAI
            self.model = "deepseek-chat"
            self.client = OpenAI(
                api_key="sk-**********************",
                base_url="https://api.deepseek.com/v1",
            )
            self.has_openai = True
        except ImportError:
            self.has_openai = False
            self.client = None
    
    def _get_session_files(self) -> List[str]:
        """获取所有会话文件"""
        if not os.path.exists(self.conversations_dir):
            return []
        
        session_files = []
        for filename in os.listdir(self.conversations_dir):
            if filename.endswith('.json') and filename.startswith('session_'):
                session_files.append(os.path.join(self.conversations_dir, filename))
        
        # 按修改时间排序（最新的在前）
        session_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        return session_files
    
    def _parse_date_from_filename(self, filename: str) -> Optional[datetime]:
        """从文件名解析日期时间"""
        # 匹配 session_YYYYMMDD_HHMMSS.json 格式
        match = re.search(r'session_(\d{8})_(\d{6})\.json', os.path.basename(filename))
        if match:
            date_str = match.group(1)  # YYYYMMDD
            time_str = match.group(2)  # HHMMSS
            try:
                return datetime.strptime(f"{date_str}_{time_str}", "%Y%m%d_%H%M%S")
            except ValueError:
                return None
        return None
    
    def _get_relative_date(self, date_filter: str) -> Optional[str]:
        """处理相对日期描述"""
        today = datetime.now()
        
        if date_filter == "今天":
            return today.strftime("%Y%m%d")
        elif date_filter == "昨天":
            yesterday = today - timedelta(days=1)
            return yesterday.strftime("%Y%m%d")
        elif date_filter == "前天":
            day_before_yesterday = today - timedelta(days=2)
            return day_before_yesterday.strftime("%Y%m%d")
        elif date_filter == "最近7天" or date_filter == "过去一周":
            return (today - timedelta(days=7)).strftime("%Y%m%d")
        elif date_filter == "最近30天" or date_filter == "过去一个月":
            return (today - timedelta(days=30)).strftime("%Y%m%d")
        
        # 尝试直接解析为YYYYMMDD格式
        if re.match(r'^\d{8}$', date_filter):
            return date_filter
        
        return None
    
    def _filter_files_by_date(self, files: List[str], date_filter: Optional[str]) -> List[str]:
        """根据日期过滤文件"""
        if not date_filter:
            return files
        
        # 处理相对日期描述
        target_date_str = self._get_relative_date(date_filter)
        if not target_date_str:
            # 如果不是相对日期，尝试直接使用
            target_date_str = date_filter
        
        filtered_files = []
        for filepath in files:
            file_date = self._parse_date_from_filename(filepath)
            if not file_date:
                continue
            
            file_date_str = file_date.strftime("%Y%m%d")
            
            # 处理"最近N天"的情况
            if date_filter in ["最近7天", "过去一周", "最近30天", "过去一个月"]:
                days_ago = 7 if "7" in date_filter or "一周" in date_filter else 30
                cutoff_date = datetime.now() - timedelta(days=days_ago)
                if file_date >= cutoff_date:
                    filtered_files.append(filepath)
            # 处理具体日期
            elif file_date_str == target_date_str:
                filtered_files.append(filepath)
        
        return filtered_files
    
    def _load_session_content(self, filepath: str) -> Dict[str, Any]:
        """加载会话文件内容"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            return {"error": f"加载文件失败: {str(e)}", "filepath": filepath}
    
    def _extract_user_messages(self, session_content: Dict[str, Any]) -> List[str]:
        """从会话内容中提取用户消息"""
        messages = session_content.get("messages", [])
        user_messages = []
        
        for msg in messages:
            if msg.get("role") == "user":
                content = msg.get("content", "").strip()
                if content:
                    user_messages.append(content)
        
        return user_messages
    
    def _generate_ai_summary(self, session_content: Dict[str, Any]) -> str:
        """使用AI生成会话总结"""
        if not self.has_openai or not self.client:
            return "AI总结功能不可用（OpenAI客户端未初始化）"
        
        try:
            messages = session_content.get("messages", [])
            if not messages:
                return "会话中没有消息内容"
            
            # 构建提示词
            prompt = """请分析以下对话记录，提取关键信息并回答以下问题：
1. 用户主要询问了哪些问题？
2. 这些问题的核心主题是什么？
3. 用户的需求或意图是什么？

对话内容：
"""
            
            for msg in messages:
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                if content:
                    prompt += f"{role}: {content}\n"
            
            # 限制长度
            if len(prompt) > 4000:
                prompt = prompt[:4000] + "...\n[内容过长，已截断]"
            
            # 调用AI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的对话分析助手，擅长总结对话内容和提取关键信息。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"AI总结生成失败: {str(e)}"
    
    def _format_user_questions_summary(self, user_messages: List[str]) -> str:
        """格式化用户问题总结"""
        if not user_messages:
            return "没有找到用户的问题。"
        
        summary = f"用户共提出了 {len(user_messages)} 个问题：\n\n"
        
        for i, question in enumerate(user_messages, 1):
            # 截断过长的内容
            if len(question) > 100:
                question_preview = question[:100] + "..."
            else:
                question_preview = question
            
            summary += f"{i}. {question_preview}\n"
        
        return summary
    
    def execute(self, **kwargs) -> SkillResult:
        """执行对话记录读取技能"""
        date_filter = kwargs.get("date_filter")
        summary = kwargs.get("summary", False)
        
        # 获取所有会话文件
        all_files = self._get_session_files()
        
        if not all_files:
            return SkillResult(
                success=False,
                content="未找到任何会话记录文件。"
            )
        
        # 根据日期过滤文件
        filtered_files = self._filter_files_by_date(all_files, date_filter)
        
        if not filtered_files:
            date_display = date_filter if date_filter else "指定日期"
            return SkillResult(
                success=False,
                content=f"未找到匹配'{date_display}'的会话记录。"
            )
        
        result_content = ""
        
        if date_filter:
            date_display = date_filter
        else:
            date_display = "所有日期"
        
        result_content += f"找到 {len(filtered_files)} 个匹配'{date_display}'的会话记录：\n\n"
        
        # 收集所有用户消息用于总体分析
        all_user_messages = []
        
        for i, filepath in enumerate(filtered_files, 1):
            content = self._load_session_content(filepath)
            file_date = self._parse_date_from_filename(filepath)
            
            result_content += f"=== 会话 {i} ===\n"
            
            if file_date:
                result_content += f"时间: {file_date.strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            if "error" in content:
                result_content += f"状态: {content['error']}\n\n"
                continue
            
            # 提取用户消息
            user_messages = self._extract_user_messages(content)
            all_user_messages.extend(user_messages)
            
            result_content += f"消息总数: {len(content.get('messages', []))}\n"
            result_content += f"用户问题数: {len(user_messages)}\n"
            
            # AI总结
            if summary and self.has_openai:
                result_content += "\nAI总结:\n"
                ai_summary = self._generate_ai_summary(content)
                result_content += f"{ai_summary}\n"
            
            result_content += "\n"
        
        # 如果没有使用AI总结，但需要回答"我昨天都问了你什么"这类问题
        if not summary and date_filter and all_user_messages:
            result_content += "\n=== 用户问题总结 ===\n"
            result_content += self._format_user_questions_summary(all_user_messages)
        
        # 如果启用了总结但AI不可用
        elif summary and not self.has_openai:
            result_content += "\n注意: AI总结功能当前不可用。\n"
        
        return SkillResult(
            success=True,
            content=result_content.strip()
        )