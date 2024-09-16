import sys
import yaml 
import re

from db import database_utils

def match_fingerprint_line(line):
    pattern = r'^ro\..+\.build\.fingerprint'
    return re.match(pattern, line) is not None

def extract_metadata_device():
    metadata = {}

    with open('data/apks/build.prop', 'r') as file:
        for line in file:
            if match_fingerprint_line(line):
                _, fingerprint = line.split('=')
                fingerprint = fingerprint.strip()

                brand, device, name, version_release, build_id, version_incremental, build_type, tags = fingerprint.replace(':', '/').split('/')

                metadata = {
                    'brand': brand,
                    'device': device,
                    'name': name,
                    'version_release': version_release,
                    'id': build_id,
                    'version_incremental': version_incremental,
                    'type': build_type,
                    'tags': tags
                }

                break 

    return metadata

def extract_metadata_config():
    with open('config/methods_config.yml') as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)

    return config.get("metadata", {})

def main():

    metadata = {}

    if image:
        metadata = extract_metadata_device()
    else:
        metadata = extract_metadata_config()

    database_utils.insert_metadata(id_execution, metadata["brand"], metadata["device"], metadata["name"], metadata["version_release"], metadata["id"], metadata["version_incremental"], metadata["type"], metadata["tags"])

if __name__ == "__main__":

    id_execution = sys.argv[1]
    image = sys.argv[2] if len(sys.argv) > 2 else None

    try:

        sys.exit(main())

    except Exception as e:
        print(e)