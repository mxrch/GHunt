from typing import *
from ghunt.objects.apis import Parser


class CacBrand(Parser):
	def __init__(self):
		self.brand_id: str = ""
		self.project_ids: List[list] = []
		self.project_numbers: List[str] = []
		self.display_name: str = ""
		self.icon_url: str = ""
		self.stored_icon_url: str = ""
		self.support_email: str = ""
		self.home_page_url: str = ""
		self.terms_of_service_urls: List[list] = []
		self.privacy_policy_urls: List[list] = []
		self.direct_notice_to_parents_url: str = ""
		self.brand_state: CacBrandState = CacBrandState()
		self.clients: List[list] = []
		self.review: CacReview = CacReview()
		self.is_org_internal: bool = False
		self.risc_configuration: CacRiscConfiguration = CacRiscConfiguration()
		self.consistency_token: str = ""
		self.creation_time: str = ""
		self.verified_brand: CacVerifiedBrand = CacVerifiedBrand()

	def _scrape(self, base_model_data: Dict[str, any]):
		self.brand_id = base_model_data.get('brandId')
		self.project_ids = base_model_data.get('projectIds')
		self.project_numbers = base_model_data.get('projectNumbers')
		self.display_name = base_model_data.get('displayName')
		self.icon_url = base_model_data.get('iconUrl')
		self.stored_icon_url = base_model_data.get('storedIconUrl')
		self.support_email = base_model_data.get('supportEmail')
		self.home_page_url = base_model_data.get('homePageUrl')
		self.terms_of_service_urls = base_model_data.get('termsOfServiceUrls')
		self.privacy_policy_urls = base_model_data.get('privacyPolicyUrls')
		self.direct_notice_to_parents_url = base_model_data.get('directNoticeToParentsUrl')
		if (brand_state_data := base_model_data.get('brandState')):
			self.brand_state._scrape(brand_state_data)
		self.clients = base_model_data.get('clients')
		if (review_data := base_model_data.get('review')):
			self.review._scrape(review_data)
		self.is_org_internal = base_model_data.get('isOrgInternal')
		if (risc_configuration_data := base_model_data.get('riscConfiguration')):
			self.risc_configuration._scrape(risc_configuration_data)
		self.consistency_token = base_model_data.get('consistencyToken')
		self.creation_time = base_model_data.get('creationTime')
		if (verified_brand_data := base_model_data.get('verifiedBrand')):
			self.verified_brand._scrape(verified_brand_data)

class CacBrandState(Parser):
	def __init__(self):
		self.state: str = ""
		self.admin_id: str = ""
		self.reason: str = ""
		self.limits: CacLimits = CacLimits()
		self.brand_setup: str = ""
		self.creation_flow: str = ""
		self.update_timestamp: str = ""

	def _scrape(self, brand_state_data: Dict[str, any]):
		self.state = brand_state_data.get('state')
		self.admin_id = brand_state_data.get('adminId')
		self.reason = brand_state_data.get('reason')
		if (limits_data := brand_state_data.get('limits')):
			self.limits._scrape(limits_data)
		self.brand_setup = brand_state_data.get('brandSetup')
		self.creation_flow = brand_state_data.get('creationFlow')
		self.update_timestamp = brand_state_data.get('updateTimestamp')

class CacLimits(Parser):
	def __init__(self):
		self.approval_quota_multiplier: int = 0
		self.max_domain_count: int = 0
		self.default_max_client_count: int = 0

	def _scrape(self, limits_data: Dict[str, int]):
		self.approval_quota_multiplier = limits_data.get('approvalQuotaMultiplier')
		self.max_domain_count = limits_data.get('maxDomainCount')
		self.default_max_client_count = limits_data.get('defaultMaxClientCount')

class CacReview(Parser):
	def __init__(self):
		self.has_abuse_verdict: bool = False
		self.is_published: bool = False
		self.review_state: str = ""
		self.high_risk_scopes_privilege: str = ""
		self.low_risk_scopes: List[list] = []
		self.pending_scopes: List[list] = []
		self.exempt_scopes: List[list] = []
		self.approved_scopes: List[list] = []
		self.historical_approved_scopes: List[list] = []
		self.pending_domains: List[str] = []
		self.approved_domains: List[list] = []
		self.enforce_request_scopes: bool = False
		self.category: List[list] = []
		self.decision_timestamp: str = ""

	def _scrape(self, review_data: Dict[str, any]):
		self.has_abuse_verdict = review_data.get('hasAbuseVerdict')
		self.is_published = review_data.get('isPublished')
		self.review_state = review_data.get('reviewState')
		self.high_risk_scopes_privilege = review_data.get('highRiskScopesPrivilege')
		self.low_risk_scopes = review_data.get('lowRiskScopes')
		self.pending_scopes = review_data.get('pendingScopes')
		self.exempt_scopes = review_data.get('exemptScopes')
		self.approved_scopes = review_data.get('approvedScopes')
		self.historical_approved_scopes = review_data.get('historicalApprovedScopes')
		self.pending_domains = review_data.get('pendingDomains')
		self.approved_domains = review_data.get('approvedDomains')
		self.enforce_request_scopes = review_data.get('enforceRequestScopes')
		self.category = review_data.get('category')
		self.decision_timestamp = review_data.get('decisionTimestamp')

