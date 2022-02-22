from cli.cli import run_cli

def main():
	twist = TwistScraper('kill-la-kill', False)

	episodes = twist.scrape_episode_urls()

	twist_decrypter(episodes)

	# run_cli()

if __name__ == '__main__':
	main()