import frappe
import json
from typing import Dict, Any, List, Optional
from ..factory import IntegrationFactory

def send_text_message(chat_id: str, content: str) -> bool:
    """发送文本消息到飞书"""
    feishu = IntegrationFactory.get_integration("feishu")
    if not feishu:
        frappe.log_error("飞书集成未初始化", "Feishu Message Error")
        return False
    
    message = {
        "receive_id": chat_id,
        "msg_type": "text",
        "content": json.dumps({"text": content})
    }
    
    return feishu.send_message(message)

def send_image_message(chat_id: str, image_key: str) -> bool:
    """发送图片消息到飞书"""
    feishu = IntegrationFactory.get_integration("feishu")
    if not feishu:
        frappe.log_error("飞书集成未初始化", "Feishu Message Error")
        return False
    
    message = {
        "receive_id": chat_id,
        "msg_type": "image",
        "content": json.dumps({"image_key": image_key})
    }
    
    return feishu.send_message(message)

def send_card_message(chat_id: str, card_content: Dict[str, Any]) -> bool:
    """发送卡片消息到飞书"""
    feishu = IntegrationFactory.get_integration("feishu")
    if not feishu:
        frappe.log_error("飞书集成未初始化", "Feishu Message Error")
        return False
    
    message = {
        "receive_id": chat_id,
        "msg_type": "interactive",
        "content": json.dumps(card_content)
    }
    
    return feishu.send_message(message)

def send_post_message(chat_id: str, post_content: Dict[str, Any]) -> bool:
    """发送富文本消息到飞书"""
    feishu = IntegrationFactory.get_integration("feishu")
    if not feishu:
        frappe.log_error("飞书集成未初始化", "Feishu Message Error")
        return False
    
    message = {
        "receive_id": chat_id,
        "msg_type": "post",
        "content": json.dumps(post_content)
    }
    
    return feishu.send_message(message)

def send_file_message(chat_id: str, file_key: str) -> bool:
    """发送文件消息到飞书"""
    feishu = IntegrationFactory.get_integration("feishu")
    if not feishu:
        frappe.log_error("飞书集成未初始化", "Feishu Message Error")
        return False
    
    message = {
        "receive_id": chat_id,
        "msg_type": "file",
        "content": json.dumps({"file_key": file_key})
    }
    
    return feishu.send_message(message)

def upload_image(file_path: str) -> Optional[str]:
    """上传图片到飞书，返回图片 key"""
    feishu = IntegrationFactory.get_integration("feishu")
    if not feishu:
        frappe.log_error("飞书集成未初始化", "Feishu Image Error")
        return None
    
    token = feishu.get_access_token()
    if not token:
        return None
    
    import requests
    
    url = "https://open.feishu.cn/open-apis/im/v1/images"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        with open(file_path, "rb") as f:
            files = {"image": f}
            response = requests.post(url, headers=headers, files=files)
            result = response.json()
            
            if result.get("code") == 0:
                return result.get("data", {}).get("image_key")
            else:
                frappe.log_error(f"上传图片到飞书失败: {result}", "Feishu Image Error")
                return None
    except Exception as e:
        frappe.log_error(f"上传图片到飞书异常: {str(e)}", "Feishu Image Exception")
        return None

def upload_file(file_path: str) -> Optional[str]:
    """上传文件到飞书，返回文件 key"""
    feishu = IntegrationFactory.get_integration("feishu")
    if not feishu:
        frappe.log_error("飞书集成未初始化", "Feishu File Error")
        return None
    
    token = feishu.get_access_token()
    if not token:
        return None
    
    import requests
    import os
    
    url = "https://open.feishu.cn/open-apis/im/v1/files"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        with open(file_path, "rb") as f:
            file_name = os.path.basename(file_path)
            files = {"file": (file_name, f)}
            response = requests.post(url, headers=headers, files=files)
            result = response.json()
            
            if result.get("code") == 0:
                return result.get("data", {}).get("file_key")
            else:
                frappe.log_error(f"上传文件到飞书失败: {result}", "Feishu File Error")
                return None
    except Exception as e:
        frappe.log_error(f"上传文件到飞书异常: {str(e)}", "Feishu File Exception")
        return None

def create_card_builder() -> Dict[str, Any]:
    """创建卡片构建器"""
    return {
        "config": {
            "wide_screen_mode": True
        },
        "elements": []
    }

def add_text_to_card(card: Dict[str, Any], text: str, is_bold: bool = False, is_italic: bool = False) -> Dict[str, Any]:
    """向卡片添加文本元素"""
    text_element = {
        "tag": "plain_text",
        "content": text
    }
    
    if is_bold or is_italic:
        text_element["style"] = {}
        if is_bold:
            text_element["style"]["bold"] = True
        if is_italic:
            text_element["style"]["italic"] = True
    
    card["elements"].append({
        "tag": "div",
        "text": text_element
    })
    
    return card

def add_markdown_to_card(card: Dict[str, Any], markdown: str) -> Dict[str, Any]:
    """向卡片添加 Markdown 元素"""
    card["elements"].append({
        "tag": "markdown",
        "content": markdown
    })
    
    return card

def add_image_to_card(card: Dict[str, Any], image_key: str, alt: str = "") -> Dict[str, Any]:
    """向卡片添加图片元素"""
    card["elements"].append({
        "tag": "img",
        "img_key": image_key,
        "alt": {
            "tag": "plain_text",
            "content": alt
        }
    })
    
    return card

def add_button_to_card(card: Dict[str, Any], text: str, value: Dict[str, Any], type: str = "default") -> Dict[str, Any]:
    """向卡片添加按钮元素"""
    card["elements"].append({
        "tag": "action",
        "actions": [
            {
                "tag": "button",
                "text": {
                    "tag": "plain_text",
                    "content": text
                },
                "type": type,
                "value": value
            }
        ]
    })
    
    return card

def add_divider_to_card(card: Dict[str, Any]) -> Dict[str, Any]:
    """向卡片添加分割线"""
    card["elements"].append({
        "tag": "hr"
    })
    
    return card

def set_card_header(card: Dict[str, Any], title: str, template: str = "blue") -> Dict[str, Any]:
    """设置卡片标题"""
    card["header"] = {
        "title": {
            "tag": "plain_text",
            "content": title
        },
        "template": template
    }
    
    return card