import requests
from .skill_base import SkillBase, SkillResult

# 定义工具函数：获取当前温度
class get_weather_by_city(SkillBase):
    def __init__(self):
        super().__init__(
            name="get_weather_by_city",
            description="获取所提供城市的天气。"
        )
        self.parameters = {
            "type": "object",
            "properties": {
                "city": {"type": "string"}
            }
        }
        self.required = ["city"]

    def execute(self, **kwargs) -> SkillResult:
        # 验证参数
        if not self.validate_params(**kwargs):
            return SkillResult(
                success=False,
                content=f"缺少必需参数。必需参数: {self.required}"
            )
        
        city_name = kwargs.get("city")
        
        url = f"https://uapis.cn/api/v1/misc/weather?city={city_name}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # 检查HTTP错误
            data = response.json()
            # temperature = data['current']['temperature_2m']
            return SkillResult(
                success=True,
                content=str(data)
            )
        except requests.exceptions.RequestException as e:
            return SkillResult(
                success=False,
                content=f"获取天气数据失败: {e}"
            )
        except KeyError:
            return SkillResult(
                success=False,
                content="错误: 天气数据格式无效"
            )
        