#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import Oauth2Authenticator

SCOPES = ["https://www.googleapis.com/auth/yt-analytics.readonly",
          "https://www.googleapis.com/auth/youtube"]

# Basic full refresh stream
class YoutubeStatsStream(HttpStream, ABC):

    url_base = "https://youtubeanalytics.googleapis.com/v2/reports"
    primary_key = None

    def __init__(self, params, authenticator = None):
        super().__init__(authenticator)
        self.params = params

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return self.params

    def path(self, **kwargs) -> str:
        return ""

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield response.json()


# Basic incremental stream
class IncrementalYoutubeStatsStream(YoutubeStatsStream, ABC):
    """
    TODO fill in details of this class to implement functionality related to incremental syncs for your connector.
         if you do not need to implement incremental sync for any streams, remove this class.
    """

    # TODO: Fill in to checkpoint stream reads after N records. This prevents re-reading of data if the stream fails for any reason.
    state_checkpoint_interval = None

    @property
    def cursor_field(self) -> str:
        """
        TODO
        Override to return the cursor field used by this stream e.g: an API entity might always use created_at as the cursor field. This is
        usually id or date based. This field's presence tells the framework this in an incremental stream. Required for incremental.

        :return str: The name of the cursor field.
        """
        return []

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Override to determine the latest state after reading the latest record. This typically compared the cursor_field from the latest record and
        the current state and picks the 'most' recent cursor. This is how a stream's state is determined. Required for incremental.
        """
        return {}


# Source
class SourceYoutubeStats(AbstractSource):
    @staticmethod
    def get_authenticator(config):
        credentials = config["credentials"]
        client_id = credentials["client_id"]
        client_secret = credentials["client_secret"]
        refresh_token = credentials["refresh_token"]

        return Oauth2Authenticator(
            token_refresh_endpoint="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=refresh_token,
            scopes=SCOPES
        )

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        authenticator = self.get_authenticator(config)
        try:
            access_token = authenticator.get_access_token()
        except Exception as err:
            logger.exception(err)
            return False, str(err)
        else:
            return True, access_token

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        authenticator = self.get_authenticator(config)
        return [YoutubeStatsStream(config["params"], authenticator)]
