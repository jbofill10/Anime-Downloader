from cli.cli import run_cli
from scraper.nyaa import NyaaScraper
from parser.nyaa_parser import parse_payload
from dotenv import load_dotenv
from qbittorrent import Client

import os

load_dotenv()

def main():

	responses = run_cli()
	print(responses)
	nyaa = NyaaScraper(
		responses['anime_name'],
		responses['anime_quality'],
		responses['anime_group'],
		responses['use_subs'],
		responses['torrent_type'],
		responses['min_video'],
		responses['max_video'],
		responses['batch'])

	res = nyaa.run_query()
	parsed_payload = parse_payload(res)

	print(parsed_payload)

def download_torrents(torrents):
	qb = Client('http://127.0.0.1:8080/', verify=False)
	qb.login(os.environ['qbitt_user'], os.environ['qbitt_pass'])

	for torrent in torrents:
		print(torrent['download_url'])
		anime_dir_name = input('Enter name of directory to save torrent in (keep it consistent with directory name in plex server): ')
		# TODO: CLI to decide whether torrent is Show, Movie, etc
		qb.download_from_link(torrent['download_url'], savepath=f"{os.environ['save_path']}/{anime_dir_name}")


if __name__ == '__main__':
	main()