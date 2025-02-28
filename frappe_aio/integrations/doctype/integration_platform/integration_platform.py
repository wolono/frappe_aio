import frappe
from frappe.model.document import Document

class IntegrationPlatform(Document):
	def validate(self):
		self.validate_duplicate()
	
	def validate_duplicate(self):
		"""确保每个平台只有一个启用的配置"""
		if self.is_enabled:
			existing = frappe.db.exists(
				"Integration Platform",
				{
					"platform_type": self.platform_type,
					"is_enabled": 1,
					"name": ["!=", self.name]
				}
			)
			if existing:
				frappe.throw(f"已存在启用的 {self.platform_type} 平台配置")