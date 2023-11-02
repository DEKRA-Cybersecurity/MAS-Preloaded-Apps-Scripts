#!/usr/bin/python

from cProfile import run
import os
import base64
from time import sleep
import xml.etree.ElementTree as ET
import subprocess
import sys
import database_utils
import nvdinterface
import formula
import datetime


'''
Automated mobile applications test cases evaluator

See README.txt for execution instructions

'''


'''
Variable definition/declaration section
'''

wdir = sys.argv[1]
internet = sys.argv[2]
name = wdir.split("/")[-1]
apk = 'base.apk'
package = ''
apk_hash = ''
activities = []

path_checksec = "checksec"
path_apksigner = "apksigner"
path_android_nm_armv7 = "nm"
path_android_nm_aarch64="nm"
path_libscout = "~/Documents/Tools/LibScout/build/libs/LibScout.jar"
path_android_jar = "~/Android/Sdk/platforms/android-31/android.jar"
path_libscout_config = "~/Documents/Tools/LibScout/config/LibScout.toml"
path_testssl = "~/Documents/Tools/testssl2"

'''
Method implementation section
'''

def check_package_name():
    '''
    Prints the package name.
    '''
    # awk -F 'package=' '{print $2}' | awk -F' ' '{print $1}' | sed s/\"//g
    grep = "YXdrIC1GICdwYWNrYWdlPScgJ3twcmludCAkMn0nIHwgYXdrIC1GJyAnICd7cHJpbnQgJDF9JyB8IHNlZCBzL1wiLy9n"
    d_grep = base64.b64decode(grep).decode("utf-8")
    cmd = f"cat {wdir}/base/AndroidManifest.xml | {d_grep}"
    output = subprocess.check_output(cmd, shell=True).decode("utf-8").replace("\n","")
    if "split" in name:
        package = output + "_" + name
    else:
        package = output
    
    return package

def check_hash_apk():
    '''
    Prints the application's hash - sha256
    '''
    cmd = f"sha256sum {wdir}/base.apk" + " | awk '{ print $1 }'"
    output = subprocess.check_output(cmd, shell=True).decode("utf-8").replace("\n","")
    
    return output

def check_all_network():
    '''
    Check if the application contains INTERNET permission in AndroidManifest.xml file.

    This is used to filter out those application that do not use internet functionalities to focus manually on
    those that do.
    '''

    #cmd = f'cat {wdir}/base/AndroidManifest.xml | grep INTERNET'
    cmd_get_suid = f'cat {wdir}/base/AndroidManifest.xml | grep -Po \"(?<=android:sharedUserId=)\\"[^\\"]+\\"\" | sed \'s/\"//g\''

    try:
        out_suid = subprocess.check_output(cmd_get_suid, shell=True).splitlines()
        out_suid_string = out_suid[0].decode()
    except:
        out_suid_string = "" #Does not have SUID

    try:
        file = open(out_suid_string, 'r')

        content = file.read().splitlines()[0]

        if content == "1":
            check_network1()
            check_network2()
            check_network3()
        elif content == "0":
            database_utils.update_values("Report", "NETWORK_1", "NA", "HASH", apk_hash)
            database_utils.update_values("Report", "NETWORK_2", "NA", "HASH", apk_hash)
            database_utils.update_values("Report", "NETWORK_3", "NA", "HASH", apk_hash)

            database_utils.update_values("Total_Fail_Counts", "NETWORK_1", 0, "HASH", apk_hash)
            database_utils.update_values("Total_Fail_Counts", "NETWORK_2", 0, "HASH", apk_hash)
            database_utils.update_values("Total_Fail_Counts", "NETWORK_3", 0, "HASH", apk_hash)

    except:
        if internet == "1":
            check_network1()
            check_network2()
            check_network3()
        else:
            database_utils.update_values("Report", "NETWORK_1", "NA", "HASH", apk_hash)
            database_utils.update_values("Report", "NETWORK_2", "NA", "HASH", apk_hash)
            database_utils.update_values("Report", "NETWORK_3", "NA", "HASH", apk_hash)

            database_utils.update_values("Total_Fail_Counts", "NETWORK_1", 0, "HASH", apk_hash)
            database_utils.update_values("Total_Fail_Counts", "NETWORK_2", 0, "HASH", apk_hash)
            database_utils.update_values("Total_Fail_Counts", "NETWORK_3", 0, "HASH", apk_hash)
    
    
    '''
    if output_internet_perm >= 1:            
    	with open(wdir+"/report_"+name+".txt", "a+") as f:
    		print("INCONCLUSIVE*,INCONCLUSIVE*,INCONCLUSIVE*,INCONCLUSIVE*,INCONCLUSIVE*,INCONCLUSIVE*,INCONCLUSIVE*,INCONCLUSIVE_NETWORK1*,INCONCLUSIVE_NETWORK2*,INCONCLUSIVE_NETWORK3*,", file=f, end="") #We cannot be sure if it is OK or not -> Manual check required.
    elif output_internet_perm == 0:
    	with open(wdir+"/report_"+name+".txt", "a+") as f:
    		print("NA*,NA*,NA*,NA*,NA*,NA*,NA*,NA_NETWORK1*,NA_NETWORK2*,NA_NETWORK3*,", file=f, end="") #Does not use internet connection


    '''
