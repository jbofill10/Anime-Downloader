from rich.console import Console
from rich.prompt import IntPrompt, Prompt
from rich.prompt import Confirm

import sys

def run_cli() -> None:
	cli_responses = dict(
		anime_name=None,
		anime_quality=None,
		anime_group=list(),
		use_subs=True,
		torrent_type='Trusted',
		min_video=None,
		max_video=None,
		batch=False
	)

	c = Console()
	c.print('HELLO WEEB', style='blue')

	choice = IntPrompt.ask('HELLO WEEB, MAKE A DECISION\n1. Query Nyaa.si\n2. GO FUCK OFF\n')
	if choice == 2:
		sys.exit(0)

	if choice == 1:
		cli_responses['anime_name'] = Prompt.ask('What anime are you looking for? (use Japanese slug)')
		cli_responses['anime_quality'] = Prompt.ask('What quality? (leave empty if you don\'t care)')
		anime_group = Prompt.ask('Enter trusted torrent uploaders (csv)', default=list())
		if type(anime_group) == list:
			cli_responses['anime_group'] = anime_group
		else:
			cli_responses['anime_group'] += anime_group.split(',')
		cli_responses['use_subs'] = Confirm.ask('Do you want an anime with subs? [Y/n]\n', default=True)
		ep_search = IntPrompt.ask(
			'You can either pick to search for batch uploads or episode range\n' + \
			'1. Batch\n' + \
			'2. Episode Range\n'
		)

		if ep_search == 1:
			ep_search = 'batch'
		else:
			ep_search = 'range'

		if ep_search =='range':
			cli_responses['min_video'] = Prompt.ask('Starting episode (Leave blank for beginning of series)', default=1)
			cli_responses['max_video'] = Prompt.ask('Ending episode (Leave blank for maximum in series)', default=9999)

	return cli_responses



