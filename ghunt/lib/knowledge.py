from ghunt.knowledge.services import services
from ghunt.errors import GHuntKnowledgeError


def get_domain_of_service(service: str) -> str:
    if service not in services:
        raise GHuntKnowledgeError(f'The service "{service}" has not been found in GHunt\'s knowledge.')
    return services.get(service)