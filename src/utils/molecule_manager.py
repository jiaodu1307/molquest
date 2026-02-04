import json
import os
import yaml
from typing import List, Optional
from src.utils.molecule_types import MoleculeData
from src.core.logger import logger

class MoleculeManager:
    """
    分子数据管理器类。
    
    负责从 JSON 文件加载分子数据，并提供查询接口。
    实现了单例模式或者是作为全局对象被调用，确保数据只加载一次。
    """
    
    def __init__(self, data_path: Optional[str] = None):
        """
        初始化管理器。
        
        Args:
            data_path (str, optional): 分子数据 JSON 文件的相对或绝对路径。
                                     如果不提供，按照以下优先级查找：
                                     1. config/settings.yaml 中的 data_path
                                     2. 默认值 "data/processed/molecules.json"
        """
        if data_path is None:
            data_path = os.getenv("MOLECULE_DATA_PATH")

            if not data_path:
                try:
                    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
                    config_path = os.path.join(project_root, "config", "settings.yaml")
                    if os.path.exists(config_path):
                        with open(config_path, "r") as f:
                            config = yaml.safe_load(f) or {}
                            data_path = config.get("data_path")
                except Exception as e:
                    logger.warning(f"尝试从 settings.yaml 读取 data_path 失败: {e}")

            if not data_path:
                data_path = "data/processed/molecules.json"

        if os.path.isabs(data_path):
            self.data_path = data_path
        else:
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            self.data_path = os.path.join(project_root, data_path)
        self.molecules: List[MoleculeData] = []
        self._load_data()

    def _load_data(self) -> None:
        """
        从 JSON 文件加载数据到内存中。
        
        如果文件不存在或解析失败，会记录错误日志，但不会导致程序崩溃（列表为空）。
        """
        if not os.path.exists(self.data_path):
            logger.warning(f"数据文件未找到: {self.data_path}. 使用空数据库。")
            return

        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 使用 Pydantic 模型批量验证和创建对象
                self.molecules = [MoleculeData(**item) for item in data]
            logger.info(f"成功从 {self.data_path} 加载了 {len(self.molecules)} 个分子数据。")
        except json.JSONDecodeError as e:
            logger.error(f"解析分子数据 JSON 失败: {e}")
        except Exception as e:
            logger.error(f"加载分子数据时发生未知错误: {e}")

    def get_molecule(self, uuid: str) -> Optional[MoleculeData]:
        """
        根据 UUID 获取分子对象。
        
        Args:
            uuid (str): 分子的唯一标识符 (UUID)。
            
        Returns:
            Optional[MoleculeData]: 找到的分子对象，如果未找到则返回 None。
        """
        for mol in self.molecules:
            if mol.uuid == uuid:
                return mol
        return None

    def get_all_molecules(self) -> List[MoleculeData]:
        """
        获取所有已加载的分子数据。
        
        Returns:
            List[MoleculeData]: 分子对象列表。
        """
        return self.molecules
