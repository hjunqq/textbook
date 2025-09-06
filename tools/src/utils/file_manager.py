"""
文件管理器模块
提供文件操作的封装
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional, Dict, Any
from .logger import Logger

class FileManager:
    """文件管理器"""
    
    def __init__(self):
        self.logger = Logger("FileManager")
    
    def read_file(self, file_path: Path) -> str:
        """读取文件内容"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.logger.info(f"读取文件成功: {file_path} ({len(content)} 字符)")
            return content
            
        except FileNotFoundError:
            self.logger.error(f"文件不存在: {file_path}")
            raise
        except UnicodeDecodeError as e:
            self.logger.error(f"文件编码错误: {file_path}, {e}")
            # 尝试其他编码
            try:
                with open(file_path, 'r', encoding='gbk') as f:
                    content = f.read()
                self.logger.warning(f"使用GBK编码读取文件: {file_path}")
                return content
            except:
                raise e
        except Exception as e:
            self.logger.error(f"读取文件失败: {file_path}, {e}")
            raise
    
    def write_file(self, file_path: Path, content: str) -> None:
        """写入文件"""
        try:
            # 确保目录存在
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.info(f"写入文件成功: {file_path} ({len(content)} 字符)")
            
        except Exception as e:
            self.logger.error(f"写入文件失败: {file_path}, {e}")
            raise
    
    def copy_file(self, source: Path, dest: Path) -> None:
        """复制文件"""
        try:
            # 确保目标目录存在
            dest.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(source, dest)
            self.logger.info(f"复制文件成功: {source} -> {dest}")
            
        except Exception as e:
            self.logger.error(f"复制文件失败: {source} -> {dest}, {e}")
            raise
    
    def move_file(self, source: Path, dest: Path) -> None:
        """移动文件"""
        try:
            # 确保目标目录存在
            dest.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.move(str(source), str(dest))
            self.logger.info(f"移动文件成功: {source} -> {dest}")
            
        except Exception as e:
            self.logger.error(f"移动文件失败: {source} -> {dest}, {e}")
            raise
    
    def delete_file(self, file_path: Path) -> None:
        """删除文件"""
        try:
            if file_path.exists():
                file_path.unlink()
                self.logger.info(f"删除文件成功: {file_path}")
            else:
                self.logger.warning(f"文件不存在，无法删除: {file_path}")
                
        except Exception as e:
            self.logger.error(f"删除文件失败: {file_path}, {e}")
            raise
    
    def ensure_directory(self, dir_path: Path) -> None:
        """确保目录存在"""
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"确保目录存在: {dir_path}")
            
        except Exception as e:
            self.logger.error(f"创建目录失败: {dir_path}, {e}")
            raise
    
    def copy_directory(self, source_dir: Path, dest_dir: Path, 
                      ignore_patterns: Optional[List[str]] = None) -> None:
        """复制目录"""
        try:
            if ignore_patterns:
                ignore = shutil.ignore_patterns(*ignore_patterns)
            else:
                ignore = None
            
            if dest_dir.exists():
                shutil.rmtree(dest_dir)
            
            shutil.copytree(source_dir, dest_dir, ignore=ignore)
            self.logger.info(f"复制目录成功: {source_dir} -> {dest_dir}")
            
        except Exception as e:
            self.logger.error(f"复制目录失败: {source_dir} -> {dest_dir}, {e}")
            raise
    
    def find_files(self, directory: Path, pattern: str = "*", 
                   recursive: bool = True) -> List[Path]:
        """查找文件"""
        try:
            if not directory.exists():
                self.logger.warning(f"目录不存在: {directory}")
                return []
            
            if recursive:
                files = list(directory.rglob(pattern))
            else:
                files = list(directory.glob(pattern))
            
            # 只返回文件，不包括目录
            files = [f for f in files if f.is_file()]
            
            self.logger.info(f"找到 {len(files)} 个文件，模式: {pattern}")
            return files
            
        except Exception as e:
            self.logger.error(f"查找文件失败: {directory}, 模式: {pattern}, {e}")
            raise
    
    def get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """获取文件信息"""
        try:
            if not file_path.exists():
                return {"exists": False}
            
            stat = file_path.stat()
            
            info = {
                "exists": True,
                "name": file_path.name,
                "size": stat.st_size,
                "modified": stat.st_mtime,
                "is_file": file_path.is_file(),
                "is_directory": file_path.is_dir(),
                "extension": file_path.suffix,
                "absolute_path": str(file_path.absolute())
            }
            
            return info
            
        except Exception as e:
            self.logger.error(f"获取文件信息失败: {file_path}, {e}")
            raise
    
    def clean_directory(self, directory: Path, keep_structure: bool = True) -> None:
        """清理目录"""
        try:
            if not directory.exists():
                self.logger.warning(f"目录不存在: {directory}")
                return
            
            if keep_structure:
                # 只删除文件，保持目录结构
                for item in directory.rglob("*"):
                    if item.is_file():
                        item.unlink()
                self.logger.info(f"清理目录内容: {directory} (保持结构)")
            else:
                # 删除整个目录内容
                for item in directory.iterdir():
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)
                self.logger.info(f"清理目录内容: {directory} (完全清理)")
            
        except Exception as e:
            self.logger.error(f"清理目录失败: {directory}, {e}")
            raise
    
    def backup_file(self, file_path: Path, backup_dir: Optional[Path] = None) -> Path:
        """备份文件"""
        try:
            if not file_path.exists():
                raise FileNotFoundError(f"文件不存在: {file_path}")
            
            if backup_dir is None:
                backup_dir = file_path.parent / "backup"
            
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # 生成备份文件名（带时间戳）
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
            backup_path = backup_dir / backup_name
            
            self.copy_file(file_path, backup_path)
            self.logger.info(f"文件备份成功: {file_path} -> {backup_path}")
            
            return backup_path
            
        except Exception as e:
            self.logger.error(f"文件备份失败: {file_path}, {e}")
            raise