def check_storage2():
    '''
    Checks for WRITE_EXTERNAL_STORAGE in AndroidManifest.xml file.

    If it is not found, it is a PASS
    '''
    output_write_external = 0
    print("Grepping Android for WRITE pattern: \n")
    cmd = f'cat {wdir}/base/AndroidManifest.xml | grep WRITE_EXTERNAL_STORAGE'

    try:
        out = subprocess.check_output(cmd, shell=True).splitlines()
        output_write_external += 1   
    except subprocess.CalledProcessError as e:
        ct = datetime.datetime.now()
        if e.returncode == 1: #permission not found
            pass
        else:
            database_utils.insert_values_logging(apk_hash, ct, "STORAGE-2", "grep for WRITE_EXTERNAL_STORAGE permission failed. File not found")
            pass
        
    if output_write_external >= 1:

        total_matches = 0
        storage_functions = ["getExternalStorageDirectory", "getExternalFilesDir"]

        for i in storage_functions:
            cmd = f"grep -rlnwz -E {i} {wdir}/decompiled | wc -l"
            try:
                output = subprocess.check_output(cmd, shell=True).splitlines()
                if int(output[0]) > 0:
                    total_matches += int(output[0]) 
            except:
                ct = datetime.datetime.now()
                database_utils.insert_values_logging(apk_hash, ct, "STORAGE-2", f"grep command failed for {i}")
                pass #No output
                
        if total_matches > 0:
            database_utils.update_values("Report", "STORAGE_2", "Fail", "HASH", apk_hash)
            database_utils.insert_values_total_fail_count(apk_hash, "STORAGE_2", total_matches)
            #database_utils.update_values("Total_Fail_Counts", "STORAGE_2", total_matches, "HASH", apk_hash)
        else:
            database_utils.update_values("Report", "STORAGE_2", "Pass", "HASH", apk_hash) #Manual check is advised, no matches
            database_utils.insert_values_total_fail_count(apk_hash, "STORAGE_2", 0)
            #database_utils.update_values("Total_Fail_Counts", "STORAGE_2", 0, "HASH", apk_hash)
        
        #database_utils.update_values("Report", "STORAGE_2", "Needs Review", "HASH", apk_hash)
        #database_utils.insert_values_total_fail_count(apk_hash, "STORAGE_2", 0)
        
    elif output_write_external == 0:
        database_utils.update_values("Report", "STORAGE_2", "Pass", "HASH", apk_hash)
        database_utils.insert_values_total_fail_count(apk_hash, "STORAGE_2", 0)
        #database_utils.update_values("Total_Fail_Counts", "STORAGE_2", 0, "HASH", apk_hash)

def check_exported_activities():
    '''
    Extract exported activities from the application.
    '''
    #grep -E '(<activity).*(android:exported="true")' | awk -F 'name=' '{print $2}' | awk -F ' ' '{print $1}' | sed s/\"//g
    grep = "Z3JlcCAtRSAnKDxhY3Rpdml0eSkuKihhbmRyb2lkOmV4cG9ydGVkPSJ0cnVlIiknIHwgYXdrIC1GICduYW1lPScgJ3twcmludCAkMn0nIHwgYXdrIC1GICcgJyAne3ByaW50ICQxfScgfCBzZWQgcy9cIi8vZw=="
    d_grep = base64.b64decode(grep).decode("utf-8")
    cmd = f"cat {wdir}/base/AndroidManifest.xml | {d_grep}"
    output = [i.decode("utf-8") for i in subprocess.check_output(cmd, shell=True).splitlines()]
    global activities
    activities = output
    return output

