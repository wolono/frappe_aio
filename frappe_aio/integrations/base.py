from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class BaseIntegration(ABC):
    def __init__(self):
        self.platform: str = ""
        self.config: Dict[str, Any] = {}
    
    @abstractmethod
    def initialize(self) -> None:
        """初始化集成配置"""
        pass

    @abstractmethod
    def get_access_token(self) -> str:
        """获取访问令牌"""
        pass

    @abstractmethod
    def refresh_token(self) -> None:
        """刷新访问令牌"""
        pass

    @abstractmethod
    def send_message(self, message: Dict[str, Any]) -> bool:
        """发送消息"""
        pass

    @abstractmethod
    def handle_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """处理平台事件"""
        pass

    @abstractmethod
    def sync_users(self) -> None:
        """同步用户信息"""
        pass

    @abstractmethod
    def sync_departments(self) -> None:
        """同步部门信息"""
        pass