start:
	bundle exec jekyll serve --config _config.yml,_config.dev.yml --watch >/dev/null 2>&1 &

stop:
	pkill -f jekyll

restart: stop start