def check_platform3():
    '''
    Extract custom url from the application.

    It extracts the scheme and the path defined. However, for this version it counts the number of custom URL scheme found
    to filter out those applications that have no custom URL in place.
    '''
    root = ET.parse(f'{wdir}/base/AndroidManifest.xml').getroot()
    activity_urls_dict = {}
    global package

    if package == '':
        package = check_package_name()

    for app in root.findall("application"):
        for activity in app.iter("activity"):

            i_filters = [x for x in activity.iter("intent-filter")] 
            
            if len(i_filters) > 0:

                custom_urls = []

                for i_filter in i_filters:
                    for data  in i_filter.iter("data"):
                        host = ''
                        path = ''
                        scheme = ''

                        for x in data.attrib.keys():
                            
                            if "host" in x:
                                host=data.attrib[x]
                            if "path" in x:
                                path=data.attrib[x]
                            
                            if "scheme" in x:
                                scheme=data.attrib[x]

                            if scheme != '' and scheme != 'http' and scheme != 'https':
                                custom_urls.append(f'{scheme}://{host}{path}')

                                
                custom_urls = list(dict.fromkeys(custom_urls))
                

                if len(custom_urls) > 0:
                    for i in activity.attrib.keys():
                        if "name" in i:
                            activity_urls_dict[activity.attrib[i]] = custom_urls             
                                                 
    if len(activity_urls_dict) > 0:
        database_utils.update_values("Report", "PLATFORM_3", "Needs Review", "HASH", apk_hash)
        database_utils.update_values("Total_Fail_Counts", "PLATFORM_3", 0, "HASH", apk_hash)
    else:
        database_utils.update_values("Report", "PLATFORM_3", "Pass", "HASH", apk_hash)
        database_utils.update_values("Total_Fail_Counts", "PLATFORM_3", 0, "HASH", apk_hash)

def check_content_providers():
    '''
    Extracts content providers.
    '''
    global package
    #grep -Po 'Provider{[\w\d\s\./]+}' | sort -u
    grep = "Z3JlcCAtUG8gJ1Byb3ZpZGVye1tcd1xkXHNcLi9dK30nIHwgc29ydCAtdQ=="
    d_grep = base64.b64decode(grep).decode("utf-8")
    
    if package == '':
        package = check_package_name()
        cmd = f"adb shell dumpsys package {package} | {d_grep}"
        
    else:
        cmd = f"adb shell dumpsys package {package} | {d_grep}"
    
    output = [i.decode("utf-8") for i in subprocess.check_output(cmd, shell=True).splitlines()]

    return output

def check_services_with_no_permissions():
    '''
    Extracts services with no permissions.
    '''
    #grep -E "<service" | egrep -v 'android:permission=' | awk -F 'android:name=' '{print $2}' | awk -F '/>' '{print $1}' | sed s/\"//g
    grep = "Z3JlcCAtRSAiPHNlcnZpY2UiIHwgZWdyZXAgLXYgJ2FuZHJvaWQ6cGVybWlzc2lvbj0nIHwgYXdrIC1GICdhbmRyb2lkOm5hbWU9JyAne3ByaW50ICQyfScgfCBhd2sgLUYgJy8+JyAne3ByaW50ICQxfScgfCBzZWQgcy9cIi8vZw=="
    d_grep = base64.b64decode(grep).decode("utf-8")
    cmd = f"cat {wdir}/base/AndroidManifest.xml | {d_grep}"
    output = [i.decode("utf-8") for i in subprocess.check_output(cmd, shell=True).splitlines()]
    
    return output    

def check_debuggable():
    '''
    Check if the application uses android:debuggable="true" in AndroidManifest.xml file
    '''
    cmd =f"cat {wdir}/base/AndroidManifest.xml |  egrep -iE 'android:debuggable=\"true\"'"
    try:
        output = [i.decode("utf-8") for i in subprocess.check_output(cmd, shell=True).splitlines()]
    except subprocess.CalledProcessError as e:
        ct = datetime.datetime.now()
        if e.returncode == 2:
            database_utils.insert_values_logging(apk_hash, ct, "CODE-2", "grep android:debuggable command failed")
            output = "Error"
        else:
            output = "No relevant results"
    
    return output

