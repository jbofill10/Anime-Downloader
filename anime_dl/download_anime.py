from cli.cli import run_cli
from scraper.nyaa import NyaaScraper
from parser.nyaa_parser import parse_payload
from dotenv import load_dotenv
from qbittorrent import Client

import os

load_dotenv()

def main():

	nyaa = NyaaScraper('Kill La Kill', '1080p', batch=True)

	res = nyaa.run_query()

	parsed_payload = parse_payload(res)

	download_torrents(parsed_payload)

	# run_cli()

def download_torrents(torrents):
	qb = Client('http://127.0.0.1:8080/', verify=False)
	qb.login(os.environ['qbitt_user'], os.environ['qbitt_pass'])

	for torrent in torrents:
		print(torrent['download_url'])
		qb.download_from_link(torrent['download_url'], savepath=os.environ['save_path'])


if __name__ == '__main__':
	main()