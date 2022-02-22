from bs4 import BeautifulSoup

# TODO: Move to constants or something
NYAA_BASE_URL = 'https://nyaa.si'

def parse_payload(payload):

	parsed_payload = list()

	for query_result in payload:

		parsed_query = dict(
			name='',
			download_url='',
			torrent_size='',
			release_date=''

		)

		soup = BeautifulSoup(query_result.text, 'html.parser')
		torrent = soup.find('tr', {'class': 'success'})

		torrent_info = torrent.findAll('td', {'class': 'text-center'})
		links = torrent.findAll('a')

		parsed_query['name'] = links[2]['title']
		parsed_query['download_url'] = NYAA_BASE_URL + links[3]['href']
		parsed_query['torrent_size'] = torrent_info[1].text
		parsed_query['release_date'] = torrent_info[2].text

		parsed_payload.append(parsed_query)

	return parsed_payload

