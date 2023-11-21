#!/bin/bash


#curl -v --silent http://goo.gl/8Rd3yj 2>&1 | grep -i "Location: https"


File=$1
Lines=$(cat $File)
counter=0
counter_lines=$(cat $File | wc -l)
for Line in $Lines
do	
	#echo $Line
	output_resolve=$(curl -v --max-time 15 --silent $Line 2>&1 | grep "Could not resolve")
	if [ $? -eq 1 ]; then
		output_https=$(curl -v --max-time 15 --silent $Line 2>&1 | grep -i "Location: https")
		if [ $? -eq 0 ]; then
			((counter++))
		fi
	
		#echo $output
	else
		((counter_lines--))
	fi

done

#echo $counter
#echo "------"
#echo $counter_lines

if [ $counter -eq $counter_lines ]; then
	echo "PASS"
else
	echo "FAIL"
fi


