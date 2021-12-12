from ghunt.knowledge.services import services_baseurls
from ghunt.knowledge.keys import keys_origins
from ghunt.errors import GHuntKnowledgeError


def get_domain_of_service(service: str) -> str:
    if service not in services_baseurls:
        raise GHuntKnowledgeError(f'The service "{service}" has not been found in GHunt\'s knowledge.')
    return services_baseurls.get(service)

def get_origin_of_key(key_name: str) -> str:
    if key_name not in keys_origins:
        raise GHuntKnowledgeError(f'The key "{key_name}" has not been found in GHunt\'s knowledge.')
    return keys_origins.get(key_name)