help:
	@echo 'Makefile for test-protobuf-on-gae                      '
	@echo '                                                       '
	@echo 'Usage:                                                 '
	@echo '   make deploy         Deploy application to App Engine'

deploy:
	appcfg.py update application/ --application=${APP_ID} --version=${APP_VERSION}

.PHONY: deploy help
