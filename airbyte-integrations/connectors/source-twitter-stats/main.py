#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_twitter_stats import SourceTwitterStats

if __name__ == "__main__":
    source = SourceTwitterStats()
    launch(source, sys.argv[1:])
