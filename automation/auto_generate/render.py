import yaml
from jinja2 import Environment, FileSystemLoader

# Load YAML file
with open('demo.yml', 'r') as yaml_file:
    yaml_data = yaml.safe_load(yaml_file)

# Set up Jinja2 environment
env = Environment(loader=FileSystemLoader(''))
template = env.get_template('template.j2')

# Render the template with YAML data
output = template.render(yaml_data)

# Save the rendered output to a file
with open('output.xml', 'w') as output_file:
    output_file.write(output)

print("Template applied successfully!")
