import datetime
import time
from typing import Dict, Optional
from .skill_base import SkillBase, SkillResult


class get_local_time(SkillBase):
    """获取指定时区或城市的当前时间"""
    
    def __init__(self):
        super().__init__(
            name="get_local_time",
            description="获取当前日期和时间。可以指定时区偏移（如'+08:00'表示东八区）或使用本地时间。"
        )
        self.parameters = {
            "type": "object",
            "properties": {
                "timezone_offset": {
                    "type": "string",
                    "description": "时区偏移，格式为'+HH:MM'或'-HH:MM'，例如'+08:00'表示东八区（中国时间），'-05:00'表示西五区（纽约时间）。如果未提供，则使用系统本地时间。"
                }
            }
        }
        self.required = []  # 时区偏移参数是可选的
        
        # 常见城市到时区偏移的映射
        self.city_to_offset = {
            # 中国城市（东八区）
            "beijing": "+08:00",
            "shanghai": "+08:00",
            "guangzhou": "+08:00",
            "shenzhen": "+08:00",
            "hong kong": "+08:00",
            "taipei": "+08:00",
            
            # 国际城市
            "new york": "-05:00",  # 东部时间
            "los angeles": "-08:00",  # 太平洋时间
            "london": "+00:00",  # GMT
            "paris": "+01:00",  # 中欧时间
            "tokyo": "+09:00",
            "seoul": "+09:00",
            "singapore": "+08:00",
            "sydney": "+10:00",
            "moscow": "+03:00",
            "berlin": "+01:00",
            
            # UTC相关
            "utc": "+00:00",
            "gmt": "+00:00",
        }
    
    def _parse_timezone_offset(self, offset_str: Optional[str] = None) -> datetime.timezone:
        """解析时区偏移字符串为timezone对象"""
        if not offset_str:
            # 返回本地时区
            return datetime.datetime.now().astimezone().tzinfo or datetime.timezone.utc
        
        # 转换为小写以便匹配
        offset_lower = offset_str.lower().strip()
        
        # 检查是否是已知城市
        if offset_lower in self.city_to_offset:
            offset_str = self.city_to_offset[offset_lower]
        
        # 解析时区偏移
        try:
            if offset_str.startswith(('+', '-')):
                # 格式: +HH:MM 或 -HH:MM
                sign = -1 if offset_str[0] == '-' else 1
                hours = int(offset_str[1:3])
                minutes = int(offset_str[4:6]) if len(offset_str) > 3 else 0
                
                offset = datetime.timedelta(hours=hours, minutes=minutes) * sign
                return datetime.timezone(offset)
            else:
                # 如果不是有效的偏移格式，使用UTC
                return datetime.timezone.utc
        except (ValueError, IndexError):
            # 解析失败，使用UTC
            return datetime.timezone.utc
    
    def execute(self, **kwargs) -> SkillResult:
        """执行时间获取技能"""
        timezone_offset = kwargs.get("timezone_offset")
        
        try:
            # 获取时区
            tz = self._parse_timezone_offset(timezone_offset)
            
            # 获取当前时间
            now = datetime.datetime.now(tz)
            
            # 格式化时间
            time_format = "%Y-%m-%d %H:%M:%S"
            formatted_time = now.strftime(time_format)
            
            # 获取时区信息
            if tz == datetime.timezone.utc:
                tz_name = "UTC"
            else:
                # 计算时区偏移
                offset = tz.utcoffset(now)
                if offset:
                    total_seconds = int(offset.total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    sign = '+' if hours >= 0 else '-'
                    tz_name = f"UTC{sign}{abs(hours):02d}:{minutes:02d}"
                else:
                    tz_name = "UTC"
            
            # 获取星期几
            weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
            weekday = weekdays[now.weekday()]
            
            # 获取月份名称
            months = ["一月", "二月", "三月", "四月", "五月", "六月", 
                     "七月", "八月", "九月", "十月", "十一月", "十二月"]
            month_name = months[now.month - 1]
            
            # 构建详细的时间信息
            time_info = {
                "formatted_time": formatted_time,
                "timezone": tz_name,
                "weekday": weekday,
                "year": now.year,
                "month": now.month,
                "month_name": month_name,
                "day": now.day,
                "hour": now.hour,
                "minute": now.minute,
                "second": now.second,
                "timestamp": int(now.timestamp()),
            }
            
            # 生成友好的输出
            if timezone_offset:
                # 尝试查找城市名称
                city_name = None
                for city, offset in self.city_to_offset.items():
                    if offset == timezone_offset:
                        city_name = city
                        break
                
                if city_name:
                    output = f"{city_name.title()} 的当前时间是：{formatted_time} ({tz_name})\n{weekday}, {now.year}年{month_name}{now.day}日"
                else:
                    output = f"时区 {timezone_offset} 的当前时间是：{formatted_time} ({tz_name})\n{weekday}, {now.year}年{month_name}{now.day}日"
            else:
                output = f"当前本地时间是：{formatted_time} ({tz_name})\n{weekday}, {now.year}年{month_name}{now.day}日"
            
            return SkillResult(
                success=True,
                content=output,
                tool_call_id=kwargs.get("tool_call_id", "")
            )
            
        except Exception as e:
            error_msg = f"获取时间失败: {str(e)}"
            return SkillResult(
                success=False,
                content=error_msg,
                tool_call_id=kwargs.get("tool_call_id", "")
            )
