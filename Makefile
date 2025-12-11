## help - Display help about make targets for this Makefile
help:
	@cat Makefile | grep '^## ' --color=never | cut -c4- | sed -e "`printf 's/ - /\t- /;'`" | column -s "`printf '\t'`" -t

## template_check_unix - Check if a template exists on the Community Apps store
# @param name - The name of the template to check
template_check_unix:
	./scripts/.venv/bin/python3 ./scripts/template_already_exists.py $(name)

## template_validate_unix - Validate the template using the XML XSD validator
# @param name - The name of the template to validate
template_validate_unix:
	node ./xml-xsd-validator/cli.js ./templates/template_schema.xsd ./templates/$(name).xml

## copy_to_unraid_unix - Copy the template to the Unraid server
# @param file - The file of the template to copy
copy_to_unraid_unix:
	sh ./scripts/copy_to_unraid.sh $(file)

## copy_placeholder_unix - Copy the placeholder template for the new app
# @param name - The name of the new app
copy_placeholder_unix:
	cp images/placeholder-icon.png images/$(name)-icon.png
	git add images/$(name)-icon.png

## copy_downloaded_icon - Copy a downloaded icon to the images folder
# @param name - The name of the new app
copy_downloaded_icon:
	mv ~/Downloads/$(name)-icon.png images/$(name)-icon.png
	git add images/$(name)-icon.png

## download_github_icon - Download an icon from a GitHub profile picture
# @param link - The GitHub profile link
# @param name - The name of the new app
download_github_icon:
	curl -s -o images/$(name)-icon.png $(link)
	git add images/$(name)-icon.png

## set_up_python - Set up the Python virtual environment and install dependencies
set_up_python:
	python3 -m venv scripts/.venv
	scripts/.venv/bin/pip install --upgrade pip
	scripts/.venv/bin/pip install -r scripts/requirements.txt

## font_awesome_icon - Download the Font Awesome icon for the app
# @param icon - Icon name from Font Awesome
# @param name - The name of the app
# @param category - The icon category (e.g., solid, regular, brands)
font_awesome_icon:
	sh ./scripts/font_awesome_icon.sh $(icon) $(name) $(category)

## validate_templates - Validate all templates in the templates folder
validate_templates:
	for template in ./templates/*.xml; do scripts/.venv/bin/python3 automation/template_validation/validate_app_config.py $$template; done

.PHONY: help template_check_unix template_validate_unix copy_placeholder_unix download_github_icon
