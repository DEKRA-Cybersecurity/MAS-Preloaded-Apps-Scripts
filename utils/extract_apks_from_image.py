import os
import sys
import subprocess
import shutil
import glob

main_path = os.getcwd()


def find_zip_image(path):
    search_pattern = os.path.join(path, '*.zip')

    zip_files = glob.glob(search_pattern)

    if len(zip_files) == 1:
        return os.path.basename(zip_files[0])
    elif len(zip_files) == 0:
        raise FileNotFoundError(
            f"No .zip file was found in the directory {path}")
    else:
        raise FileExistsError(
            f"Several .zip files were found in the directory {path}")


def extract_image():

    os.chdir(and_scanner_path)
    command = ['python3', 'scan.py', image_path, apks_dir, '--extract']

    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        print('Image extraction completed successfully.')

    except Exception as e:
        print(e)


def get_apks():

    try:
        for root, dirs, files in os.walk(apks_dir, image_name):
            for file in files:
                if file.endswith('.apk'):
                    apk_path = os.path.join(root, file)

                    apk_name = os.path.splitext(file)[0]
                    apk_folder_path = os.path.join(apks_dir, apk_name)
                    os.makedirs(apk_folder_path, exist_ok=True)

                    new_apk_path = os.path.join(apk_folder_path, file)
                    shutil.copy2(apk_path, new_apk_path)

        shutil.rmtree(os.path.join(apks_dir, image_name+'.extracted'))
        print('APK extraction from the device image completed successfully.')

    except Exception as e:
        print(e)

def get_buildprop():

    filename = "build.prop"
    buildprop_path = ""

    for root, dirs, files in os.walk(apks_dir, image_name+'.extracted'):
        if filename in files:
            buildprop_path = os.path.join(root, filename)
    

    shutil.copy(buildprop_path, apks_dir)
    print("Build prop file extracted from image device.")
    

def main():

    print('Extracting apks from image device.')
    extract_image()
    os.chdir(main_path)
    get_buildprop()
    get_apks()


if __name__ == "__main__":

    vendor = sys.argv[1]
    vendor_path = os.path.join(main_path, 'data/images', vendor)
    apks_dir = os.path.join(main_path, 'data/apks')
    and_scanner_path = os.path.join(main_path, 'tools/AndScanner/')

    try:

        image_name = find_zip_image(vendor_path)
        image_path = os.path.join(main_path, vendor_path, image_name)

        sys.exit(main())

    except Exception as e:
        print(e)
