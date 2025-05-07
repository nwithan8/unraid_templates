# template_check_unix: Check if a template exists on the Community Apps store
# @param name - The name of the template to check
template_check_unix:
	./scripts/.venv/bin/python3 ./scripts/template_already_exists.py $(name)

# template_validate_unix: Validate the template using the XML XSD validator
# @param name - The name of the template to validate
template_validate_unix:
	node ./xml-xsd-validator/cli.js ./templates/template_schema.xsd ./templates/$(name).xml

# copy_placeholder_unix: Copy the placeholder template for the new app
# @param name - The name of the new app
copy_placeholder_unix:
	cp images/placeholder-icon.png images/$(name)-icon.png
	git add images/$(name)-icon.png
