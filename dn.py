import traceback
import glob
import os
import sys
import pdfplumber

from collections import OrderedDict
from PyPDF2 import PdfFileReader

def getfiles():
    return glob.glob("formats/**/*.pdf", recursive=True)

def readini(fname):
    """Instruction(s) to read an .ini file"""
    dic = {}

    with open(fname) as file:
        for line in file.readlines():
            line = line.rstrip()
            k, v = line.split("=") if line.find("=") > 0 else line.split('|')
            dic[k] = v

    return dic

def getformfields(obj, tree=None, retval=None, fileobj=None):
    fieldAttributes = {'/FT': 'Field Type', '/Parent': 'Parent', '/T': 'Field Name', 
        '/TU': 'Alternate Field Name', '/TM': 'Mapping Name', '/Ff': 'Field Flags', 
        '/V': 'Value', '/DV': 'Default Value'}

    if retval is None:
        retval = OrderedDict()
        catalog = obj.trailer["/Root"]

        if "/AcroForm" in catalog:
            tree = catalog["/AcroForm"]
        else:
            return None

    if tree is None:
        return retval

    obj._checkKids(tree, retval, fileobj)

    for attr in fieldAttributes:
        if attr in tree:
            obj._buildField(tree, retval, fileobj, fieldAttributes)
            break

    if "/Fields" in tree:
        fields = tree["/Fields"]

        for f in fields:
            field = f.getObject()
            obj._buildField(field, retval, fileobj, fieldAttributes)

    return retval

def getfields(fn):
    fields = getformfields(PdfFileReader(open(fn, 'rb')))
    
    return OrderedDict((k, v.get('/V', '')) for k, v in fields.items())

def gettextfields(layout_dic, fn):
    init_dic       =  layout_dic.get(os.path.basename(fn))
    txt_fields_dic =  filter_text_fields(init_dic)
    res            =  []
    pdf            =  pdfplumber.open(fn)
    page           =  pdf.pages[0]
    pg_txt         =  page.extract_text()

    for l in pg_txt.split(os.linesep):
        print(l.split(' '))   

    pdf.close()

    return dict(res)

def die(msg):
    """Print msg to std.err and exit program with error code"""

    print(msg, file=sys.stderr)

    exit(1)

def filter_form_fields(dic):
    """Filter information from init file(form_fields)"""
    return dict(filter(lambda v: v[1].lower() in ['e', 's'], dic.items()))

def filter_text_fields(dic):
    """Filter information from init file(txt_fields)"""
    return dict(filter(lambda v: v[1].lower() not in ['e', 's'], dic.items()))

def main():
    try:
        i1 = readini('l1.ini') # Read the 1st .ini file
        i2 = readini('l2.ini') # Read the 2nd .ini file
        layout_dic = {'1900070.pdf' : i1, '211559-050.pdf': i2}

        for fn in getfiles():
            form_fields = getfields(fn)
            init_dic = layout_dic.get(os.path.basename(fn))
            select_fields = filter_form_fields(init_dic)
            form_fields = { k:form_fields.get(k) for k in select_fields.keys() & form_fields.keys() }
    except BaseException as msg:
        traceback.print_exc(file=sys.stdout)
        die('Error occured: ' + str(msg))

if __name__ == '__main__':
    main()