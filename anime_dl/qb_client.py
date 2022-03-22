from qbittorrent import Client

import os

# TODO: Port inotify to this class so then the pause and resume functions can be private
class QbitClient():

	def __init__(self):
		# TODO: Move login info to params for class
		self.qb = Client('http://127.0.0.1:8080/', verify=False)
		self.qb.login(os.environ['qbitt_user'], os.environ['qbitt_pass'])

	def download_torrent(self, torrent, save_dir) -> Client:

		self.pause_other_torrents()

		self.qb.download_from_link(
			torrent['download_url'],
			savepath=save_dir
		)


		# Must find torrent that just begun downloading
		not_found = True
		while not_found:
			active_torrents = self.qb.torrents()
			for active_torrent in active_torrents:
				# Found torrent. break
				if torrent['name'] == active_torrent['name']:
					self.torrent_hash = active_torrent['hash']
					not_found = False
					break # Don't need to iterate entire list

	def pause_other_torrents(self) -> bool:
		active_torrents = self.qb.torrents(filter='downloading')

		for active_torrent in active_torrents:
			self.qb.pause(active_torrent['hash'])

	def resume_other_torrents(self) -> None:
		paused_torrents = self.qb.torrents(filter='downloading')

		for paused_torrent in paused_torrents:
			self.qb.resume(paused_torrent['hash'])

	def get_all_torrents(self) -> list[dict]:
		return self.qb.torrents()

	def get_torrent_info(self) -> dict:
		torrents_list = self.qb.torrents()

		for torrent in torrents_list:
			if self.torrent_hash == torrent['hash']:
				return torrent




