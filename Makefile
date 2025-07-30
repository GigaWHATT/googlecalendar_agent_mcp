server:
	-python src/core/server.py

client:
	-python src/core/client.py

check:
	-pre-commit run --all-files

save:
	-git add .
	-make check
	-git add .
	-git commit -m "$(M)"
