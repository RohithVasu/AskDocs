from datetime import datetime
import json
from loguru import logger
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
from typing import Dict, List, Optional, Any
import uuid

from app.core.settings import settings

class Qdrant:
    def __init__(self):
        self.client = QdrantClient(
            url=settings.qdrant.url,
        )
        self.encoder = SentenceTransformer(
            settings.qdrant.embed_model
        )
        self.search_limit = settings.qdrant.search_limit
        self.scroll_limit = settings.qdrant.scroll_limit
    
    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for text"""
        return self.encoder.encode(text)

    def _ensure_collection(self, collection_name: str):
        """Ensure the specified collection exists"""
        try:
            self.client.get_collection(collection_name)
        except:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=384,
                    distance=models.Distance.COSINE
                ),
                on_disk_payload=True
            )

    # def add_document(self, collection_name: str, payload: Dict[str, Any], content: str):
    #     """Add a single chunk to the collection."""
    #     self._ensure_collection(collection_name)

    #     embedding = self._get_embedding(content)

    #     self.client.upsert(
    #         collection_name=collection_name,
    #         points=[
    #             models.PointStruct(
    #                 id=str(uuid.uuid4()),
    #                 vector=embedding,
    #                 payload={**payload, "text": content}
    #             )
    #         ]
    #     )

    # def manage_aliases(self, alias_name: str, collection_name: str, previous_collection=None):
    #     """Manage Qdrant collection aliases"""
    #     try:
    #         # Get existing aliases
    #         aliases = self.client.get_aliases()
    #         previous_collection = previous_collection or None

    #         # Find existing alias if not provided
    #         if not previous_collection:
    #             for alias in aliases.aliases:
    #                 if alias.alias_name == alias_name:
    #                     previous_collection = alias.collection_name
    #                     break

    #         # If there's a previous collection, update alias and delete old collection
    #         if previous_collection:
    #             # First update the alias to point to new collection
    #             self.client.update_collection_aliases(
    #                 change_aliases_operations=[
    #                     models.DeleteAliasOperation(
    #                         delete_alias=models.DeleteAlias(alias_name=alias_name)
    #                     ),
    #                     models.CreateAliasOperation(
    #                         create_alias=models.CreateAlias(
    #                             collection_name=collection_name,
    #                             alias_name=alias_name
    #                         )
    #                     ),
    #                 ]
    #             )
                
    #             # Only delete the old collection after successfully updating alias
    #             try:
    #                 self.client.delete_collection(collection_name=previous_collection)
    #                 logger.info(f"Successfully deleted previous collection - {previous_collection}")
    #             except Exception as e:
    #                 logger.error(f"Failed to delete previous collection {previous_collection}: {str(e)}")
                
    #             logger.info(f"Switched alias to new collection - {collection_name}")
            
    #         # If no previous collection, just create the alias
    #         else:
    #             self.client.update_collection_aliases(
    #                 change_aliases_operations=[
    #                     models.CreateAliasOperation(
    #                         create_alias=models.CreateAlias(
    #                             collection_name=collection_name,
    #                             alias_name=alias_name
    #                         )
    #                     )
    #                 ]
    #             )
    #             logger.info(f"Created alias name - {alias_name} for collection - {collection_name}")
        
    #     except Exception as e:
    #         logger.error(f"Error managing aliases: {str(e)}")
    #         raise

    # def search(self, query: str, user_id: Optional[str] = None, limit: Optional[int] = None) -> List[Dict]:
    #     """Perform semantic search on chat history or database documents"""
    #     if limit is None:
    #         limit = self.search_limit
        
    #     collection_name = self._get_collection_name(user_id)
    #     query_embedding = self._get_embedding(query)
        
    #     # Search in Qdrant
    #     result = self.client.search(
    #         collection_name=collection_name,
    #         query_vector=query_embedding,
    #         limit=limit,
    #         with_payload=True
    #     )
        
    #     return [hit.payload for hit in result]