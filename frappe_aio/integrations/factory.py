from typing import Dict, Optional
from .base import BaseIntegration

class IntegrationFactory:
    _instances: Dict[str, BaseIntegration] = {}
    
    @classmethod
    def get_integration(cls, platform: str) -> Optional[BaseIntegration]:
        """获取指定平台的集成实例"""
        if platform not in cls._instances:
            if platform == "feishu":
                from .feishu.client import FeishuIntegration
                cls._instances[platform] = FeishuIntegration()
            # 预留其他平台的实现
            # elif platform == "wecom":
            #     from .wecom.client import WecomIntegration
            #     cls._instances[platform] = WecomIntegration()
            # elif platform == "dingtalk":
            #     from .dingtalk.client import DingTalkIntegration
            #     cls._instances[platform] = DingTalkIntegration()
        
        return cls._instances.get(platform)