def check_signature():
    '''
    Returns output of apksigner to verify the signature.
    '''
    try:
        cmd = f"{path_apksigner} verify -verbose {wdir}/{apk}"
        output = [i.decode("utf-8") for i in subprocess.check_output(cmd, shell=True).splitlines()]
        return output
    except:
        ct = datetime.datetime.now()
        database_utils.insert_values_logging(apk_hash, ct, "CODE-1", "apksigner failed verifying signature")
        return "Invalid"

def check_debug_symbols():
    '''
    Checks debug and dynamic symbols for library files in the application.
    '''
    path = f'{wdir}/base/lib'
    files = []
    final_dict_debug_sym = {}
    final_dict_dynam_sym = {}

    for r,d,f, in os.walk(path):
        
        for file in f:
            files.append(os.path.join(r,file))

        for i in files:
            debug_sym = []
            dynam_sym = []
            cmd_check_arch = f"file {i}"
            output = subprocess.check_output(cmd_check_arch, shell=True).decode("utf-8").replace("\n","")

            if "aarch64" in output:
                cmd_a= f'{path_android_nm_aarch64} -a {i}'
                out = subprocess.check_output(cmd_a, shell=True, stderr=subprocess.STDOUT).decode("utf-8").splitlines()

                for x in out:
                    if x.find("no symbols") == -1:
                        debug_sym.append(x)

                cmd_d = f'{path_android_nm_aarch64} -D {i}'
                out = subprocess.check_output(cmd_d, shell=True, stderr=subprocess.STDOUT).decode("utf-8").replace("\n","").splitlines()

                for x in out:
                    if x.find("no symbols") == -1:
                        dynam_sym.append(x)


            elif "ELF 32-bit LSB shared object, ARM" in output:
                cmd_a= f'{path_android_nm_armv7} -a {i}'
                out = subprocess.check_output(cmd_a, shell=True, stderr=subprocess.STDOUT).decode("utf-8").splitlines()

                for x in out:
                    if x.find("no symbols") == -1:  
                        debug_sym.append(x)    
              
                cmd_d = f'{path_android_nm_armv7} -D {i}'
                out = subprocess.check_output(cmd_d, shell=True, stderr=subprocess.STDOUT).decode("utf-8").splitlines()

                for x in out:
                    if x.find("no symbols") == -1:
                        dynam_sym.append(x) 
            
            if len(debug_sym) != 0:
                final_dict_debug_sym[i]=debug_sym 
            
            if len(dynam_sym) != 0:
                final_dict_dynam_sym[i]=dynam_sym

    if len(final_dict_debug_sym) != 0:
        #Debug symbols found in files
        database_utils.update_values("Report", "CODE_3", "Fail", "HASH", apk_hash)          
        database_utils.update_values("Total_Fail_Counts", "CODE_3", len(final_dict_debug_sym), "HASH", apk_hash)
    else:
        #No debug symbols found
        database_utils.update_values("Report", "CODE_3", "Pass", "HASH", apk_hash)
        database_utils.update_values("Total_Fail_Counts", "CODE_3", 0, "HASH", apk_hash)

    #Dynamic symbols not taken into account, but may be useful in the future.
    if len(final_dict_dynam_sym) != 0:
    	pass



