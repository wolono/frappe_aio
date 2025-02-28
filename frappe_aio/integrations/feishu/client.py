from typing import Any, Dict, Optional
from ..base import BaseIntegration

class FeishuIntegration(BaseIntegration):
    def __init__(self):
        super().__init__()
        self.platform = "feishu"
        self.initialize()
    
    def initialize(self) -> None:
        """初始化飞书集成配置"""
        self.settings = frappe.get_doc("Feishu Settings")
        self.config = {
            "app_id": self.settings.app_id,
            "app_secret": self.settings.app_secret,
            "verification_token": self.settings.verification_token,
            "encryption_key": self.settings.encryption_key
        }
    
    def get_access_token(self) -> str:
        """获取飞书访问令牌"""
        return self.settings.get_access_token()
    
    def refresh_token(self) -> None:
        """刷新飞书访问令牌"""
        self.get_access_token()
    
    def send_message(self, message: Dict[str, Any]) -> bool:
        """发送消息到飞书"""
        token = self.get_access_token()
        if not token:
            return False
        
        url = "https://open.feishu.cn/open-apis/im/v1/messages"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        try:
            response = requests.post(url, headers=headers, data=json.dumps(message))
            result = response.json()
            if result.get("code") == 0:
                return True
            else:
                frappe.log_error(f"发送飞书消息失败: {result}", "Feishu Message Error")
                return False
        except Exception as e:
            frappe.log_error(f"发送飞书消息异常: {str(e)}", "Feishu Message Exception")
            return False
    
    def handle_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """处理飞书事件回调"""
        # 根据事件类型处理不同的事件
        event_type = event.get("type")
        if event_type == "url_verification":
            # 处理 URL 验证事件
            return {
                "challenge": event.get("challenge")
            }
        elif event_type == "im.message.receive_v1":
            # 处理接收消息事件
            self._handle_message_event(event)
        
        return {"code": 0, "msg": "success"}
    
    def _handle_message_event(self, event: Dict[str, Any]) -> None:
        """处理消息事件"""
        # 这里可以添加消息处理逻辑
        message = event.get("event", {}).get("message", {})
        if not message:
            return
        
        # 记录消息
        frappe.get_doc({
            "doctype": "Feishu Message",
            "message_id": message.get("message_id"),
            "chat_id": message.get("chat_id"),
            "content": message.get("content"),
            "sender_id": message.get("sender", {}).get("sender_id", {}).get("user_id"),
            "create_time": datetime.fromtimestamp(int(message.get("create_time", 0)))
        }).insert(ignore_permissions=True)
    
    def sync_users(self) -> None:
        """同步飞书用户信息"""
        token = self.get_access_token()
        if not token:
            return
        
        # 获取部门列表
        departments = self._get_departments(token)
        
        # 获取用户列表
        for dept in departments:
            users = self._get_department_users(token, dept.get("department_id"))
            # 处理用户数据
            self._process_users(users)
    
    def _get_departments(self, token: str) -> List[Dict[str, Any]]:
        """获取部门列表"""
        url = "https://open.feishu.cn/open-apis/contact/v3/departments/children"
        params = {"department_id": "0", "fetch_child": "true"}
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            response = requests.get(url, params=params, headers=headers)
            result = response.json()
            if result.get("code") == 0:
                return result.get("data", {}).get("items", [])
            else:
                frappe.log_error(f"获取飞书部门列表失败: {result}", "Feishu Department Error")
                return []
        except Exception as e:
            frappe.log_error(f"获取飞书部门列表异常: {str(e)}", "Feishu Department Exception")
            return []
    
    def _get_department_users(self, token: str, department_id: str) -> List[Dict[str, Any]]:
        """获取部门用户列表"""
        url = "https://open.feishu.cn/open-apis/contact/v3/users/find_by_department"
        params = {"department_id": department_id, "page_size": 100}
        headers = {"Authorization": f"Bearer {token}"}
        
        all_users = []
        has_more = True
        page_token = None
        
        while has_more:
            if page_token:
                params["page_token"] = page_token
                
            try:
                response = requests.get(url, params=params, headers=headers)
                result = response.json()
                if result.get("code") == 0:
                    data = result.get("data", {})
                    users = data.get("items", [])
                    all_users.extend(users)
                    
                    has_more = data.get("has_more", False)
                    page_token = data.get("page_token")
                else:
                    frappe.log_error(f"获取飞书部门用户列表失败: {result}", "Feishu User Error")
                    break
            except Exception as e:
                frappe.log_error(f"获取飞书部门用户列表异常: {str(e)}", "Feishu User Exception")
                break
        
        return all_users
    
    def _process_users(self, users: List[Dict[str, Any]]) -> None:
        """处理用户数据"""
        for user in users:
            user_id = user.get("user_id")
            if not user_id:
                continue
                
            # 检查用户是否已存在
            existing = frappe.db.exists("Feishu User", {"user_id": user_id})
            
            if existing:
                # 更新用户
                doc = frappe.get_doc("Feishu User", existing)
                doc.update({
                    "name": user.get("name"),
                    "email": user.get("email"),
                    "mobile": user.get("mobile"),
                    "department_ids": json.dumps(user.get("department_ids", [])),
                    "status": user.get("status", {}).get("is_active") and "Active" or "Inactive"
                })
                doc.save(ignore_permissions=True)
            else:
                # 创建新用户
                frappe.get_doc({
                    "doctype": "Feishu User",
                    "user_id": user_id,
                    "name": user.get("name"),
                    "email": user.get("email"),
                    "mobile": user.get("mobile"),
                    "department_ids": json.dumps(user.get("department_ids", [])),
                    "status": user.get("status", {}).get("is_active") and "Active" or "Inactive"
                }).insert(ignore_permissions=True)
    
    def sync_departments(self) -> None:
        """同步飞书部门信息"""
        token = self.get_access_token()
        if not token:
            return
            
        # 获取部门列表
        departments = self._get_departments(token)
        
        # 处理部门数据
        self._process_departments(departments)
    def _process_departments(self, departments: List[Dict[str, Any]]) -> None:
        """处理部门数据"""
        for dept in departments:
            dept_id = dept.get("department_id")
            if not dept_id:
                continue
                
            # 检查部门是否已存在
            existing = frappe.db.exists("Feishu Department", {"department_id": dept_id})
            
            if existing:
                # 更新部门
                doc = frappe.get_doc("Feishu Department", existing)
                doc.update({
                    "department_name": dept.get("name"),
                    "parent_department_id": dept.get("parent_department_id"),
                    "leader_user_id": dept.get("leader_user_id"),
                    "status": dept.get("status", {}).get("is_deleted") and "Deleted" or "Active"
                })
                doc.save(ignore_permissions=True)
            else:
                # 创建新部门
                frappe.get_doc({
                    "doctype": "Feishu Department",
                    "department_id": dept_id,
                    "department_name": dept.get("name"),
                    "parent_department_id": dept.get("parent_department_id"),
                    "leader_user_id": dept.get("leader_user_id"),
                    "status": dept.get("status", {}).get("is_deleted") and "Deleted" or "Active"
                }).insert(ignore_permissions=True)