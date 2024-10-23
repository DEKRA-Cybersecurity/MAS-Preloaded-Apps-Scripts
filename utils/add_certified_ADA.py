import yaml
import json
import os 
import sys

def add_certified_apps_to_json(yaml_file, json_file):
    with open(yaml_file, 'r') as file:
        yaml_data = yaml.safe_load(file)
    
    certified_apps = yaml_data.get('certified_apps', [])
    
    with open(json_file, 'r') as file:
        json_data = json.load(file)
    
    for app in certified_apps:
        new_certificate = {
            "packageName": app
        }
        json_data['certificates'].append(new_certificate)
    
    with open(json_file, 'w') as file:
        json.dump(json_data, file, indent=4)

if __name__ == "__main__":

    config_file = os.path.join(sys.argv[1])
    cert_json = os.path.join(sys.argv[2])
    
    add_certified_apps_to_json(config_file, cert_json)
