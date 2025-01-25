from typing import *
from ghunt.objects.apis import Parser


class MobileSDKDynamicConfig(Parser):
	def __init__(self):
		self.database_url: str = ""
		self.storage_bucket: str = ""
		self.auth_domain: str = ""
		self.messaging_sender_id: str = ""
		self.project_id: str = ""

	def _scrape(self, dynamic_config_base_model_data: Dict[str, str]):
		self.database_url = dynamic_config_base_model_data.get('databaseURL')
		self.storage_bucket = dynamic_config_base_model_data.get('storageBucket')
		self.auth_domain = dynamic_config_base_model_data.get('authDomain')
		self.messaging_sender_id = dynamic_config_base_model_data.get('messagingSenderId')
		self.project_id = dynamic_config_base_model_data.get('projectId')

