#!/bin/bash

#First, extract list of all apps installed in the phone:

adb shell pm list packages > all_apps.txt

#Keep the package only

sed -i 's/package://g' all_apps.txt

#Line by line, create a new directory and extract all apk files in there

Lines=$(cat all_apps.txt)

for Line in $Lines
do
	mkdir $Line;
	Path=$(adb shell pm path $Line | sed 's/package://g' | sed 's/([a-zA-Z0-9_]*\.)*apk$//g');
	adb shell ls $Path | grep -E "\.x?apk" > all_files.txt;
	Files=$(cat all_files.txt);
	for File in $Files
	do
		adb pull $File $Line || (echo "Copying to external storage" && adb shell mkdir /data/local/tmp/$Line && adb shell cp $File /data/local/tmp/$Line && adb pull /data/local/tmp/$Line . && adb shell rm -r /data/local/tmp/$Line;) 
		
	done
done
