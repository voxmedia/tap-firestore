"""Stream type classes for tap-firestore."""

from __future__ import annotations

from pathlib import Path

from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_firestore.client import FirestoreStream


# class UsersStream(FirestoreStream):
#     """Define custom stream."""
#
#     name = "users"
#     primary_keys = ["id"]
#     replication_key = None
#     # Optionally, you may also use `schema_filepath` in place of `schema`:
#     # schema_filepath = SCHEMAS_DIR / "users.json"
#     schema = th.PropertiesList(
#         th.Property("name", th.StringType),
#         th.Property(
#             "id",
#             th.StringType,
#             description="The user's system ID",
#         ),
#         th.Property(
#             "age",
#             th.IntegerType,
#             description="The user's age in years",
#         ),
#         th.Property(
#             "email",
#             th.StringType,
#             description="The user's email address",
#         ),
#         th.Property("street", th.StringType),
#         th.Property("city", th.StringType),
#         th.Property(
#             "state",
#             th.StringType,
#             description="State name in ISO 3166-2 format",
#         ),
#         th.Property("zip", th.StringType),
#     ).to_dict()
