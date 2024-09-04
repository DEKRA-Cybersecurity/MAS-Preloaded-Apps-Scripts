#!/bin/bash

export PYTHONPATH=$(pwd)

hora_inicio=$(date +"%H:%M:%S")
actual_timestamp=$(date +'%Y-%m-%d %H:%M:%S.%6N')
uuid_execution=$(uuidgen)

path=$(pwd)
input=$1
apk_path='data/apks/*'
resultsPath='results/'

ADA_DIRECTORY="$path/data/"
ADA_JSON_FILE="certs.json"

if [ -n "$input" ] && [ "$input" == "test" ]; then 
	apk_path='unit_tests/reference_apk/*'
	uuid_execution='55555555-4444-3333-2222-111111111111'
	echo "Unit tests will be executed."
fi

if [ -n "$input" ] && [ "$input" != "test" ]; then 
    python3 utils/extract_apks_from_image.py "$input"
fi

python3 -c "from db.database_utils import insert_new_execution; insert_new_execution('$uuid_execution', '$actual_timestamp')"

getADAJson(){
	URL="https://appdefense-dot-devsite-v2-prod-3p.appspot.com/directory/data/certs.json"

	# Request to get JSON_FILE
	curl -s "$URL" -o "$ADA_DIRECTORY/$ADA_JSON_FILE"

	# Verify ADA_JSON_FILE was successfully downloaded
	if [ $? -eq 0 ]; then
	echo "App Defence Alliance results successfully saved."
	else
	echo "WARNING - There was a problem while downloading App Defence Alliance results."
	fi
}

jadxFunction()
{
	mkdir $absolute_dir/decompiled;

	python3 $path/utils/decompile_jadx.py $absolute_dir/decompiled $absolute_dir/base.apk $path;

	# Extracting the urls inside the code
	grep -or -E "https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,4}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)"  $absolute_dir/decompiled/ --exclude-dir=resources --no-filename 2>/dev/null | uniq > $absolute_dir/net2_$stripped.txt
	grep -or -E "http:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,4}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)"  $absolute_dir/decompiled/ --exclude-dir=resources --no-filename 2>/dev/null | uniq > $absolute_dir/http_net2.txt
	
	# Parsing the URLS to a specific format
	cat $absolute_dir/net2_$stripped.txt | cut -d "/" -f 3 | sort | uniq > $absolute_dir/_filtered_net2.txt

	cp $absolute_dir/decompiled/resources/AndroidManifest.xml $absolute_dir/base/AndroidManifest.xml
	internet=$(cat $absolute_dir/base/AndroidManifest.xml | grep -E "INTERNET|ACCESS_NETWORK_STATE|ACCESS_WIFI_STATE")
  	suid=$(cat $absolute_dir/base/AndroidManifest.xml | grep -Po "(?<=android:sharedUserId=)\"[^\"]+\"" | sed 's/\"//g')
	if [[ ! -z "$suid" ]]; then
	    if [[  -z "$internet"  ]]; then
	      echo "0" > $absolute_dir/$suid
		  has_internet=0
	    else
		  has_internet=1
	      find $path -name $suid -exec echo "1" > {} \;  
	    fi  
	else
	    if [[  ! -z "$internet" ]]; then
	      has_internet=1
	    else
	      has_internet=0
	    fi
	fi
	cd $path
	python3 main.py $absolute_dir $has_internet $uuid_execution $ADA_DIRECTORY/$ADA_JSON_FILE;
	sleep 2
}

apktoolFunction()
{
	for dir in $apk_path
	do
		absolute_dir=`realpath $dir`;
		mv $absolute_dir/*.apk $absolute_dir/base.apk 2>/dev/null;
		cd $absolute_dir
		if [[ $(ls | grep -x base | wc -l) -eq 0 && $(ls | grep -x base.apk | wc -l) -eq 1 && ! -f "apkTool.txt"  ]]; then			
			python3 $path/utils/decompile_apktool.py $absolute_dir/base.apk $path;
			touch apkTool.txt
			jadxFunction
			if [ $(find $absolute_dir/base -name "*apk" | wc -l) -ne 0 ]; then
				for apk in $(find $absolute_dir/base -name "*apk")
				do
					stripped=$(echo $apk | cut -d "/" -f 10 | cut -d "." -f 1)
					mkdir $path/$stripped/ && mv $apk $path/$stripped/base.apk
					cd $path
					apktoolFunction
				done
			else
				cd $path
			fi
		else
			cd $path
		fi
	done
}

checkResultsDirectory(){
	if [ ! -d "$resultsPath" ]; then
		mkdir -p "$resultsPath"
		if [  ! -d "$resultsPath" ]; then
			echo "Error creating the Results directory."
			exit 1
		fi
	fi 
}

getADAJson

apktoolFunction

checkResultsDirectory

python3 utils/collect_data.py "$actual_timestamp" $uuid_execution;

find . -name "apkTool.txt" -exec rm {} \;

echo "Analysis successfully executed"