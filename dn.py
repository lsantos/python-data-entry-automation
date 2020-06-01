import glob

def getfiles():
    return glob.glob("formats/**/*.pdf", recursive=True)
    
print(getfiles())