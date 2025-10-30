#!/usr/bin/python

import argparse
import xml.etree.ElementTree as ET
import re

def validate_template_file(template_file_path: str) -> bool:
    """
    Validates if the provided XML file has a valid Unraid app template configuration.

    :param template_file_path: Path to the XML file.
    :type template_file_path: str
    :return: True if valid, False otherwise. If invalid, an error message is printed.
    :rtype: bool
    """
    try:
        with open(template_file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        content = content.strip()

        # If not valid XML, return False
        if not content.startswith('<?xml'):
            print("Error: The file is not a valid XML file.")
            return False

        try:
            xml_data = ET.fromstring(content)
        except ET.ParseError as e:
            print(f"Error: XML parsing error: {e}")
            return False

        # Check that the port in WebUI is listed in a Config Port element
        webui_element = xml_data.find('WebUI')
        if webui_element is not None:
            webui_text = webui_element.text or ""
            if not re.match(r'^http(s)?://\[IP\]:\[PORT:\d+\]', webui_text):
                print("Error: WebUI element does not match the required format 'http(s)://[IP]:[PORT:<port_number>]'.")
                return False

            port_number = re.search(r'\[PORT:(\d+)\]', webui_text)
            if not port_number:
                print("Error: WebUI element does not contain a valid port number.")
                return False

            webui_port = port_number.group(1).strip()

            # Find the matching Config element with Type 'Port' and Target matching the port number
            port_number_regex = re.compile(r'-?' + webui_port + r'-?')  # Matches 1234 (single port) or *-1234-* (port range starting/ending with port)
            matching_port_config = [config for config in xml_data.findall('.//Config') if config.get('Type').lower().strip() == 'port' and (config.get('Target') is not None and re.findall(port_number_regex, config.get('Target').strip()))]
            if not matching_port_config:
                print(f"Error: No Config element with Type 'Port' and Target '{webui_port}' matching a defined WebUI port.")
                return False

            # TODO: Add more validation checks as needed

        return True

    except FileNotFoundError:
        print(f"Error: File {template_file_path} not found.")
        return False
    except Exception as e:
        print(f"Error: An unexpected error occurred: {e}")
        return False




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check if provided XML file has valid Unraid app template configuration.")
    parser.add_argument(
        type=str,
        help="Path to the app template XML file to validate.",
        dest="template_file",
    )
    args = parser.parse_args()

    is_valid = validate_template_file(template_file_path=args.template_file)
    if not is_valid:
        print(f"{args.template_file} failed validation")
        exit(1)

    print(f"{args.template_file} passed validation")
    exit(0)