def check_crypto1():
    '''
        Hardcoded Byte arrays, b64 str or final Strings in files where crypto lib are imported
        Key generation with hardcoded parameters
        Triple backward slash to get escaped \"
        Output is always multiline, so len of output is not necessarily required, only a match is enough.
        However, if other regular expressions are imported, it may be useful in the future 
    '''
    total_matches = 0
    vuln_parameters = ["\"import java(x)?\.(security|crypto).*;(\\n|.)*((final String [a-zA-Z0-9]+[ ]*\=)|(==\\\")|(byte\[\] [a-zA-Z0-9]* = [{]{1}[ ]?[0-9]+)|(SecretKeySpec\(((\{[0-9]+)|(\\\"[a-zA-Z0-9]+\\\"))))\"", "\"Lcom\/jiolib\/libclasses\/utils\/AesUtil\""]

    for i in vuln_parameters:
        cmd = f"grep -rlnwz -E {i} {wdir}/decompiled | wc -l"
        try:
            output = subprocess.check_output(cmd, shell=True).splitlines()
            if int(output[0]) > 0:
                total_matches += int(output[0]) 
        except:
            ct = datetime.datetime.now()
            database_utils.insert_values_logging(apk_hash, ct, "CRYPTO-1", f"grep command failed for {i}")
            pass #No output
            
    if total_matches > 0:
        database_utils.update_values("Report", "CRYPTO_1", "Fail", "HASH", apk_hash)
        database_utils.update_values("Total_Fail_Counts", "CRYPTO_1", total_matches, "HASH", apk_hash)
    else:
        database_utils.update_values("Report", "CRYPTO_1", "Pass", "HASH", apk_hash) #Manual check is advised, no matches
        database_utils.update_values("Total_Fail_Counts", "CRYPTO_1", 0, "HASH", apk_hash)


def check_crypto3():
    '''
        Check for potentially vulnerable algorithms in the code.
        If a match is found, FAIL is set, otherwise PASS
    '''
    total_matches = 0
    vuln_algo = ["\"AES/CBC/PKCS5Padding\"", "\"DES/CBC/PKCS5Padding\"", "\".*/ECB/.*\"", "\"^(TLS).*-CBC-.*\""]

    for i in vuln_algo:
        cmd = f"grep -rlnwz -e {i} {wdir}/decompiled | wc -l"
        try:
            output = subprocess.check_output(cmd, shell=True).splitlines()
            if int(output[0]) > 0:
                total_matches += int(output[0])
        except:
            ct = datetime.datetime.now()
            database_utils.insert_values_logging(apk_hash, ct, "CRYPTO-3", f"grep command failed for {i}")
            pass #No output

    if total_matches > 0:
        database_utils.update_values("Report", "CRYPTO_3", "Fail", "HASH", apk_hash)
        database_utils.update_values("Total_Fail_Counts", "CRYPTO_3", total_matches, "HASH", apk_hash)
    else:
        database_utils.update_values("Report", "CRYPTO_3", "Pass", "HASH", apk_hash)
        database_utils.update_values("Total_Fail_Counts", "CRYPTO_3", 0, "HASH", apk_hash)
            
def check_platform2():
    '''
    The primary objective is to search for potential SQL injection in queries.
    A main regex to search for these queries is applied. 
    
    E.g:
    "SELECT Column FROM Table WHERE id = " + input_variable + " ... ;"

    May suggest that an user could inject malicious SQL code to cause an injection. 

    If a match with these queries is registered, it may conclude in an INCONCLUSIVE.


    Dynamic analysis: Add drozer module to query and extract potential injections in content providers.
    Drozer can be launched in cmdline.

    docker run fsecurelabs/drozer /bin/bash -c "drozer console connect --server 192.168.3.14 -c 'run scanner.provider.injection -a com.android.chrome'";
    '''
    total_matches = 0
    vuln_parameters = ["\"\\\"[ ]*(ALTER|CREATE|DELETE|DROP|EXEC(UTE){0,1}|INSERT( +INTO){0,1}|MERGE|SELECT|UPDATE|UNION( +ALL){0,1})[a-zA-Z0-9\\ \\*_\\-]+(\=)(\\ |\\\")[ ]?\\\+\"", "\"(shouldOverrideUrlLoading\\(.*\\{)[\\n\\s\\t]*return false;(\\n|[\\s\\t])\\}\""]
    #cmd_webview = f'grep -rnwz -E {wdir}/decompiled | wc -l'

    for i in vuln_parameters:
        cmd = f"grep -rlnwz -E {i} {wdir}/decompiled | wc -l" #cmd = f"grep -rnwz -E {vuln_parameters[0]} {wdir}/decompiled | wc -l"
  
        try:
            output = subprocess.check_output(cmd, shell=True).splitlines()
            if int(output[0]) > 0:
                total_matches = int(output[0]) 
        except:
            ct = datetime.datetime.now()
            database_utils.insert_values_logging(apk_hash, ct, "PLATFORM-2", "grep failed  for {i}")
            pass #No output
            
    if total_matches > 0:
        database_utils.update_values("Report", "PLATFORM_2", "Fail", "HASH", apk_hash)
        database_utils.update_values("Total_Fail_Counts", "PLATFORM_2", total_matches, "HASH", apk_hash)
    else:
        database_utils.update_values("Report", "PLATFORM_2", "Pass", "HASH", apk_hash)
        database_utils.update_values("Total_Fail_Counts", "PLATFORM_2", 0, "HASH", apk_hash)

