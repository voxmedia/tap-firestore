"""Custom client handling, including FirestoreStream base class."""

from __future__ import annotations

from typing import Iterable

import firebase_admin
from firebase_admin import credentials, firestore
from singer_sdk.streams import Stream


class FirestoreStream(Stream):
    """Stream class for Firestore streams."""

    def _pagination_field_for_collection(self, collection_name: str) -> str | None:
        """Return the pagination key for a given collection name."""
        pagination_fields = [
            val for val in self.config.get("pagination_fields", [])
            if val["collection"] == collection_name
        ]
        if len(pagination_fields) == 0:
            return None
        if len(pagination_fields) > 1:
            raise ValueError(
                f"Multiple pagination fields found for collection {collection_name}. "
                f"Ensure that the `pagination_fields` config has only one entry per "
                f"collection."
            )
        return pagination_fields[0]["field_name"]

    def sync_batch(self, pagination_field: str):
        db = firestore.client()
        query = (
            db.collection(self.name)
            .order_by(pagination_field)
            .limit(self.config["pagination_limit"])
        )
        for doc in query.stream():
            yield {"_id": doc.id, "document": doc.to_dict()}

    def get_records(self, context: dict | None) -> Iterable[dict]:
        """Return a generator of record-type dictionary objects.

        The optional `context` argument is used to identify a specific slice of the
        stream if partitioning is required for the stream. Most implementations do not
        require partitioning and should ignore the `context` argument.

        Args:
            context: Stream partition or context dictionary.
        """
        # TODO: should any of this live in the tap class?
        creds = credentials.Certificate(self.config["service_account_path"])
        try:  # TODO: improve this
            firebase_admin.initialize_app(creds)
        except ValueError:
            pass
        db = firestore.client()

        pagination_field = self._pagination_field_for_collection(self.name)
        if pagination_field:
            query = (
                db.collection(self.name)
                .order_by(pagination_field)
                .limit(self.config["pagination_limit"])
            )
            for doc in query.stream():
                yield {"_id": doc.id, "document": doc.to_dict()}
            is_complete = len(list(query.stream())) < self.config["pagination_limit"]
            try:
                start_after_val = list(query.stream())[-1].to_dict()[pagination_field]
            except IndexError:
                is_complete = True

            while not is_complete:
                query = (
                    db.collection(self.name)
                    .order_by(pagination_field)
                    .start_after({pagination_field: start_after_val})
                    .limit(self.config["pagination_limit"])
                )
                for doc in query.stream():
                    yield {"_id": doc.id, "document": doc.to_dict()}
                is_complete = len(list(query.stream())) < self.config["pagination_limit"]
                try:
                    start_after_val = list(query.stream())[-1].to_dict()[pagination_field]
                except IndexError:
                    is_complete = True

        else:
            docs = db.collection(self.name).start_after().stream()
            for doc in docs:
                yield {"_id": doc.id, "document": doc.to_dict()}