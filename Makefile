start:
	bundle exec jekyll serve --config _config.yml,_config.dev.yml --watch >/dev/null 2>&1 &
	@echo Test site should be available at http://127.0.0.1:4000/yadm/

stop:
	pkill -f jekyll

restart: stop start