class CacRiscConfiguration(Parser):
	def __init__(self):
		self.enabled: bool = False
		self.delivery_method: str = ""
		self.receiver_supported_event_type: List[list] = []
		self.legal_agreement: List[str] = []

	def _scrape(self, risc_configuration_data: Dict[str, any]):
		self.enabled = risc_configuration_data.get('enabled')
		self.delivery_method = risc_configuration_data.get('deliveryMethod')
		self.receiver_supported_event_type = risc_configuration_data.get('receiverSupportedEventType')
		self.legal_agreement = risc_configuration_data.get('legalAgreement')

class CacVerifiedBrand(Parser):
	def __init__(self):
		self.display_name: CacDisplayName = CacDisplayName()
		self.stored_icon_url: CacStoredIconUrl = CacStoredIconUrl()
		self.support_email: CacSupportEmail = CacSupportEmail()
		self.home_page_url: CacHomePageUrl = CacHomePageUrl()
		self.privacy_policy_url: CacPrivacyPolicyUrl = CacPrivacyPolicyUrl()
		self.terms_of_service_url: CacTermsOfServiceUrl = CacTermsOfServiceUrl()

	def _scrape(self, verified_brand_data: Dict[str, any]):
		if (display_name_data := verified_brand_data.get('displayName')):
			self.display_name._scrape(display_name_data)
		if (stored_icon_url_data := verified_brand_data.get('storedIconUrl')):
			self.stored_icon_url._scrape(stored_icon_url_data)
		if (support_email_data := verified_brand_data.get('supportEmail')):
			self.support_email._scrape(support_email_data)
		if (home_page_url_data := verified_brand_data.get('homePageUrl')):
			self.home_page_url._scrape(home_page_url_data)
		if (privacy_policy_url_data := verified_brand_data.get('privacyPolicyUrl')):
			self.privacy_policy_url._scrape(privacy_policy_url_data)
		if (terms_of_service_url_data := verified_brand_data.get('termsOfServiceUrl')):
			self.terms_of_service_url._scrape(terms_of_service_url_data)

class CacDisplayName(Parser):
	def __init__(self):
		self.value: str = ""
		self.reason: str = ""

	def _scrape(self, display_name_data: Dict[str, str]):
		self.value = display_name_data.get('value')
		self.reason = display_name_data.get('reason')

class CacStoredIconUrl(Parser):
	def __init__(self):
		self.value: str = ""
		self.reason: str = ""

	def _scrape(self, stored_icon_url_data: Dict[str, str]):
		self.value = stored_icon_url_data.get('value')
		self.reason = stored_icon_url_data.get('reason')

class CacSupportEmail(Parser):
	def __init__(self):
		self.value: str = ""
		self.reason: str = ""

	def _scrape(self, support_email_data: Dict[str, str]):
		self.value = support_email_data.get('value')
		self.reason = support_email_data.get('reason')

class CacHomePageUrl(Parser):
	def __init__(self):
		self.value: str = ""
		self.reason: str = ""

	def _scrape(self, home_page_url_data: Dict[str, str]):
		self.value = home_page_url_data.get('value')
		self.reason = home_page_url_data.get('reason')

class CacPrivacyPolicyUrl(Parser):
	def __init__(self):
		self.value: str = ""
		self.reason: str = ""

	def _scrape(self, privacy_policy_url_data: Dict[str, str]):
		self.value = privacy_policy_url_data.get('value')
		self.reason = privacy_policy_url_data.get('reason')

class CacTermsOfServiceUrl(Parser):
	def __init__(self):
		self.value: str = ""
		self.reason: str = ""

	def _scrape(self, terms_of_service_url_data: Dict[str, str]):
		self.value = terms_of_service_url_data.get('value')
		self.reason = terms_of_service_url_data.get('reason')

