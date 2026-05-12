# 创建 Skill 的格式和步骤总结

## 一、Skill 文件结构

### 1. 基本模板
```python
"""
技能描述
"""
import os
import json
from typing import Dict, Any
from .skill_base import SkillBase, SkillResult

class 技能名称(SkillBase):
    """技能类文档字符串"""
    
    def __init__(self):
        super().__init__(
            name="技能名称",  # 必须与类名一致
            description="技能功能描述"
        )
        # 参数定义（JSON Schema格式）
        self.parameters = {
            "type": "object",
            "properties": {
                "参数1": {
                    "type": "string",  # 类型：string, number, boolean, array, object
                    "description": "参数描述"
                },
                # 更多参数...
            }
        }
        # 必需参数列表
        self.required = ["参数1"]
        
        # 初始化其他属性
        self.数据目录 = "data"
        os.makedirs(self.数据目录, exist_ok=True)
    
    def execute(self, **kwargs) -> SkillResult:
        """执行技能的核心方法"""
        # 1. 参数验证
        if not self.validate_params(**kwargs):
            return SkillResult(
                success=False,
                content=f"缺少必需参数。必需参数: {self.required}"
            )
        
        # 2. 提取参数
        参数1 = kwargs.get("参数1")
        
        try:
            # 3. 执行业务逻辑
            result = self._执行具体操作(参数1)
            
            # 4. 返回成功结果
            return SkillResult(
                success=True,
                content=result
            )
        except Exception as e:
            # 5. 返回错误结果
            return SkillResult(
                success=False,
                content=f"操作失败: {str(e)}"
            )
    
    def _执行具体操作(self, 参数):
        """私有方法，实现具体业务逻辑"""
        # 实现细节
        pass
```

## 二、创建步骤

### 步骤1：设计技能接口
1. **确定技能名称**：使用小写字母和下划线，如 `document_manager`
2. **定义功能描述**：清晰说明技能用途，AI 会根据描述决定是否调用
3. **设计参数**：
   - 必需参数：用户必须提供的参数
   - 可选参数：有默认值或可选的参数
   - 参数类型：必须使用 JSON Schema 类型（string, number, boolean, array, object）

### 步骤2：创建技能文件
1. **文件位置**：`skill/技能名称.py`
2. **导入基类**：`from .skill_base import SkillBase, SkillResult`
3. **定义类**：类名与技能名称一致，继承 `SkillBase`
4. **实现 `__init__` 方法**：设置名称、描述、参数
5. **实现 `execute` 方法**：核心业务逻辑

### 步骤3：实现业务逻辑
1. **参数验证**：使用 `self.validate_params(**kwargs)`
2. **错误处理**：使用 try-except 捕获异常
3. **返回结果**：使用 `SkillResult(success, content)`
4. **私有方法**：复杂的逻辑拆分为私有方法

### 步骤4：集成到系统
1. **修改 `skill/__init__.py`**：
   ```python
   try:
       from .技能名称 import 技能类名
   except ImportError:
       技能类名 = None
   
   # 在 register_all_skills() 中添加注册
   if 技能类名:
       registry.register(技能类名)
   ```
2. **更新 `__all__` 列表**：添加技能类名

### 步骤5：测试技能
1. **创建测试脚本**：验证所有功能
2. **测试用例**：
   - 正常情况测试
   - 参数缺失测试
   - 错误处理测试
   - 边界条件测试
3. **集成测试**：在主程序中测试技能调用

## 三、关键注意事项

### 1. 参数定义规范
```python
self.parameters = {
    "type": "object",
    "properties": {
        "action": {
            "type": "string",
            "description": "操作描述",
            "enum": ["create", "read"]  # 可选：枚举值限制
        },
        "title": {
            "type": "string",
            "description": "文档标题"
        },
        "count": {
            "type": "number",
            "description": "数量"
        },
        "enabled": {
            "type": "boolean",
            "description": "是否启用"
        }
    }
}
```

### 2. 错误处理最佳实践
```python
def execute(self, **kwargs) -> SkillResult:
    # 参数验证
    if not self.validate_params(**kwargs):
        return SkillResult(success=False, content="参数错误")
    
    try:
        # 业务逻辑
        result = self._process(**kwargs)
        return SkillResult(success=True, content=result)
    except ValueError as e:
        return SkillResult(success=False, content=f"输入错误: {str(e)}")
    except Exception as e:
        return SkillResult(success=False, content=f"系统错误: {str(e)}")
```

### 3. 技能设计原则
1. **单一职责**：一个技能只做一件事
2. **明确接口**：参数和返回值清晰明确
3. **错误友好**：错误信息对用户友好
4. **资源管理**：妥善管理文件、网络连接等资源
5. **线程安全**：考虑并发调用情况

## 四、示例参考
- 天气查询：`skill/get_weather_by_city.py`
- 时间获取：`skill/get_local_time.py`
- 对话历史：`skill/get_chat_history.py`
- Token计数：`skill/token_counter.py`
- 文档管理：`skill/document_manager.py`（刚刚创建）

## 五、常见问题解决

### 1. 技能未注册
- 检查 `skill/__init__.py` 中的导入和注册代码
- 确保技能类名正确

### 2. 参数验证失败
- 检查 `self.required` 列表是否正确
- 确保参数类型与 JSON Schema 一致（使用 `"string"` 而不是 `"str"`）

### 3. AI 不调用技能
- 检查技能描述是否清晰明确
- 确保参数设计合理，AI 能理解何时调用

### 4. 技能执行错误
- 添加详细的错误日志
- 使用 try-except 捕获所有异常
- 返回用户友好的错误信息

## 六、快速开始模板

```python
"""
{技能名称} - {功能简介}
"""
import os
from typing import Dict, Any
from .skill_base import SkillBase, SkillResult

class {技能类名}(SkillBase):
    """{详细功能描述}"""
    
    def __init__(self):
        super().__init__(
            name="{技能名称}",
            description="{技能功能描述，AI会根据这个描述决定是否调用}"
        )
        self.parameters = {
            "type": "object",
            "properties": {
                "param1": {
                    "type": "string",
                    "description": "参数1描述"
                }
            }
        }
        self.required = ["param1"]
    
    def execute(self, **kwargs) -> SkillResult:
        """执行{技能名称}"""
        if not self.validate_params(**kwargs):
            return SkillResult(
                success=False,
                content=f"缺少必需参数。必需参数: {self.required}"
            )
        
        param1 = kwargs.get("param1")
        
        try:
            # 实现业务逻辑
            result = f"处理结果: {param1}"
            return SkillResult(success=True, content=result)
        except Exception as e:
            return SkillResult(success=False, content=f"执行失败: {str(e)}")
```

通过以上格式和步骤，可以快速创建符合 Agent SKILL 系统规范的新技能。