"""
文件管理技能 - 创建、读取、更新和删除任意类型的文件
"""
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional, Union
from .skill_base import SkillBase, SkillResult


class document_manager(SkillBase):
    """文件管理技能，支持创建、读取、更新和删除任意类型的文件"""
    
    def __init__(self):
        super().__init__(
            name="document_manager",
            description="管理任意类型的文件：创建新文件、读取现有文件内容、更新文件内容或删除文件。使用'path'参数指定文件路径，'content'参数提供文件内容（用于创建或更新）。"
        )
        self.parameters = {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "文件路径（如'documents/information.md'、'data/config.json'、'scripts/test.py'等），支持任意文件扩展名"
                },
                "content": {
                    "type": "string",
                    "description": "文件内容（用于创建或更新文件）。对于文本文件，直接写入内容；对于二进制文件，应提供base64编码的内容"
                },
                "mode": {
                    "type": "string",
                    "description": "文件打开模式（可选）：'text'（默认，文本模式）、'binary'（二进制模式）、'append'（追加模式）",
                    "enum": ["text", "binary", "append"]
                },
                "encoding": {
                    "type": "string",
                    "description": "文件编码（可选，仅文本模式有效），默认'utf-8'"
                }
            }
        }
        self.required = ["path"]
        
        # 默认文档存储目录
        self.documents_dir = "documents"
        os.makedirs(self.documents_dir, exist_ok=True)
    
    def _ensure_directory_exists(self, path: str) -> None:
        """确保文件所在目录存在"""
        dir_path = os.path.dirname(path)
        if dir_path:  # 如果路径包含目录部分
            os.makedirs(dir_path, exist_ok=True)
    
    def _write_file(self, path: str, content: str, mode: str = "text", encoding: str = "utf-8") -> SkillResult:
        """写入文件（支持文本和二进制模式）"""
        try:
            self._ensure_directory_exists(path)
            
            if mode == "binary":
                # 二进制模式：假设content是base64编码的字符串
                import base64
                binary_data = base64.b64decode(content)
                with open(path, 'wb') as f:
                    f.write(binary_data)
                return SkillResult(
                    success=True,
                    content=f"二进制文件 '{path}' 写入成功"
                )
            elif mode == "append":
                # 追加模式
                with open(path, 'a', encoding=encoding) as f:
                    f.write(content)
                return SkillResult(
                    success=True,
                    content=f"内容已追加到文件 '{path}'"
                )
            else:
                # 文本模式（默认）
                with open(path, 'w', encoding=encoding) as f:
                    f.write(content)
                return SkillResult(
                    success=True,
                    content=f"文本文件 '{path}' 写入成功"
                )
        except Exception as e:
            return SkillResult(
                success=False,
                content=f"写入文件失败: {str(e)}"
            )
    
    def _read_file(self, path: str, mode: str = "text", encoding: str = "utf-8") -> SkillResult:
        """读取文件（支持文本和二进制模式）"""
        try:
            if not os.path.exists(path):
                return SkillResult(
                    success=False,
                    content=f"文件 '{path}' 不存在"
                )
            
            if mode == "binary":
                # 二进制模式：返回base64编码的内容
                import base64
                with open(path, 'rb') as f:
                    binary_data = f.read()
                content_base64 = base64.b64encode(binary_data).decode('utf-8')
                return SkillResult(
                    success=True,
                    content=content_base64
                )
            else:
                # 文本模式
                with open(path, 'r', encoding=encoding) as f:
                    content = f.read()
                return SkillResult(
                    success=True,
                    content=content
                )
        except UnicodeDecodeError:
            # 如果文本解码失败，尝试其他编码或建议使用二进制模式
            return SkillResult(
                success=False,
                content=f"文件 '{path}' 无法用 '{encoding}' 编码读取。请尝试使用 mode='binary' 参数以二进制模式读取。"
            )
        except Exception as e:
            return SkillResult(
                success=False,
                content=f"读取文件失败: {str(e)}"
            )
    
    def _delete_file(self, path: str) -> SkillResult:
        """删除文件"""
        try:
            if not os.path.exists(path):
                return SkillResult(
                    success=False,
                    content=f"文件 '{path}' 不存在，无法删除"
                )
            
            os.remove(path)
            return SkillResult(
                success=True,
                content=f"文件 '{path}' 已成功删除"
            )
        except Exception as e:
            return SkillResult(
                success=False,
                content=f"删除文件失败: {str(e)}"
            )
    
    def _list_files(self, directory: str = None, pattern: str = "*") -> SkillResult:
        """列出目录中的文件"""
        try:
            if directory is None:
                directory = self.documents_dir
            
            if not os.path.exists(directory):
                return SkillResult(
                    success=False,
                    content=f"目录 '{directory}' 不存在"
                )
            
            import fnmatch
            files = []
            for root, dirs, filenames in os.walk(directory):
                for filename in filenames:
                    if fnmatch.fnmatch(filename, pattern):
                        full_path = os.path.join(root, filename)
                        rel_path = os.path.relpath(full_path, directory)
                        file_stat = os.stat(full_path)
                        files.append({
                            "name": filename,
                            "path": rel_path,
                            "full_path": full_path,
                            "size": file_stat.st_size,
                            "modified": datetime.fromtimestamp(file_stat.st_mtime).isoformat()
                        })
            
            return SkillResult(
                success=True,
                content=json.dumps({"files": files}, ensure_ascii=False, indent=2)
            )
        except Exception as e:
            return SkillResult(
                success=False,
                content=f"列出文件失败: {str(e)}"
            )
    
    def execute(self, **kwargs) -> SkillResult:
        """执行文件管理操作"""
        # 验证参数
        if not self.validate_params(**kwargs):
            return SkillResult(
                success=False,
                content=f"缺少必需参数。必需参数: {self.required}"
            )
        
        path = kwargs.get("path")
        content = kwargs.get("content")
        mode = kwargs.get("mode", "text")
        encoding = kwargs.get("encoding", "utf-8")
        
        # 如果提供了content，则写入文件（创建或更新）
        if content is not None:
            return self._write_file(path, content, mode, encoding)
        else:
            # 如果没有提供content，则读取文件
            return self._read_file(path, mode, encoding)
    
    # 向后兼容的别名方法
    def _read_by_path(self, path: str) -> SkillResult:
        """根据路径读取文件（向后兼容）"""
        return self._read_file(path)
    
    def _delete_by_path(self, path: str) -> SkillResult:
        """根据路径删除文件（向后兼容）"""
        return self._delete_file(path)
