class GHuntKnowledgeError(Exception):
    pass

class GHuntCorruptedHeadersError(Exception):
    pass

class GHuntUnknownVerbError(Exception):
    pass

class GHuntUnknownRequestDataTypeError(Exception):
    pass

class GHuntInsufficientCreds(Exception):
    pass

class GHuntParamsTemplateError(Exception):
    pass

class GHuntParamsInputError(Exception):
    pass

class GHuntAPIResponseParsingError(Exception):
    pass

class GHuntObjectsMergingError(Exception):
    pass

class GHuntAndroidMasterAuthError(Exception):
    pass

class GHuntAndroidAppOAuth2Error(Exception):
    pass

class GHuntOSIDAuthError(Exception):
    pass

class GHuntCredsNotLoaded(Exception):
    pass

class GHuntInvalidSession(Exception):
    pass

class GHuntNotAuthenticated(Exception):
    pass

class GHuntInvalidTarget(Exception):
    pass

class GHuntLoginError(Exception):
    pass