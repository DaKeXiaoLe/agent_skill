#!/usr/bin/env python3
"""
Agent SKILL项目 - 终端交互式智能体
支持命令：/help, /exit, /skills, /clear, /history
对话消息自动保存到JSON文件，每次开启新对话
"""

import json
import os
import sys
import re
from datetime import datetime
from typing import Optional, List, Dict, Any

from skill import registry
from openai import OpenAI
from skill.token_counter import get_usage_percentage, add_to_session


class SkillAgent:
    """技能智能体 - 终端交互式AI助手"""
    
    def __init__(self):
        # 初始化OpenAI客户端（混元API）
        self.model = "deepseek-chat"
        self.client = OpenAI(
            api_key="sk-**********************",
            base_url="https://api.deepseek.com",
            )
        
        # 从注册表获取技能定义
        self.tools = registry.get_skills_dict()
        
        # 对话历史目录
        self.conversations_dir = "conversations"
        os.makedirs(self.conversations_dir, exist_ok=True)
        
        # 生成基于时间戳的会话ID（每次启动都是新对话）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_id = f"session_{timestamp}"
        
        # 会话文件路径
        self.session_file = os.path.join(self.conversations_dir, f"{self.session_id}.json")
        
        # 初始化空的对话历史（每次都是新对话）
        self.messages: List[Dict[str, Any]] = []
        
        prompt = [
            "你是一个有用的助手，可以调用工具来帮助回答问题。请用自然语言回答用户，不要输出任何内部标记（如<|Plan|>、<||Thought|>、<||Action|>等）。",
            "历史对话路径为：conversations。",
            "待办事宜路径为：documents/待办事宜.json",
            "笔记本路径为：documents/笔记本.json"
            "技能文件和注册文件都路径：skill",
            "skill创建文档为：skill/creat_skill.md",
            "个人信息文档为：documents/个人信息.md"
        ]

        # 使用 join() 将列表连接成字符串，用换行符分隔
        prompt_str = '\n'.join(prompt)

        # 添加系统提示
        system_prompt = {
            "role": "system",
            "content": prompt_str
}
        self.messages.append(system_prompt)
        
        # 保存初始会话信息
        self._save_messages()
        
        # 命令处理器映射
        self.command_handlers = {
            "/help": self.cmd_help,
            "/h": self.cmd_help,
            "/exit": self.cmd_exit,
            "/quit": self.cmd_exit,
            "/q": self.cmd_exit,
            "/skills": self.cmd_skills,
            "/clear": self.cmd_clear,
            "/history": self.cmd_history,
            "/reset": self.cmd_reset,
        }
        
        # 运行标志
        self.running = True
    
    def _save_messages(self):
        """保存对话消息到JSON文件"""
        try:
            session_data = {
                "session_id": self.session_id,
                "created_at": datetime.now().isoformat(),
                "messages": self.messages,
                "message_count": len(self.messages)
            }
            
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"⚠️  保存对话失败: {e}")
            return False
    
    def _add_message_and_save(self, message: Dict[str, Any]):
        """添加消息并自动保存"""
        self.messages.append(message)
        self._save_messages()
    
    def _extract_natural_response(self, ai_response: str) -> str:
        """
        从AI回复中提取自然语言回答
        处理包含<|Plan|>、<|Thought|>、<|Action|>等标记的情况
        """
        if not ai_response:
            return ""
        
        # 如果回复已经是自然语言，直接返回
        if not re.search(r'<\|.*?\|>', ai_response):
            return ai_response
        
        # 尝试提取READY_ANS之后的内容
        ready_ans_match = re.search(r'<\|Action\|>READY_ANS</\|Action\|>(.*)', ai_response, re.DOTALL)
        if ready_ans_match:
            extracted = ready_ans_match.group(1).strip()
            if extracted:
                return extracted
        
        # 如果提取失败，尝试移除所有标记
        cleaned = re.sub(r'<\|.*?\|>', '', ai_response)
        cleaned = re.sub(r'^Planner:\s*', '', cleaned, flags=re.IGNORECASE)
        cleaned = cleaned.strip()
        
        if cleaned:
            return cleaned
        
        # 如果还是空，返回原始回复
        return ai_response
    
    def print_banner(self):
        """打印欢迎横幅"""
        print("=" * 60)
        print(f"🤖 {self.model} 智能体 v1.0")
        print("=" * 60)
        print(f"会话ID: {self.session_id}")
        print(f"已加载 {len(self.tools)} 个可用技能")
        print("输入 /help /h 查看可用命令")
        print("输入普通文本与AI对话")
        print(f"对话将保存到: {self.session_file}")
        print("=" * 60)
    
    def cmd_help(self, args: List[str]) -> bool:
        """显示帮助信息"""
        print("\n📖 可用命令：")
        print("  /help, /h      - 显示此帮助信息")
        print("  /exit, /quit, /q - 退出程序")
        print("  /skills        - 显示所有可用技能")
        print("  /clear         - 清除当前对话历史")
        print("  /history       - 显示对话历史")
        print("  /reset         - 重置对话（清空历史）")
        print("\n💡 提示：")
        print("  - 直接输入文本与AI进行对话")
        print("  - AI可以调用技能技能来回答问题")
        print("  - 对话自动保存到JSON文件")
        print("  - 每次启动都是新的对话会话")
        return True
    
    def cmd_exit(self, args: List[str]) -> bool:
        """退出程序"""
        # 退出前保存最后的状态
        self._save_messages()
        print(f"👋 再见！对话已保存到: {self.session_file}")
        self.running = False
        return False
    
    def cmd_skills(self, args: List[str]) -> bool:
        """显示所有可用技能"""
        print("\n🛠️  可用技能：")
        skills = registry.list_skills()
        if skills:
            for i, skill_info in enumerate(skills, 1):
                print(f"  [{i}] {skill_info.get('name', '未知')}")
                print(f"     描述: {skill_info.get('description', '无描述')}")
        else:
            print("  (暂无注册技能)")
        
    def cmd_clear(self, args: List[str]) -> bool:
        """清除当前对话历史"""
        # 保留系统消息
        system_message = None
        if self.messages and self.messages[0].get("role") == "system":
            system_message = self.messages[0]
        
        self.messages = []
        
        # 重新添加系统消息
        if system_message:
            self.messages.append(system_message)
        
        self._save_messages()
        print("🗑️  对话历史已清除并保存（系统消息保留）")
        return True
    
    def cmd_history(self, args: List[str]) -> bool:
        """显示对话历史"""
        if not self.messages:
            print("📝 对话历史为空")
            return True
        
        print(f"\n📝 当前会话对话历史（{len(self.messages)}条消息）：")
        print(f"会话文件: {self.session_file}")
        for i, msg in enumerate(self.messages, 1):
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            tool_calls = msg.get("tool_calls")
            
            if role == "system":
                # 系统消息可以简短显示
                print(f"  [{i}] ⚙️  系统: [系统提示]")
            elif role == "user":
                print(f"  [{i}] 👤 用户: {content}")
            elif role == "assistant":
                if tool_calls:
                    print(f"  [{i}] 🤖 AI: [调用了技能]")
                    for tool_call in tool_calls:
                        func = tool_call.get("function", {})
                        print(f"      技能: {func.get('name')}({func.get('arguments')})")
                else:
                    # 简化显示，如果内容太长
                    if content and len(content) > 100:
                        print(f"  [{i}] 🤖 AI: {content[:100]}...")
                    else:
                        print(f"  [{i}] 🤖 AI: {content}")
            elif role == "tool":
                # 工具结果可能很长，只显示开头
                if content and len(content) > 100:
                    print(f"  [{i}] 🛠️  技能结果: {content[:100]}...")
                else:
                    print(f"  [{i}] 🛠️  技能结果: {content}")
        return True
    
    def cmd_reset(self, args: List[str]) -> bool:
        """重置对话"""
        # 保留系统消息
        system_message = None
        if self.messages and self.messages[0].get("role") == "system":
            system_message = self.messages[0]
        
        self.messages = []
        
        # 重新添加系统消息
        if system_message:
            self.messages.append(system_message)
        
        self._save_messages()
        print("🔄 对话已重置并保存（系统消息保留）")
        return True
    
    def process_command(self, input_text: str) -> bool:
        """处理命令输入"""
        parts = input_text.strip().split()
        if not parts:
            return True
        
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        if cmd in self.command_handlers:
            return self.command_handlers[cmd](args)
        else:
            print(f"❌ 未知命令: {cmd}")
            print("  输入 /help 查看可用命令")
            return True
    
    def process_ai_query(self, user_input: str):
        """处理AI查询"""
        # 添加用户消息到历史并保存
        user_message = {"role": "user", "content": user_input}
        self._add_message_and_save(user_message)
        
        # 添加用户输入的 token 计数
        add_to_session(user_input, self.session_id)
        
        print(f"\n💭 思考中...")
        
        try:
            # 调用AI
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                tools=self.tools,
            )
            response_message = completion.choices[0].message
            if response_message.content:
                result_message = {
                            "role": "assistant",
                            "content": response_message.content
                        }

                # 获取当前会话的 token 使用百分比
                percentage = int(get_usage_percentage(self.session_id))
                print(f"\n🤖 AI[{percentage}%]: {response_message.content}")
                self._add_message_and_save(result_message)
            while(response_message.tool_calls):
                # 检查是否有技能调用
                if response_message.tool_calls:
                    print("\n🔧 AI决定使用技能...")
                    
                    # 收集技能调用信息
                    tool_call_list = []
                    for tool_call in response_message.tool_calls:
                        tool_name = tool_call.function.name
                        tool_args = json.loads(tool_call.function.arguments)
                        tool_call_list.append((tool_name, tool_args, tool_call.id))
                    
                    # 显示技能调用清单
                    print("\n📋 技能调用清单：")
                    for tool_name, tool_args, _ in tool_call_list:
                        print(f"   🛠️  {tool_name}")
                    
                    # 将AI的技能调用消息转换为可序列化的字典并保存
                    response_dict = {
                        "role": response_message.role,
                        "content": response_message.content,
                        "tool_calls": []
                    }
                    
                    if response_message.tool_calls:
                        for tool_call in response_message.tool_calls:
                            tool_call_dict = {
                                "id": tool_call.id,
                                "type": tool_call.type,
                                "function": {
                                    "name": tool_call.function.name,
                                    "arguments": tool_call.function.arguments
                                }
                            }
                            response_dict["tool_calls"].append(tool_call_dict)
                    
                    self._add_message_and_save(response_dict)
                    
                    # 处理每个技能调用
                    tool_results = []  # 保存所有工具调用结果
                    for tool_name, tool_args, tool_call_id in tool_call_list:
                        print(f"\n⚡ 执行技能: {tool_name}",end="")
                        
                        # 执行对应的技能
                        skill_instance = registry.create_skill(tool_name)
                        if skill_instance:
                            # 执行技能
                            result = skill_instance.execute(**tool_args)
                            
                            # 保存工具结果
                            tool_results.append({
                                "tool_name": tool_name,
                                "tool_args": tool_args,
                                "tool_call_id": tool_call_id,
                                "result": result.content if result.success else f"错误: {result.content}"
                            })
                            
                            # 将技能执行结果添加到消息历史并保存
                            tool_result_message = {
                                "role": "tool",
                                "tool_call_id": tool_call_id,
                                "content": result.content if result.success else f"错误: {result.content}"
                            }
                            self._add_message_and_save(tool_result_message)
                            
                            status = "  ✅" if result.success else "❌"
                            print(f"{status} ")
                        else:
                            error_msg = f"错误: 未找到技能 '{tool_name}'"
                            tool_result_message = {
                                "role": "tool",
                                "tool_call_id": tool_call_id,
                                "content": error_msg
                            }
                            self._add_message_and_save(tool_result_message)
                            print(f"❌ {error_msg}")
                    
                    # 获取AI的最终回答
                    print("\n💭 思考中...")
                    completion_2 = self.client.chat.completions.create(
                        model=self.model,
                        messages=self.messages,
                        tools=self.tools,
                    )
                    
                    response_message = completion_2.choices[0].message
                    if response_message.content:
                        result_message = {
                                    "role": "assistant",
                                    "content": response_message.content
                                }

                        # 获取当前会话的 token 使用百分比
                        percentage = int(get_usage_percentage(self.session_id))
                        print(f"\n🤖 AI[{percentage}%]: {response_message.content}")
                        self._add_message_and_save(result_message)
                
                
                
                
        except Exception as e:
            error_msg = f"AI查询出错: {str(e)}"
            print(f"❌ {error_msg}")
            error_message = {"role": "assistant", "content": error_msg}
            self._add_message_and_save(error_message)
    
    def run(self):
        """运行交互式终端"""
        self.print_banner()
        
        while self.running:
            try:
                # 获取用户输入
                user_input = input("\n💬 > ").strip()
                
                if not user_input:
                    continue
                
                # 检查是否是命令
                if user_input.startswith("/"):
                    self.process_command(user_input)
                else:
                    # 处理AI查询
                    self.process_ai_query(user_input)
                    
            except KeyboardInterrupt:
                print("\n\n⚠️  中断请求，输入 /exit 退出")
                continue
            except EOFError:
                print("\n")
                self.cmd_exit([])
                break
            except Exception as e:
                print(f"❌ 错误: {str(e)}")


def main():
    """主函数"""
    agent = SkillAgent()
    agent.run()


if __name__ == "__main__":
    main()