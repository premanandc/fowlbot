#! /bin/sh

pushd extractor
scrapy crawl fowler -O ../article_headers.json
scrapy crawl article -O ../article_details.json
popd

python ingestor.py
