#!/bin/bash
set -e;

IMAGES_PATH='data/images/';
IMAGES=($(ls $IMAGES_PATH));
RAMDISK="$(pwd)/data/ramdisk"
RESULTS="$(pwd)/data/results"
mkdir -p "$RESULTS"
APK_PATH="$RAMDISK/apks"

image=$1

# Setup MYSQL for the Test cases script
sudo docker container rm -f db || true;
sudo docker network rm -f testcases || true;
echo "[+] Removed old containers and networks"

sudo docker network create testcases;
sudo docker run -it -e MYSQL_RANDOM_ROOT_PASSWORD=1 -e MYSQL_USER=masa_script -e MYSQL_PASSWORD=MASA123 -e MYSQL_DATABASE=automated_MASA --name db --network testcases -d mysql:8
echo "[+] Created the network and started the MySQL database"

# Setup the Test Cases database (initial wait required for service discovery to wake up)
sudo docker run --rm --network testcases --name testcases-setup -it android-scoring-testcases:latest python3 -c "import time; time.sleep(15); from db.database_utils import first_execution; first_execution()"
echo "[+] Created the Test Cases database"

if [ "$image" == "True" ]; then 

  sudo rm -r "$APK_PATH"/*

  for DIRECTORY in "${IMAGES[@]}"; do
    VENDOR_DIR="$IMAGES_PATH$DIRECTORY"
    if [ -d "$VENDOR_DIR" ]; then
      VENDOR_IMAGES=($(ls "$VENDOR_DIR"))
      for IMAGE in "${VENDOR_IMAGES[@]}"; do
        IMAGE_PATH="$VENDOR_DIR/$IMAGE"
        sudo docker run -v "$(pwd)/data/:/usr/src/app/data" -it android-scoring-extractor:latest "$IMAGE_PATH" "$DIRECTORY" "data/ramdisk"
        echo "[+] Extracted the firmware image $IMAGE_PATH"
        EXTRACTED_IMAGE_PATH="$RAMDISK/$IMAGE.extracted"
        
        IMAGE="${IMAGE/.zip/}"
        IMAGE="${IMAGE/.rar/}"
        APKS=($(sudo find "$EXTRACTED_IMAGE_PATH" -name "*.apk"))
        mkdir -m 777 -p "$APK_PATH"
        mkdir -m 777 -p "$APK_PATH/$IMAGE"
        # Run the Test Cases script
        for APK in "${APKS[@]}"; do
          sudo mv "$APK" "$APK_PATH/$IMAGE"
        done;
        APK_FILES=($(sudo find $APK_PATH/$IMAGE -type f -name \*.apk))
        for APK in "${APK_FILES[@]}"; do
          DIR="${APK/.apk/}"
          mkdir -p "$DIR"
          mv "$APK" "$DIR"
        done;
        sudo rm -r "$EXTRACTED_IMAGE_PATH"

        if [ ! -d "$APK_PATH/$IMAGE/Results" ]; then
          # Create Results folder
          mkdir -m 777 -p "$APK_PATH/$IMAGE/Results"
        fi
          
        sudo docker run -v "$APK_PATH/$IMAGE:/usr/src/app/apks" -v "$APK_PATH/$IMAGE/Results:/usr/src/app/Results" --rm --network testcases --name testcases-setup -it android-scoring-testcases:latest /bin/bash automate_apps_updated 1
        echo "[+] Ran the TestCases script" 

        folder_results=$(ls "$APK_PATH/$IMAGE/Results/" -1 | head -n 1)

        sudo mv "$APK_PATH/$IMAGE/Results/$folder_results" "$RESULTS/"
       
      done;
    fi
  done;

else

  if [ ! -d "$APK_PATH" ]; then
      echo "The specified directory does not exist."
      return 1
  fi

  for apk_file in "$APK_PATH"/*.apk; do
    if [ -f "$apk_file" ]; then
      apk_name="${apk_file##*/}"
      apk_name="${apk_name%.apk}"
      folder_name="${APK_PATH}/${apk_name}"

      if [ ! -d "$folder_name" ]; then
          mkdir -m 777 -p "$folder_name"
      fi

      mv "$apk_file" "$folder_name"
    fi
  done
    
  uuid=$(sudo docker run -v "$APK_PATH:/usr/src/app/apks" -v "$APK_PATH/Results:/usr/src/app/Results" --rm --network testcases --name testcases-setup -it android-scoring-testcases:latest /bin/bash automate_apps_updated 1 | tee /dev/tty | grep "UUID:" | awk '{print $2}')
  echo "[+] Ran the TestCases script" 

  folder_results=$(ls "$APK_PATH/Results/" -1 | head -n 1)

  sudo mv "$APK_PATH/Results/$folder_results" "$RESULTS/"

  sudo rm -rf "$APK_PATH/Results/"
  
fi
