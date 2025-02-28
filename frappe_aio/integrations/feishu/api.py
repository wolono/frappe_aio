import frappe
from frappe import _
import json
from ..factory import IntegrationFactory

@frappe.whitelist(allow_guest=True)
def webhook():
    """处理飞书事件回调"""
    if frappe.request.method != "POST":
        frappe.throw(_("仅支持 POST 请求"))
    
    try:
        # 获取请求数据
        data = json.loads(frappe.request.data)
        
        # 获取飞书集成实例
        feishu = IntegrationFactory.get_integration("feishu")
        if not feishu:
            frappe.throw(_("飞书集成未初始化"))
        
        # 处理事件
        result = feishu.handle_event(data)
        
        return result
    except Exception as e:
        frappe.log_error(f"处理飞书事件回调失败: {str(e)}", "Feishu Webhook Error")
        return {"code": -1, "msg": str(e)}

@frappe.whitelist(allow_guest=True)
def card_callback():
    """处理飞书卡片消息回调"""
    if frappe.request.method != "POST":
        frappe.throw(_("仅支持 POST 请求"))
    
    try:
        # 获取请求数据
        data = json.loads(frappe.request.data)
        
        # 获取飞书集成实例
        feishu = IntegrationFactory.get_integration("feishu")
        if not feishu:
            frappe.throw(_("飞书集成未初始化"))
        
        # 处理卡片回调
        result = feishu.handle_card_callback(data)
        
        return result
    except Exception as e:
        frappe.log_error(f"处理飞书卡片回调失败: {str(e)}", "Feishu Card Callback Error")
        return {"code": -1, "msg": str(e)}
# 在现有的 api.py 文件中添加以下方法

@frappe.whitelist()
def refresh_token():
    """刷新飞书访问令牌"""
    try:
        feishu = IntegrationFactory.get_integration("feishu")
        if not feishu:
            return {"success": False, "error": "飞书集成未初始化"}
        
        feishu.refresh_token()
        return {"success": True}
    except Exception as e:
        frappe.log_error(f"刷新飞书访问令牌失败: {str(e)}", "Feishu Token Error")
        return {"success": False, "error": str(e)}

@frappe.whitelist()
def test_connection():
    """测试飞书连接"""
    try:
        feishu = IntegrationFactory.get_integration("feishu")
        if not feishu:
            return {"success": False, "error": "飞书集成未初始化"}
        
        token = feishu.get_access_token()
        if not token:
            return {"success": False, "error": "获取访问令牌失败"}
        
        return {"success": True}
    except Exception as e:
        frappe.log_error(f"测试飞书连接失败: {str(e)}", "Feishu Connection Error")
        return {"success": False, "error": str(e)}

@frappe.whitelist()
def sync_data():
    """同步飞书数据"""
    try:
        # 使用后台任务执行同步，避免请求超时
        frappe.enqueue(
            "frappe_aio.integrations.feishu.tasks.sync_feishu_data",
            queue="long",
            timeout=1500
        )
        return {"success": True}
    except Exception as e:
        frappe.log_error(f"同步飞书数据失败: {str(e)}", "Feishu Sync Error")
        return {"success": False, "error": str(e)}

@frappe.whitelist()
def send_test_message(chat_id, content):
    """发送测试消息"""
    try:
        from .utils import send_text_message
        
        result = send_text_message(chat_id, content)
        if result:
            return {"success": True}
        else:
            return {"success": False, "error": "发送消息失败"}
    except Exception as e:
        frappe.log_error(f"发送测试消息失败: {str(e)}", "Feishu Message Error")
        return {"success": False, "error": str(e)}