def check_platform4():
    with open(wdir+'/report_'+name+'.txt', 'a+') as f:
        output_total_fails = 0
        activities = check_exported_activities()
            
        if len(activities) > 0:
            output_total_fails +=1

        providers = check_content_providers()


        if len(providers) > 0:
            output_total_fails +=1

        services_no_perm = check_services_with_no_permissions()
            
        if len(services_no_perm) > 0:
            output_total_fails +=1


        if output_total_fails >= 2:
            database_utils.update_values("Report", "PLATFORM_4", "Fail", "HASH", apk_hash)
            database_utils.update_values("Total_Fail_Counts", "PLATFORM_4", output_total_fails, "HASH", apk_hash)
        elif output_total_fails == 1 or output_total_fails == 0:
            database_utils.update_values("Report", "PLATFORM_4", "Pass", "HASH", apk_hash) #Most likely, only MainActivity is the exported activity, which is PASS if that is the only exported one
            database_utils.update_values("Total_Fail_Counts", "PLATFORM_4", 0, "HASH", apk_hash)

def check_network2():
    '''
        Check for potentially vulnerable TLS configurations.
        If a match is found, INCONCLUSIVE is set, could be a potential FAIL
        This case creates a report that shall be reviewed manually to inspect for a verdict in the Test Case

        Future work: check with a whitelist of URLs if they are considered PASS even if they allow TLS1 or TLS1.1 according to ciphersuites.
    '''
    total_matches = 0
    is_inconclusive = False
    grep_filter = ["\"((SSLv2).*(deprecated))|((SSLv3).*(deprecated))|((TLS 1).*(deprecated))|((TLS 1.1).*(deprecated))\"", "\"((TLSv1:)|(TLSv1.1:)).*(-DES-[A-Z0-9]+)\""]
    with open(wdir+'/_filtered_net2.txt') as all_urls:

        for url in all_urls:
            url_no_breakline = url.rstrip("\n")
            cmd = f'echo no | {path_testssl} -P {url_no_breakline} 2>/dev/null | grep -E {grep_filter[1]} | wc -l'

            results = database_utils.get_values("TestSSL_URLS", "URL", url_no_breakline)
            print(results)
            if not results:
                print("Result is empty.")
                try:
                    output = subprocess.check_output(cmd, shell=True).splitlines()
                    if int(output[0]) > 0:
                        total_matches += 1 
                except:
                    ct = datetime.datetime.now()
                    database_utils.insert_values_logging(apk_hash, ct, "NETWORK-2", "Command failed.")
                    pass #No output

                if total_matches > 0:
                    is_inconclusive = True
                    database_utils.insert_values_testsslURLs(url_no_breakline, "Needs Review")
                else:
                    database_utils.insert_values_testsslURLs(url_no_breakline, "Pass")

                print(total_matches)
            else:
                print("Skipped testssl. Result in DB")
                if results[0][1] == "INCONCLUSIVE":
                    is_inconclusive = True
                elif results[0][1] == "PASS":
                    is_inconclusive = False

            total_matches = 0

    if is_inconclusive:
        database_utils.update_values("Report", "NETWORK_2", "Needs Review", "HASH", apk_hash)
        database_utils.update_values("Total_Fail_Counts", "NETWORK_2", total_matches, "HASH", apk_hash)
    else:
        database_utils.update_values("Report", "NETWORK_2", "Pass", "HASH", apk_hash)
        database_utils.update_values("Total_Fail_Counts", "NETWORK_2", 0, "HASH", apk_hash)



