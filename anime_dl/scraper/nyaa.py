import math
import requests

class NyaaScraper:

	NYAA_BASE_URL = 'https://nyaa.si'
	headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'}


	def __init__(self, search: str, ep_quality: str, anime_groups=list(), subs=True, ep_filter='Trusted' ,ep_start=1, ep_end=math.inf, batch=False) -> None:
		# Can only use either batch query or ep range
		if batch:
			ep_start = None
			ep_end = None

		self.search = search
		# Nyaa uses + for spaces in their query
		if ' ' in search:
			self.search = self.search.replace(' ', '+')

		if subs:
			self.subs = '1_2'
		else:
			self.subs='0_0'

		self.ep_quality = ep_quality
		self.anime_groups = anime_groups
		if ep_filter == 'Trusted':
			self.ep_filter = '2'
		self.ep_start = ep_start
		self.ep_end = ep_end
		self.batch = batch

		# Build search uri
		self.__build_uri()

	def __build_uri(self) -> None:
		self.query_uris = list()
		# TODO: Clean this up
		if len(self.anime_groups) > 1:
			for anime_group in self.anime_groups:
				self.query_uris.append(f'{self.NYAA_BASE_URL}/user/{anime_group}?f={self.ep_filter}&c={self.subs}&q={self.search}+{self.ep_quality}')
		else:
			self.query_uris.append(f'{self.NYAA_BASE_URL}/?f={self.ep_filter}&c={self.subs}&q={self.search}+{self.ep_quality}')

		self.query_uris = [query + '+batch' for query in self.query_uris if self.batch]
	def run_query(self):
		query_payload = list()
		for query in self.query_uris:
			print(query)
			query_payload.append(requests.get(query, headers=self.headers))
		return query_payload

