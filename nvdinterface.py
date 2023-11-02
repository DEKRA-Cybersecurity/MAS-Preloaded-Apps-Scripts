#!/usr/bin/python
from search_engine import *
from parsers import *

def run(path):

    file = path

    libraries_list,fname = parse_file(file)
    modules_cve_dict = seek(libraries_list,fname)
    #select(modules_cve_dict,libraries_list) 
    return modules_cve_dict
