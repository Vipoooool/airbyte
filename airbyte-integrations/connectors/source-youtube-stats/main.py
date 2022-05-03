#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_youtube_stats import SourceYoutubeStats

if __name__ == "__main__":
    source = SourceYoutubeStats()
    launch(source, sys.argv[1:])
