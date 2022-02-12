from ghunt.knowledge.services import services_baseurls
from ghunt.knowledge.keys import keys
from ghunt.knowledge.maps import types_translations
from ghunt.errors import GHuntKnowledgeError


def get_domain_of_service(service: str) -> str:
    if service not in services_baseurls:
        raise GHuntKnowledgeError(f'The service "{service}" has not been found in GHunt\'s knowledge.')
    return services_baseurls.get(service)

def get_origin_of_key(key_name: str) -> str:
    if key_name not in keys:
        raise GHuntKnowledgeError(f'The key "{key_name}" has not been found in GHunt\'s knowledge.')
    return keys.get(key_name, {}).get("origin")

def get_api_key(key_name: str) -> str:
    if key_name not in keys:
        raise GHuntKnowledgeError(f'The key "{key_name}" has not been found in GHunt\'s knowledge.')
    return keys.get(key_name, {}).get("key")

def get_gmaps_type_translation(type_name: str) -> str:
    #if type_name not in types_translations:
        #raise GHuntKnowledgeError(f'The gmaps type "{type_name}" has not been found in GHunt\'s knowledge.\nPlease open an issue on the GHunt Github or submit a PR to add it !')
    return types_translations.get(type_name)