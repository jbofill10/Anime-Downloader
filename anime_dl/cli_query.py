#! /bin/python3

from qb_client import QbitClient
from scraper.nyaa import NyaaScraper
from parser.nyaa_parser import parse_payload
from pprint import PrettyPrinter, pprint
from dotenv import load_dotenv

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
parser.add_argument('-v', '--verbose', help='Verbose logging for debugging purposes', required=False, action='store_true')

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
	verbose_logging = args.verbose

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

	qb = QbitClient()
	# Download torrent once inotify has been initialized
	qb.download_torrent(query_target, torrent_save_path)

	# Need to make sure torrent gets rechecked to download potentially missing pieces
	run_recheck = False
	# Wait for torrent to finish
	while True:
		torrent_info = qb.get_torrent_info()
		if verbose_logging:
			pp.pprint(torrent_info)

		# Torrent is done downloading, either recheck or exit loop
		if torrent_info['progress'] == 1:
			if not run_recheck:
				run_recheck = True
				qb.qb.recheck(qb.torrent_hash)
			else:
				time.sleep(2) # Give time to the torrent to fully finish -- possibly not needed
				break

	# Need to wait on all subproccess statements, otherwise mkvs might suffer some form of corruption

	# Conform to plex naming standards
	if verbose_logging:
		print(fr"mv '{torrent_save_path}/{query_target['name']}' '{torrent_save_path}/{anime_name} - s{season}e{ep_num}-.mkv'")
	subprocess.Popen(fr"mv '{torrent_save_path}/{query_target['name']}' '{torrent_save_path}/{anime_name} - s{season}e{ep_num}-.mkv'", shell=True).wait()

	# Move to plex library
	# Raw string to preserve spaces
	# Need to wait for copy to finish before progressing
	if verbose_logging:
		print(fr"mv '{torrent_save_path}/{query_target['name']}' '{torrent_save_path}/{anime_name} - s{season}e{ep_num}-.mkv'")
	subprocess.Popen(fr"cp -r '{top_level_save_dir}' '{plex_location}'", shell=True).wait()

	if verbose_logging:
		print(fr"rm -rf '{os.path.dirname(torrent_save_path)}'")
	os.system(fr"rm -rf '{os.path.dirname(torrent_save_path)}'")

	# Need to give access for plex to read
	if verbose_logging:
		print(fr"chmod -R 777 '{plex_location}/{anime_name}'")
	subprocess.Popen(fr"chmod -R 777 '{plex_location}/{anime_name}'", shell=True).wait()

	all_torrents = qb.get_all_torrents()

	# TODO: Move QbitClient class
	for qb_torrent in all_torrents:
		if verbose_logging:
			pp.pprint(qb_torrent)

		if query_target['name'] == qb_torrent['name']:
			if verbose_logging:
				print('Deleting torrent')
			qb.qb.delete(qb_torrent['hash'])

	# TODO: Move QbitClient class
	if verbose_logging:
		print('Resuming torrents')
	qb.resume_other_torrents()

	if verbose_logging:
		print(f'Writing latest ep file to: {plex_location}/{save_location}/.latest_ep')

	with open(f'{plex_location}/{save_location}/.latest_ep', 'w') as latest_ep_file:
		latest_ep_file.write(ep_num)

	sys.exit(0)

# Shitty text cleansing, will work for the most reputable torrent uploaders anyways
def invalid_torrent_name(text: str) -> bool:
	return '[' in text or ']' in text or '(' in text or ')' in text

if __name__ == '__main__':
	main()