class ResourceManager:
    """资源管理器 - 管理图片、字体等资源文件"""
    
    def __init__(self, source_dir: Path, output_dir: Path):
        self.source_dir = source_dir
        self.output_dir = output_dir
        self.file_manager = FileManager()
        self.logger = Logger("ResourceManager")
    
    def copy_images(self) -> List[Path]:
        """复制图片资源"""
        image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.pdf']
        copied_files = []
        
        try:
            # 查找所有图片文件
            for ext in image_extensions:
                image_files = self.file_manager.find_files(
                    self.source_dir, f"*{ext}", recursive=True
                )
                
                for image_file in image_files:
                    # 计算相对路径
                    relative_path = image_file.relative_to(self.source_dir)
                    dest_path = self.output_dir / "images" / relative_path
                    
                    # 复制图片
                    self.file_manager.copy_file(image_file, dest_path)
                    copied_files.append(dest_path)
            
            self.logger.info(f"复制了 {len(copied_files)} 个图片文件")
            return copied_files
            
        except Exception as e:
            self.logger.error(f"复制图片失败: {e}")
            raise
    
    def optimize_images(self, max_width: int = 1920, quality: int = 85) -> None:
        """优化图片（需要Pillow库）"""
        try:
            from PIL import Image
            
            image_dir = self.output_dir / "images"
            if not image_dir.exists():
                return
            
            image_files = self.file_manager.find_files(image_dir, "*.jpg") + \
                         self.file_manager.find_files(image_dir, "*.png")
            
            optimized_count = 0
            for image_file in image_files:
                try:
                    with Image.open(image_file) as img:
                        # 如果图片宽度超过最大宽度，则缩放
                        if img.width > max_width:
                            ratio = max_width / img.width
                            new_height = int(img.height * ratio)
                            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
                        
                        # 保存优化后的图片
                        if image_file.suffix.lower() in ['.jpg', '.jpeg']:
                            img.save(image_file, 'JPEG', quality=quality, optimize=True)
                        elif image_file.suffix.lower() == '.png':
                            img.save(image_file, 'PNG', optimize=True)
                        
                        optimized_count += 1
                        
                except Exception as e:
                    self.logger.warning(f"优化图片失败: {image_file}, {e}")
            
            self.logger.info(f"优化了 {optimized_count} 个图片文件")
            
        except ImportError:
            self.logger.warning("未安装Pillow库，跳过图片优化")
        except Exception as e:
            self.logger.error(f"图片优化失败: {e}")
    
    def validate_resources(self) -> Dict[str, Any]:
        """验证资源文件完整性"""
        validation_result = {
            "total_images": 0,
            "missing_images": [],
            "broken_images": [],
            "large_images": []  # 大于5MB的图片
        }
        
        try:
            image_dir = self.output_dir / "images"
            if image_dir.exists():
                image_files = self.file_manager.find_files(
                    image_dir, "*", recursive=True
                )
                
                validation_result["total_images"] = len(image_files)
                
                for image_file in image_files:
                    # 检查文件大小
                    file_size = image_file.stat().st_size
                    if file_size > 5 * 1024 * 1024:  # 5MB
                        validation_result["large_images"].append({
                            "path": str(image_file),
                            "size_mb": round(file_size / (1024 * 1024), 2)
                        })
                    
                    # 检查图片是否可以正常读取（如果有Pillow）
                    try:
                        from PIL import Image
                        with Image.open(image_file) as img:
                            img.verify()
                    except ImportError:
                        pass  # 没有Pillow库，跳过验证
                    except Exception:
                        validation_result["broken_images"].append(str(image_file))
            
            self.logger.info(f"资源验证完成: {validation_result['total_images']} 个文件")
            return validation_result
            
        except Exception as e:
            self.logger.error(f"资源验证失败: {e}")
            raise