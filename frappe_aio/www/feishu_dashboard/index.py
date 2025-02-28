import frappe
from frappe import _
from frappe.utils import now_datetime

def get_context(context):
    context.title = _("飞书集成管理")
    context.no_cache = 1
    
    # 获取飞书设置
    context.feishu_settings = frappe.get_doc("Feishu Settings")
    
    # 获取用户和部门统计
    context.user_count = frappe.db.count("Feishu User")
    context.department_count = frappe.db.count("Feishu Department")
    
    # 获取最近的消息记录
    context.recent_messages = frappe.get_all(
        "Feishu Message",
        fields=["message_id", "chat_id", "sender_id", "content", "create_time"],
        order_by="create_time desc",
        limit=10
    )
    
    return context