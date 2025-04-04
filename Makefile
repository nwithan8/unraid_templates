# template_check_unix: Check if a template exists on the Community Apps store
# @param name - The name of the template to check
template_check_unix:
	./scripts/.venv/bin/python3 ./scripts/template_already_exists.py $(name)