def check_network1():
    '''
        Check if there is any URL with "http" schema.

        URLs are extracted from the static decompiled code.

        In the case there is at least one, it is INCONCLUSIVE (Manual review is required, as many of these URLs are static resources and not
        relevant to security purposes), otherwise, PASS.

        An auxiliar file with those found URLs is provided for manual review.

    '''

    with open(wdir+'/http_net2.txt') as f:
        lines = len(f.readlines())

    
    if lines > 0:
        try:
            cmd = f'./check_network1_redirects.sh {wdir+"/http_net2.txt"}'
            output = subprocess.check_output(cmd, shell=True)
            if output.decode("utf-8").rstrip("\n") == "PASS":
                database_utils.update_values("Report", "NETWORK_1", "Pass", "HASH", apk_hash)
                database_utils.update_values("Total_Fail_Counts", "NETWORK_1", 0, "HASH", apk_hash)
            else:
                database_utils.update_values("Report", "NETWORK_1", "Fail", "HASH", apk_hash)
                database_utils.update_values("Total_Fail_Counts", "NETWORK_1", 1, "HASH", apk_hash)
        except:
            ct = datetime.datetime.now()
            database_utils.insert_values_logging(apk_hash, ct, "NETWORK-1", "Check redirects script failed")
            pass
        
    else:
        database_utils.update_values("Report", "NETWORK_1", "Pass", "HASH", apk_hash)
        database_utils.update_values("Total_Fail_Counts", "NETWORK_1", 0, "HASH", apk_hash)


def check_network3():
    net_config=False
    low_target_Sdk = False
    total_matches = 0
    verifier_check = ["\"(import java(x)?\\.(.*)HostnameVerifier;)\""]
    cmd =f"cat {wdir}/base/AndroidManifest.xml |  egrep -iE 'android:networkSecurityConfig' | wc -l"
    try:
        output = subprocess.check_output(cmd, shell=True).splitlines()
        if int(output[0]) > 0:
            net_config = True
    except:
        net_config = False
        ct = datetime.datetime.now()
        database_utils.insert_values_logging(apk_hash, ct, "NETWORK-3", "Network security config file grep error")

    cmd_get_target_sdk = f'cat {wdir}/base/AndroidManifest.xml | grep -Po \"(?<=android:targetSdkVersion=)\\"[^\\"]+\\"\" | sed \'s/\"//g\''
    try:
        output = subprocess.check_output(cmd_get_target_sdk, shell=True).splitlines()
        print(int(output[0]))
        if int(int(output[0])) < 24:
            low_target_Sdk = True
    except:
        low_target_Sdk = False
        ct = datetime.datetime.now()
        database_utils.insert_values_logging(apk_hash, ct, "NETWORK-3", "Target sdk grep error")


    cmd_check_hostnameverifier = f"grep -rnwz -E {verifier_check[0]} {wdir}/decompiled | wc -l"
    try:
        output = subprocess.check_output(cmd_check_hostnameverifier, shell=True).splitlines()
        if int(output[0]) > 0:
            total_matches += 1 
    except:
        ct = datetime.datetime.now()
        database_utils.insert_values_logging(apk_hash, ct, "NETWORK-3", "hostname verifier functions grep error or not found")
        pass #No output

    with open(wdir+'/report_'+name+'.txt', 'a+') as f:
        if net_config == True and total_matches == 0:
            database_utils.update_values("Report", "NETWORK_3", "Needs Review", "HASH", apk_hash)
            database_utils.update_values("Total_Fail_Counts", "NETWORK_3", 0, "HASH", apk_hash)
        elif net_config == False and low_target_Sdk == True and total_matches == 0:
            database_utils.update_values("Report", "NETWORK_3", "Fail", "HASH", apk_hash)
            database_utils.update_values("Total_Fail_Counts", "NETWORK_3", 1, "HASH", apk_hash)
        elif net_config == False and low_target_Sdk == False or total_matches > 0:
            database_utils.update_values("Report", "NETWORK_3", "Pass", "HASH", apk_hash)
            database_utils.update_values("Total_Fail_Counts", "NETWORK_3", 0, "HASH", apk_hash)

def check_code1():
    with open(wdir+'/report_'+name+'.txt', 'a+') as f:
        output_sign_count = 0
        signature_info = check_signature()
        for i in signature_info:
            if "v2): true" in i or "v3): true" in i:
                output_sign_count += 1
                
        if output_sign_count >= 1:
            database_utils.update_values("Report", "CODE_1", "Pass", "HASH", apk_hash)
            database_utils.update_values("Total_Fail_Counts", "CODE_1", 0, "HASH", apk_hash)
            
        else:
            database_utils.update_values("Report", "CODE_1", "Fail", "HASH", apk_hash)
            database_utils.update_values("Total_Fail_Counts", "CODE_1", 0, "HASH", apk_hash)

