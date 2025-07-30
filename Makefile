server:
	-python src/core/server.py

client:
	-python src/core/client.py

check:
	-pre-commit run --all-files
