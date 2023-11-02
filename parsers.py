import string
import os

#This method is suitable for LibScout Output  
def parse_file(file):
    #Returns a list with modules, because versions are not included in this file...niceee
    f = open(file,"r")
    lines = f.readlines()
    libraries_list=[]
    for i in lines:
        libraries_list.append(i)
    
    fname = f'persist_{os.path.basename(f.name)}'
    return libraries_list, fname

def identify_parser(file):
    
    f = open(file, "r")
    content =f.readlines()

    if "1 {" in content[0]:
        print("identified a json_pb file-type format")
        suitable_parser = "json_pb"

    elif "/license" in content[0].lower():
        print("identified a license file-type format")
        suitable_parser = "license"
    
    elif "simple_file_format_DEKRA" in content[0]:
        print("identified a simple file-type format")
        suitable_parser="simple"

    elif "+---DEKRA" in content[0]:
        print("identified a symbols file-type format")
        suitable_parser="symbols"

    elif "---quote" in content[0]:
        print("identified a quote file-type format")
        suitable_parser="quote"

    return suitable_parser
