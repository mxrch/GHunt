class GHuntKnowledgeError(BaseException):
    pass

class GHuntCorruptedHeadersError(BaseException):
    pass

class GHuntUnknownVerbError(BaseException):
    pass

class GHuntUnknownRequestDataTypeError(BaseException):
    pass

class GHuntInsufficientCreds(BaseException):
    pass

class GHuntParamsTemplateError(BaseException):
    pass

class GHuntParamsInputError(BaseException):
    pass

class GHuntAPIResponseParsingError(BaseException):
    pass

class GHuntObjectsMergingError(BaseException):
    pass

class GHuntAndroidMasterAuthError(BaseException):
    pass

class GHuntAndroidAppOAuth2Error(BaseException):
    pass

class GHuntOSIDAuthError(BaseException):
    pass

class GHuntCredsNotLoaded(BaseException):
    pass

class GHuntInvalidSession(BaseException):
    pass

class GHuntNotAuthenticated(BaseException):
    pass

class GHuntInvalidTarget(BaseException):
    pass

class GHuntLoginError(BaseException):
    pass