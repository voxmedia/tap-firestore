"""Firestore tap class."""

from __future__ import annotations

import firebase_admin
from firebase_admin import credentials, firestore
from singer_sdk import Tap
from singer_sdk import typing as th  # JSON schema typing helpers
from singer_sdk._singerlib.catalog import Catalog, CatalogEntry

# TODO: Import your custom stream types here:
from tap_firestore import streams


class TapFirestore(Tap):
    """Firestore tap class."""

    name = "tap-firestore"

    # TODO: Update this section with the actual config values you expect:
    config_jsonschema = th.PropertiesList(
        th.Property(
            "service_account_path",
            th.StringType,
            required=True,
            description="File path to GCP Service Account JSON file",
        ),
        th.Property(
            "start_date",
            th.DateTimeType,
            description="The earliest record date to sync",
        ),
        th.Property(
            "pagination_fields",
            th.ArrayType(
                th.ObjectType(
                    th.Property("collection", th.StringType, required=True),
                    th.Property("field_name", th.StringType, required=True),
                )
            ),
            description="List of fields to use for pagination. Each list element is an "
                        "object with `collecction` (the name of the collection) and "
                        "`field_name` (the field to use for paginating through that "
                        "collection. If not provided for a collection, the tap will"
                        "attempt to fetch all documents without pagination, which could"
                        "result in 5xx errors from Firestore.",
        ),
        th.Property(
            "pagination_limit",
            th.IntegerType,
            description="The maximum number of documents to fetch per page. Defaults "
                        "to 10000. If you are getting 5xx errors from Firestore, try "
                        "reducing this value.",
            default=10_000,
        ),
    ).to_dict()

    @property
    def catalog_dict(self) -> dict:
        """Returns the tap catalog as a dictionary."""
        # Use cached catalog if available
        if hasattr(self, "_catalog_dict") and self._catalog_dict:
            return self._catalog_dict
        # Defer to passed in catalog if available
        if self.input_catalog:
            return self.input_catalog.to_dict()

        # If no catalog is provided, discover streams
        catalog = Catalog()
        creds = credentials.Certificate(self.config["service_account_path"])
        try:  # TODO: improve this
            firebase_admin.initialize_app(creds)
        except ValueError:
            pass
        db = firestore.client()

        for collection in db.collections():
            entry = CatalogEntry.from_dict(
                {"tap_stream_id": collection.id, "key_properties": ["_id"]}
            )
            schema = {
                "type": "object",
                "description": "The document from the Firestore collection",
                "properties": {
                    "_id": {
                        "type": ["string", "null"],
                        "description": "The document ID",
                    },
                    "document": {
                        "type": "object",
                        "additionalProperties": True,
                        "description": "The document from the Firestore collection",
                    }
                },
            }
            entry.schema = entry.schema.from_dict(schema)
            entry.metadata = entry.metadata.get_standard_metadata(
                schema=schema,
                key_properties=["_id"],
            )
            catalog.add_stream(entry)

        self._catalog_dict = catalog.to_dict()
        return self._catalog_dict

    def discover_streams(self) -> list[streams.FirestoreStream]:
        """Return a list of discovered streams.

        Returns:
            A list of discovered streams.
        """
        for entry in self.catalog.streams:
            stream = streams.FirestoreStream(
                tap=self,
                name=entry.tap_stream_id,
                schema=entry.schema,
            )
            stream.apply_catalog(self.catalog)
            yield stream


if __name__ == "__main__":
    TapFirestore.cli()
