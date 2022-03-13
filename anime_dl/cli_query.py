#! /bin/python3

from unittest import result
from scraper.nyaa import NyaaScraper
from parser.nyaa_parser import parse_payload
from pprint import PrettyPrinter
from dotenv import load_dotenv
from qbittorrent import Client

import argparse
import os
import subprocess
import sys
import time

load_dotenv()

parser = argparse.ArgumentParser(description='Query episodes without GUI')

parser.add_argument('-n', '--name', help='Episode name to query', required=True)
parser.add_argument('-q', '--quality', help='Quality of episode', choices=['480', '720', '1080'], required=False)
parser.add_argument('-u', '--uploader', help='Torrent uploader', required=False)
parser.add_argument('-num', '--number', help='Episode number', required=False)
parser.add_argument('-t', '--test', help='Test your query without downloading the torrent. Will override errors from episode number', required=False, action='store_true')
parser.add_argument('-s', '--save_location', help='Save location of torrent ** SHOULD MATCH LAYOUT OF PLEX IF THAT MATTERS **', required=False)

args = parser.parse_args()


pp = PrettyPrinter()

def main():

	search = args.name
	quality = args.quality
	uploader = list() if not args.uploader else [args.uploader]
	ep_num = args.number if args.number else ''
	test_query = args.test
	save_location = args.save_location
	torrent_save_path = f"{os.environ['save_path']}/{save_location}"
	plex_location = os.environ['plex_location']

	if not save_location and not test_query:
		print('You must enter a save location if not doing a test query!')
		sys.exit(1)

	if save_location:
		anime_name = os.path.dirname(save_location)
		season = os.path.basename(save_location).split()[1]
		top_level_save_dir = f"{os.environ['save_path']}/{anime_name}"

	result = NyaaScraper(f'{search} {ep_num}', quality, uploader).run_query()
	parsed_payload = parse_payload(result)

	if test_query:
		for torrent in parsed_payload:
			print()
			pp.pprint(torrent)
			print()
		sys.exit(0)

	# No torrents found
	if not len(parsed_payload) >= 1:
		print('No torrents found given the query!')
		sys.exit(8)

	else:
		# The torrent the user potentially wants
		if len(parsed_payload) == 0:
			print('No torrents found')
			sys.exit(10)
		query_target = None
		for torrent in parsed_payload:
			# torrent name without any hidden mkv naming schemes
			pure_name = [text for text in torrent['name'].split() if not invalid_torrent_name(text)]
			if ep_num in pure_name:
				query_target = torrent

		if query_target == None:
			print('Torrents Found, but couldn\'t resolve to a single torrent!')
			for torrent in parsed_payload:
				print()
				pp.pprint(torrent)
				print()
			sys.exit(9)

	# Ensure saved directory already exists so inotify can properly initialize
	os.makedirs(torrent_save_path, exist_ok=True)

	# Initialize listener on torrent directory
	process = subprocess.Popen(['inotifywait', '-m', torrent_save_path], stdout=subprocess.PIPE)

	# Download torrent once inotify has been initialized
	qb = download_torrent(query_target, torrent_save_path)

	# Wait for torrent to finish
	while True:
		stdout = str(process.stdout.readline(), 'utf-8')
		# Torrent is done downloading, leave loop
		if 'CLOSE_WRITE,CLOSE' in stdout:
			time.sleep(2) # Give time to the torrent to fully finish -- possibly not needed
			break

	# Need to wait on all subproccess statements, otherwise mkvs might suffer some form of corruption

	# Conform to plex naming standards
	subprocess.Popen(fr"mv '{torrent_save_path}/{query_target['name']}' '{torrent_save_path}/{anime_name} - s{season}e{ep_num}-.mkv'", shell=True).wait()

	# Move to plex library
	# Raw string to preserve spaces
	# Need to wait for copy to finish before progressing
	subprocess.Popen(fr"cp -r '{top_level_save_dir}' '{plex_location}'", shell=True).wait()

	os.system(fr"rm -rf '{os.path.dirname(torrent_save_path)}'")

	# Need to give access for plex to read
	subprocess.Popen(fr"chmod -R 777 '{plex_location}/{anime_name}'", shell=True).wait()

	active_torrents = qb.torrents()

	for active_torrent in active_torrents:
		if query_target['name'] == active_torrent['name']:
			print('Episode: ' + ep_num + ' MATCH')
			qb.delete(active_torrent['hash'])

	with open(f'{plex_location}/{save_location}/.lastest_ep', 'w') as latest_ep_file:
		latest_ep_file.write(ep_num)

	sys.exit(0)

# Shitty text cleansing, will work for the most reputable torrent uploaders anyways
def invalid_torrent_name(text: str) -> bool:
	return '[' in text or ']' in text or '(' in text or ')' in text

# TODO: Move out of cli_query and download_anime into a separate file to deduplicate code usage
# a class is a good idea since several operations on the same torrent need to occur anyways
def download_torrent(torrent, save_dir) -> Client:
	qb = Client('http://127.0.0.1:8080/', verify=False)
	qb.login(os.environ['qbitt_user'], os.environ['qbitt_pass'])

	qb.download_from_link(
		torrent['download_url'],
		savepath=save_dir
	)

	return qb
if __name__ == '__main__':
	main()