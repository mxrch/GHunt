from typing import *
from ghunt.objects.apis import Parser


class DalStatements(Parser):
	def __init__(self):
		self.statements: List[DalStatement] = []
		self.max_age: str = ""
		self.debug_string: str = ""

	def _scrape(self, digital_assets_links_base_model_data: Dict[str, any]):
		if (statements_data := digital_assets_links_base_model_data.get('statements')):
			for statements_data_item in statements_data:
				statements_item = DalStatement()
				statements_item._scrape(statements_data_item)
				self.statements.append(statements_item)
		self.max_age = digital_assets_links_base_model_data.get('maxAge')
		self.debug_string = digital_assets_links_base_model_data.get('debugString')

class DalStatement(Parser):
	def __init__(self):
		self.source: DalSource = DalSource()
		self.relation: str = ""
		self.target: DalTarget = DalTarget()

	def _scrape(self, digital_assets_links_unknown_model1_data: Dict[str, any]):
		if (source_data := digital_assets_links_unknown_model1_data.get('source')):
			self.source._scrape(source_data)
		self.relation = digital_assets_links_unknown_model1_data.get('relation')
		if (target_data := digital_assets_links_unknown_model1_data.get('target')):
			self.target._scrape(target_data)

class DalSource(Parser):
	def __init__(self):
		self.web: DalWeb = DalWeb()

	def _scrape(self, digital_assets_links_source_data: Dict[str, any]):
		if (web_data := digital_assets_links_source_data.get('web')):
			self.web._scrape(web_data)

class DalWeb(Parser):
	def __init__(self):
		self.site: str = ""

	def _scrape(self, digital_assets_links_web_data: Dict[str, str]):
		self.site = digital_assets_links_web_data.get('site')

class DalTarget(Parser):
	def __init__(self):
		self.android_app: DalAndroidApp = DalAndroidApp()
		self.web: DalWeb = DalWeb()

	def _scrape(self, digital_assets_links_target_data: Dict[str, any]):
		if (android_app_data := digital_assets_links_target_data.get('androidApp')):
			self.android_app._scrape(android_app_data)
		if (web_data := digital_assets_links_target_data.get('web')):
			self.web._scrape(web_data)

class DalAndroidApp(Parser):
	def __init__(self):
		self.package_name: str = ""
		self.certificate: DalCertificate = DalCertificate()

	def _scrape(self, digital_assets_links_android_app_data: Dict[str, any]):
		self.package_name = digital_assets_links_android_app_data.get('packageName')
		if (certificate_data := digital_assets_links_android_app_data.get('certificate')):
			self.certificate._scrape(certificate_data)

class DalCertificate(Parser):
	def __init__(self):
		self.sha_fingerprint: str = ""

	def _scrape(self, digital_assets_links_certificate_data: Dict[str, str]):
		self.sha_fingerprint = digital_assets_links_certificate_data.get('sha256Fingerprint')
