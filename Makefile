## feel.Makefile: commands for generating a low-memory CSV filter CLI called feel

.DEFAULT_GOAL := help
TARGET_MAX_CHAR_NUM=20
# COLORS
ifneq (,$(findstring xterm,${TERM}))
	BLACK        := $(shell tput -Txterm setaf 0 || exit 0)
	RED          := $(shell tput -Txterm setaf 1 || exit 0)
	GREEN        := $(shell tput -Txterm setaf 2 || exit 0)
	YELLOW       := $(shell tput -Txterm setaf 3 || exit 0)
	LIGHTPURPLE  := $(shell tput -Txterm setaf 4 || exit 0)
	PURPLE       := $(shell tput -Txterm setaf 5 || exit 0)
	BLUE         := $(shell tput -Txterm setaf 6 || exit 0)
	WHITE        := $(shell tput -Txterm setaf 7 || exit 0)
	RESET := $(shell tput -Txterm sgr0)
else
	BLACK        := ""
	RED          := ""
	GREEN        := ""
	YELLOW       := ""
	LIGHTPURPLE  := ""
	PURPLE       := ""
	BLUE         := ""
	WHITE        := ""
	RESET        := ""
endif

## show usage / common commands available
.PHONY: help
help:
	@printf "\n${PURPLE}common${RESET}: collection of commands to simplify running common Docker containers\n\n"
	@printf "${RED}cmds:\n\n";

	@awk '{ \
			if ($$0 ~ /^.PHONY: [a-zA-Z\-\_0-9]+$$/) { \
				helpCommand = substr($$0, index($$0, ":") + 2); \
				if (helpMessage) { \
					printf "  ${LIGHTPURPLE}%-$(TARGET_MAX_CHAR_NUM)s${RESET} ${GREEN}%s${RESET}\n\n", helpCommand, helpMessage; \
					helpMessage = ""; \
				} \
			} else if ($$0 ~ /^[a-zA-Z\-\_0-9.]+:/) { \
				helpCommand = substr($$0, 0, index($$0, ":")); \
				if (helpMessage) { \
					printf "  ${BLUE}%-$(TARGET_MAX_CHAR_NUM)s${RESET} ${GREEN}%s${RESET}\n", helpCommand, helpMessage; \
					helpMessage = ""; \
				} \
			} else if ($$0 ~ /^##/) { \
				if (helpMessage) { \
					helpMessage = helpMessage"\n                     "substr($$0, 3); \
				} else { \
					helpMessage = substr($$0, 3); \
				} \
			} else { \
				if (helpMessage) { \
					print "\n${YELLOW}             "helpMessage"\n" \
				} \
				helpMessage = ""; \
			} \
		}' \
		$(MAKEFILE_LIST)


## -- shell commands --

# general config
ifeq ($(parser_in),)
parser_in := /Users/abenezer.mamo/Klaviyo/personal/packages/sirch/parser/content
endif
ifeq ($(parser_out),)
parser_out := /Users/abenezer.mamo/Klaviyo/personal/packages/sirch/site/content/post
endif
ifeq ($(input_path),)
input_path := /Users/abenezer.mamo/Klaviyo/Repos/eng-handbook/
endif
ifeq ($(output_path),)
output_path := /Users/abenezer.mamo/Klaviyo/personal/packages/sirch/parser/content
endif
ifeq ($(root_path),)
root_path := /Users/abenezer.mamo/Klaviyo/Repos/eng-handbook
endif

## install deps
deps:
	@python3 -m pip install -U pip setuptools wheel
	@python3 -m pip install -r requirements.txt

## format cli
format:
	@python3 -m black src
	@python3 -m black tests

## lint cli
lint:
	@python3 -m pylint src
	@python3 -m pylint tests

## build cli
build:
	@python3 -m setup build

## install cli
install:
	@python3 -m setup install
