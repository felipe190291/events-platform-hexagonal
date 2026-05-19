"""Event service orchestrating event CRUD and search."""

from app.domain.entities.event import EventEntity
from app.domain.enums import EventStatus, UserRole
from app.domain.exceptions import (
    AuthorizationException,
    EntityNotFoundException,
    InvalidOperationException,
)
from app.domain.ports.event_repository import EventRepositoryPort
from app.domain.ports.cache_port import CachePort


class EventService:
    """Orchestrates event-related business operations."""

    def __init__(self, event_repo: EventRepositoryPort, cache: CachePort):
        self._event_repo = event_repo
        self._cache = cache

    def create_event(self, event_data: dict, organizer_id: int) -> EventEntity:
        """Create a new event with business validations."""
        if event_data["end_date"] <= event_data["start_date"]:
            raise InvalidOperationException("End date must be after start date")

        event = EventEntity(**event_data, organizer_id=organizer_id)
        created = self._event_repo.create(event)
        self._cache.delete_pattern("events:*")
        return created

    def get_event(self, event_id: int) -> EventEntity:
        """Retrieve a single event by its ID."""
        event = self._event_repo.get_by_id(event_id)
        if not event:
            raise EntityNotFoundException("Event", event_id)
        return event

    def search_events(
        self,
        query: str | None = None,
        status: EventStatus | None = None,
        organizer_id: int | None = None,
        page: int = 1,
        size: int = 10,
    ) -> tuple[list[EventEntity], int]:
        """Search events with optional filters and pagination, using cache."""
        # 1. Crear una clave única para esta búsqueda
        cache_key = f"events:search:{query}:{status}:{organizer_id}:{page}:{size}"
        
        # 2. Intentar obtener los resultados desde la caché (Redis)
        cached_result = self._cache.get(cache_key)
        if cached_result:
            print(f"🚀 [CACHE HIT] Resultados obtenidos desde Redis para {cache_key}")
            # Reconstruir las entidades desde el diccionario cacheado
            events = [EventEntity(**e) for e in cached_result["events"]]
            return events, cached_result["total"]
            
        print(f"🐢 [CACHE MISS] Consultando base de datos PostgreSQL para {cache_key}")
        # 3. Si no está en caché, consultar la Base de Datos
        skip = (page - 1) * size
        events, total = self._event_repo.search(
            query=query, 
            status=status, 
            organizer_id=organizer_id, 
            skip=skip, 
            limit=size
        )
        
        # 4. Guardar en caché para futuras consultas (expira en 60 segundos)
        self._cache.set(
            cache_key, 
            {
                "events": [e.model_dump(mode="json") for e in events],
                "total": total
            },
            ttl=60
        )
        
        return events, total

    def update_event(
        self, event_id: int, event_data: dict, user_id: int, user_role: UserRole
    ) -> EventEntity:
        """Update an existing event with authorization and validation."""
        event = self._event_repo.get_by_id(event_id)
        if not event:
            raise EntityNotFoundException("Event", event_id)

        if user_role != UserRole.ADMIN and event.organizer_id != user_id:
            raise AuthorizationException("Only the organizer or admin can update this event")

        if event.status in (EventStatus.COMPLETED, EventStatus.CANCELLED):
            raise InvalidOperationException(f"Cannot update an event with status '{event.status.value}'")

        if "end_date" in event_data and "start_date" in event_data:
            if event_data["end_date"] <= event_data["start_date"]:
                raise InvalidOperationException("End date must be after start date")

        for key, value in event_data.items():
            setattr(event, key, value)

        updated = self._event_repo.update(event)
        self._cache.delete_pattern("events:*")
        return updated

    def delete_event(self, event_id: int, user_id: int, user_role: UserRole) -> bool:
        """Delete an event (ADMIN only)."""
        event = self._event_repo.get_by_id(event_id)
        if not event:
            raise EntityNotFoundException("Event", event_id)

        if user_role != UserRole.ADMIN:
            raise AuthorizationException("Only admins can delete events")

        result = self._event_repo.delete(event_id)
        self._cache.delete_pattern("events:*")
        return result
