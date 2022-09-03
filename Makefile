IGNORED := $(shell grep -v testenv .gitignore)
VOLUME_ARG =
COMPOSE_V2 = 0

ifeq ($(COMPOSE_V2),1)
	COMPOSE_COMMAND = docker compose
else
	COMPOSE_COMMAND = docker-compose
endif

.PHONY: all
all:
	@$(MAKE) usage | less

# Display usage for all make targets
.PHONY: usage
usage:
	@echo
	@echo 'make TARGET'
	@echo
	@echo 'TESTING'
	@echo
	@echo '  make test'
	@echo '    - Perform tests done by continuous integration.'
	@echo '      This target will:'
	@echo '        - Remove previously built data'
	@echo '        - Build the site'
	@echo '        - Test the site using html-proofer'
	@echo
	@echo '  make up'
	@echo '    - Start a container to locally test the website.'
	@echo '      This target will:'
	@echo '        - Start a jekyll container (re-using it if it already exists)'
	@echo '        - Expose the website on port 4000 of the local host'
	@echo
	@echo '  make logs'
	@echo '    - Tail the logs of the running jekyll container.'
	@echo
	@echo '  make restart'
	@echo '    - Restart the jekyll container.'
	@echo
	@echo '  make down'
	@echo '    - Shutdown and remove the jekyll container.'
	@echo
	@echo '  make clean'
	@echo '    - Remove previously built data and any jekyll containers.'
	@echo
	@echo '  make fresh'
	@echo '    - Like "make clean", but also removes the docker volumes.'
	@echo

.PHONY: test
test: require-docker-compose clean
	$(COMPOSE_COMMAND) run --rm website test/validate

.PHONY: up
up: require-docker-compose
	$(COMPOSE_COMMAND) up --no-recreate -d
	@echo
	@echo Started docker container. It will probably take a bit of time before
	@echo the webserver is listening. You can run \"make logs\" to watch the logs
	@echo of this container.
	@echo
	@echo The site will be served at http://0.0.0.0:4000/

.PHONY: logs
logs: require-docker-compose
	$(COMPOSE_COMMAND) logs --tail 0 -f

.PHONY: restart
restart: require-docker-compose
	$(COMPOSE_COMMAND) restart

.PHONY: down
down: require-docker-compose
	$(COMPOSE_COMMAND) down --remove-orphans ${VOLUME_ARG}

.PHONY: clean
clean: down
	rm -rf ${IGNORED}

.PHONY: fresh
fresh: VOLUME_ARG = -v
fresh: clean

.PHONY: require-docker-compose
require-docker-compose: require-docker
	@if [ "$(COMPOSE_V2)" = "0" ]; then \
	  if ! command -v "docker-compose" >/dev/null 2>&1; then \
		  echo "Sorry, this make target requires docker-compose to be installed. To use compose v2, re-run with COMPOSE_V2=1"; \
		  false; \
	  fi \
	else \
	  if ! $(COMPOSE_COMMAND) >/dev/null 2>&1; then \
		  echo "Sorry, this make target has been configured to support docker compose v2 but the compose subcommand isn't present in docker. To use docker-compose v1, remove the COMPOSE_V2 switch"; \
		  false; \
	  fi \
	fi

.PHONY: require-docker
require-docker:
	@if ! command -v "docker" >/dev/null 2>&1; then \
		echo "Sorry, this make target requires docker to be installed."; \
		false; \
	fi