def check_code2():
    debug_info = check_debuggable()
    with open(wdir+'/report_'+name+'.txt', 'a+') as f:
        if debug_info == 'No relevant results':
            database_utils.update_values("Report", "CODE_2", "Pass", "HASH", apk_hash)
            database_utils.update_values("Total_Fail_Counts", "CODE_2", 0, "HASH", apk_hash)
        else:
            database_utils.update_values("Report", "CODE_2", "Fail", "HASH", apk_hash)
            database_utils.update_values("Total_Fail_Counts", "CODE_2", 1, "HASH", apk_hash)

def check_code5():
    # command to parse libscout output: jq ".""lib_packageOnlyMatches""[]" libscoutOutput.json | uniq
    # command to execute libscout: java -jar ~/Documents/Tools/LibScout/build/libs/LibScout.jar -o match -p /home/jmsl/Documents/Tools/LibScout-Profiles/ -j {wdir}/libscout_output -a ~/Android/Sdk/platforms/android-31/android.jar base.apk
    # 1st execute libscout over apk to generate libraries
    # 2nd parse json output to keep only libraries
    # 3rd execute nvdapi script to receive output, then write to database PASS/FAIL

    cmd = f"java -jar {path_libscout} -o match -c {path_libscout_config} -p /home/jmsl/Documents/Tools/LibScout-Profiles/ -j {wdir}/libscout_output -a {path_android_jar} {wdir}/base.apk"
    try:
        output = subprocess.check_output(cmd, shell=True)
    except:
        ct = datetime.datetime.now()
        database_utils.insert_values_logging(apk_hash, ct, "CODE-5", "LibScout execution failed")
        print("Something happened with LibScout execution")

    cmd_copy_json = f"find {wdir}/libscout_output -name \"*.json\" -exec cp {{}} {wdir}/libscoutOutput.json \\;"

    try:
        output = subprocess.check_output(cmd_copy_json, shell=True)
    except:
        ct = datetime.datetime.now()
        database_utils.insert_values_logging(apk_hash, ct, "CODE-5", "find and copy from libscout output failed.")
        print("Something happened with Find&Copy execution")

    cmd_parse_json = f"jq \".\"\"lib_packageOnlyMatches\"\"[]\" {wdir}/libscoutOutput.json | uniq > {wdir}/libscoutOutput_parsed.txt"
    
    try:
        output = subprocess.check_output(cmd_parse_json, shell=True)
    except:
        ct = datetime.datetime.now()
        database_utils.insert_values_logging(apk_hash, ct, "CODE-5", "parsing libscout json output with jq failed")
        print("Something happened with Parsing execution")

    modules_cves_dict = nvdinterface.run(wdir+"/libscoutOutput_parsed.txt")

    if len(modules_cves_dict) > 0:
        database_utils.update_values("Report", "CODE_5", "Fail", "HASH", apk_hash)
        database_utils.update_values("Total_Fail_Counts", "CODE_5", len(modules_cves_dict), "HASH", apk_hash)
    else:
        database_utils.update_values("Report", "CODE_5", "Pass", "HASH", apk_hash)
        database_utils.update_values("Total_Fail_Counts", "CODE_5", 0, "HASH", apk_hash)

def setup():

    global wdir
    global apk
    
setup()

'''
Script execution section
'''

print("Script begins here")
package = check_package_name()
apk_hash = check_hash_apk()
database_utils.insert_values_report(apk_hash, package)



#MSTG-STORAGE-2
check_storage2()


#MSTG-CRYPTO-1
check_crypto1()

#MSTG-CRYPTO-3
check_crypto3()


#MSTG-PLATFORM-2
check_platform2()

#MSTG-PLATFORM-3
check_platform3()   

#NETWORK
check_all_network()

#MSTG-CODE-1
check_code1()


#MSTG-CODE-2
check_code2()

formula.extract_and_store_permissions(apk_hash, package, wdir+"/base/AndroidManifest.xml")