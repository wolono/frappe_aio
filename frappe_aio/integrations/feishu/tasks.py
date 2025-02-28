import frappe
from ..factory import IntegrationFactory

def sync_feishu_data():
    """同步飞书数据（用户和部门）"""
    if not frappe.db.get_single_value("Feishu Settings", "enabled"):
        return
    
    feishu = IntegrationFactory.get_integration("feishu")
    if not feishu:
        frappe.log_error("飞书集成未初始化", "Feishu Sync Error")
        return
    
    try:
        # 同步部门信息
        feishu.sync_departments()
        
        # 同步用户信息
        feishu.sync_users()
        
        frappe.logger().info("飞书数据同步完成")
    except Exception as e:
        frappe.log_error(f"飞书数据同步失败: {str(e)}", "Feishu Sync Error")