import frappe
from frappe.model.document import Document
import json
import requests
from datetime import datetime, timedelta

class FeishuSettings(Document):
    def validate(self):
        self.set_webhook_url()
    
    def set_webhook_url(self):
        """设置 Webhook URL"""
        site_url = frappe.utils.get_url()
        self.webhook_url = f"{site_url}/api/method/frappe_aio.integrations.feishu.api.webhook"
    
    def get_access_token(self):
        """获取飞书访问令牌"""
        # 检查是否有有效的访问令牌
        if self.access_token and self.token_expiry:
            expiry = datetime.fromisoformat(self.token_expiry)
            if expiry > datetime.now() + timedelta(minutes=5):
                return self.access_token
        
        # 获取新的访问令牌
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        response = requests.post(url, headers=headers, data=json.dumps(data))
        result = response.json()
        
        if result.get("code") == 0:
            self.access_token = result.get("tenant_access_token")
            expiry_time = datetime.now() + timedelta(seconds=result.get("expire", 7200))
            self.token_expiry = expiry_time.isoformat()
            self.save(ignore_permissions=True)
            return self.access_token
        else:
            frappe.log_error(f"获取飞书访问令牌失败: {result}", "Feishu Token Error")
            return None