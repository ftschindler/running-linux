.PHONY: all build serve clean

all: bootstrap build

build: bootstrap
	@echo "building site ..."
	@npx quartz build -o _site -v
	@echo "site available in _site/ or via 'make serve'"

serve: bootstrap
	@echo "building and serving site ..."
	NODE_ENV=development npx quartz build -o _site -v --serve

bootstrap: .bootstrapped

.quartz/README.md:
	@echo "Initializing git submodules..."
	@git submodule update --init

.bootstrapped: .quartz/README.md
	@echo -n "pulling quartz infrastructure out of .quartz ... "
	@cd .quartz && for file in $$(ls *.ts *.json) .node-version .npmrc .prettierignore .prettierrc quartz; do \
		if [ ! -e ../$$file ]; then \
			cp -r $$file ../; \
		fi \
	done
	@echo "done"
	@echo "installing quartz with dependencies ..."
	@npm ci
	@touch .bootstrapped
	@echo "run 'make build' or 'make serve' next"

clean:
	rm -rf _site .bootstrapped
