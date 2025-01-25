from typing import *
from ghunt.objects.apis import Parser


class ITKProjectConfig(Parser):
	def __init__(self):
		self.project_id: str = ""
		self.authorized_domains: List[str] = []

	def _scrape(self, itk_project_config_data: Dict[str, any]):
		self.project_id = itk_project_config_data.get('projectId')
		self.authorized_domains = itk_project_config_data.get('authorizedDomains')

class ITKPublicKeys(Parser):
	def __init__(self):
		self.sk_ib_ng: str = ""
		self.t_xew: str = ""
		self.p_r_ww: str = ""
		self.t_bma: str = ""
		self.tl_gyha: str = ""

	def _scrape(self, itk_public_keys_data: Dict[str, str]):
		self.sk_ib_ng = itk_public_keys_data.get('skIBNg')
		self.t_xew = itk_public_keys_data.get('7TX2ew')
		self.p_r_ww = itk_public_keys_data.get('0pR3Ww')
		self.t_bma = itk_public_keys_data.get('tB0M2A')
		self.tl_gyha = itk_public_keys_data.get('tlGYHA')

class ITKSessionCookiePublicKeys(Parser):
	def __init__(self):
		self.keys: List[ITKSessionCookiePublicKey] = []

	def _scrape(self, itk_session_cookie_public_keys_data: Dict[str, list]):
		if (keys_data := itk_session_cookie_public_keys_data.get('keys')):
			for keys_data_item in keys_data:
				keys_item = ITKSessionCookiePublicKey()
				keys_item._scrape(keys_data_item)
				self.keys.append(keys_item)

class ITKSessionCookiePublicKey(Parser):
	def __init__(self):
		self.kty: str = ""
		self.alg: str = ""
		self.use: str = ""
		self.kid: str = ""
		self.n: str = ""
		self.e: str = ""

	def _scrape(self, itk_session_cookie_public_key_data: Dict[str, str]):
		self.kty = itk_session_cookie_public_key_data.get('kty')
		self.alg = itk_session_cookie_public_key_data.get('alg')
		self.use = itk_session_cookie_public_key_data.get('use')
		self.kid = itk_session_cookie_public_key_data.get('kid')
		self.n = itk_session_cookie_public_key_data.get('n')
		self.e = itk_session_cookie_public_key_data.get('e')

class ITKSignupNewUser(Parser):
	def __init__(self):
		self.kind: str = ""
		self.id_token: str = ""
		self.email: str = ""
		self.refresh_token: str = ""
		self.expires_in: str = ""
		self.local_id: str = ""

	def _scrape(self, itk_signup_data: Dict[str, str]):
		self.kind = itk_signup_data.get('kind')
		self.id_token = itk_signup_data.get('idToken')
		self.email = itk_signup_data.get('email')
		self.refresh_token = itk_signup_data.get('refreshToken')
		self.expires_in = itk_signup_data.get('expiresIn')
		self.local_id = itk_signup_data.get('localId')

class ITKVerifyPassword(Parser):
	def __init__(self):
		self.kind: str = ""
		self.local_id: str = ""
		self.email: str = ""
		self.display_name: str = ""
		self.id_token: str = ""
		self.registered: bool = False
		self.refresh_token: str = ""
		self.expires_in: str = ""

	def _scrape(self, itk_verify_password_data: Dict[str, any]):
		self.kind = itk_verify_password_data.get('kind')
		self.local_id = itk_verify_password_data.get('localId')
		self.email = itk_verify_password_data.get('email')
		self.display_name = itk_verify_password_data.get('displayName')
		self.id_token = itk_verify_password_data.get('idToken')
		self.registered = itk_verify_password_data.get('registered')
		self.refresh_token = itk_verify_password_data.get('refreshToken')
		self.expires_in = itk_verify_password_data.get('expiresIn')

