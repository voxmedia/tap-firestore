"""Tests standard tap features using the built-in SDK tests library."""

import datetime
import os

from singer_sdk.testing import get_tap_test_class

from tap_firestore.tap import TapFirestore


SAMPLE_CONFIG = {
    "start_date": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d"),
    "service_account_path": os.getenv(
        "TAP_FIRESTORE_SERVICE_ACCOUNT_PATH",
        ".secrets/service_account.json",
    )
    # TODO: Initialize minimal tap config
}


# Run standard built-in tap tests from the SDK:
TestTapFirestore = get_tap_test_class(
    tap_class=TapFirestore,
    config=SAMPLE_CONFIG
)


# TODO: Create additional tests as appropriate for your tap.
