import exifread,os,sys,re

pattern=re.compile(r'^.{1,}\.jp[e]{0,1}g',re.IGNORECASE)
newDirectory = r'F:\JPEG'

def traverseDirectory(rootDir):
    for dirName, subdirList, fileList in os.walk(rootDir, topdown=False):
        print('Found directory: %s' % dirName)
        for fname in fileList:
            if pattern.match(fname):
                processFile(dirName,fname)
            else:
                print("not jpeg")
def processFile(dirName,fName):
    with open(dirName+'\\'+fName,'rb') as image:
        dateandtime = str(exifread.process_file(image).get('EXIF DateTimeOriginal'))
        year = dateandtime.split(':')[0]
        date =dateandtime.split(' ')[0].replace(':','-')
        if year not in [x[1] for x in os.walk(newDirectory)][0]:
            try:
                os.mkdir(newDirectory+'\\'+year)
            except OSError:
                print ("Creation of the directory %s failed" % newDirectory+'\\'+year)
            else:  
                print ("Successfully created the directory %s " % newDirectory+'\\'+year)
    targetDir=newDirectory+'\\'+year
    print(targetDir+'\\'+date)
    if date not in [x[1] for x in os.walk(targetDir)][0]:
        try:
            os.mkdir(targetDir+'\\'+date)
        except OSError:
            print ("Creation of the directory %s failed" % targetDir+'\\'+date)
            exit()
        else:  
            print ("Successfully created the directory %s " % targetDir+'\\'+date)
    try:
        os.rename(dirName+'\\'+fName,targetDir+'\\'+date+'\\'+fName)
    except FileExistsError:
        #overwrite=input("Overwrite?")
        #if overwrite in ['yes','y']:
        #    os.remove(targetDir+'\\'+date+'\\'+fName)
        #    os.rename(dirName+'\\'+fName,targetDir+'\\'+date+'\\'+fName)
        #else:
        i=1
        while True:
            try:
                os.rename(dirName+'\\'+fName,targetDir+'\\'+date+'\\'+fName.split('.')[0]+'_'+str(i)+'.jpg')
            except FileExistsError:
                continue
            else:
                break
        
            print(targetDir+'\\'+date+'\\'+fName+'_'+str(i))
    else:
        print(targetDir+'\\'+date+'\\'+fName)
    return
def main(argv):
    traverseDirectory(r'F:\User Files\Pictures')

if __name__=="__main__":
    main(sys.argv[1:])


