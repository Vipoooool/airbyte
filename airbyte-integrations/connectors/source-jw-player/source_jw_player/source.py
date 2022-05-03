#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream

# Basic full refresh stream
class JwPlayerStream(HttpStream):
    url_base = "https://api.jwplayer.com/v2/"

    primary_key = None

    def __init__(self, api_secret: str, site_id: str, **kwargs):
        super().__init__(**kwargs)
        self.api_secret = api_secret
        self.site_id = site_id

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        """
        Override this method to define the query parameters that should be set on an outgoing HTTP request given the inputs.

        E.g: you might want to define query parameters for paging if next_page_token is not None.
        """
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        TODO: Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        return [response.json()]

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

class JwMedia(JwPlayerStream):

    def __init__(self, api_secret: str, site_id: str, media_id: str, **kwargs):
        super().__init__(api_secret, site_id, **kwargs)
        self.media_id = media_id
    
    def request_headers(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) -> Mapping[str, Any]:
        return {
            "Accept": "application/json",
            "Authorization": self.api_secret,
        }
        
    def path(self, **kwargs) -> str:
        return f"sites/{self.site_id}/media/{self.media_id}/"

class JwTag(JwPlayerStream):

    def __init__(self, api_secret: str, site_id: str, tag_name: str, **kwargs):
        super().__init__(api_secret, site_id, **kwargs)
        self.tag_name = tag_name
        
    def path(self, **kwargs) -> str:
        return f"sites/{self.site_id}/remove_tag/"

    def request_headers(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) -> Mapping[str, Any]:
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": self.api_secret,
        }

    @property
    def http_method(self) -> str:
        return "PUT" 

    def request_body_json(self, **kwargs) -> Optional[Mapping]:
        return {"tag": self.tag_name}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        TODO: Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        return [{"Status": response.status_code, "tag": self.tag_name}]


# Source
class SourceJwPlayer(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        api_secret = config.get("api_secret")

        if api_secret.isdigit():
            return False, f"Api token {api_secret} is invalid, please provide a valid token!"
        
        else:
            return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        TODO: Replace the streams below with your own streams.

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        jwp_streams = [
            JwMedia(config.get('api_secret'), config.get('site_id'), config.get('media_id')),
            JwTag(config.get('api_secret'), config.get('site_id'), config.get('tag_name'))
            ]
        return jwp_streams
