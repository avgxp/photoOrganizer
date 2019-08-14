import exifread,os,sys,re
from queue import Queue
from threading import Thread

#pattern=re.compile(r'^.{1,}\.jp[e]{0,1}g$',re.IGNORECASE)
#pattern=re.compile(r'^.{1,}\.(arw$|cr2$)',re.IGNORECASE)
pattern = re.compile(r'^.{1,}\.(arw$|cr2$|jp[e]{0,1}g$|orf$)',re.IGNORECASE)
newDirectory = r'F:\JPEG'


class OrganizerWorker(Thread):
    
    def __init__(self,imageQueue):
        Thread.__init__(self)
        self.queue=imageQueue

    def run(self):
        while True:
            directory,fname,targetDir = self.queue.get()
            try:
                self.processFile(directory,fname,targetDir)
            finally:
                self.queue.task_done()

    def overwritePhoto(self,dirName,targetDir,date,fName):
        os.remove(targetDir+'\\'+date+'\\'+fName)
        os.rename(dirName+'\\'+fName,targetDir+'\\'+date+'\\'+fName)
    
    def processFile(self,dirName,fName,targetDir):
        try:
            os.rename(dirName+'\\'+fName,targetDir+'\\'+fName)
            print(fName+' moved')
        except FileExistsError:
            i=1
            while True:
                try:
                    os.rename(dirName+'\\'+fName,targetDir+'\\'+fName.split('.')[0]+'_'+str(i)+'.jpg')
                except FileExistsError:
                    i+=1
                    continue
                else:
                    break
        return
class directoryCreator(Thread):
    
    def __init__(self,dirQueue,imageQueue):
        Thread.__init__(self)
        self.queue=dirQueue
        self.imageQueue =imageQueue

    def run(self):
        while True:
            dirName,fileList = self.queue.get()
            try:
                self.processDirectory(dirName,fileList)
            finally:
                self.queue.task_done()

    def processDirectory(self,dirName,fileList):
        for fname in fileList:
            if pattern.match(fname):    
                with open(dirName+'\\'+fname,'rb') as image:
                    exifList = ['EXIF DateTimeOriginal','EXIF ModifyDate','']
                    dateandtime=False
                    for exifTag in exifList:
                        if not dateandtime:
                            dateandtime = str(exifread.process_file(image).get(exifTag))
                        else:
                            break
                if dateandtime:
                    yearDir = self.setDirectory(dateandtime.split(':')[0],newDirectory)
                    if yearDir:
                        targetDir = self.setDirectory(dateandtime.split(' ')[0].replace(':','-'),yearDir)
                        self.imageQueue.put((dirName,fname,targetDir))
                        print(dirName+'\\'+fname+' added to queue')
                      
                        
    def setDirectory(self,newFolder,inFolder):
        if newFolder not in [x[1] for x in os.walk(inFolder)][0]:
            if not os.path.exists(inFolder+'\\'+newFolder):
                try:
                    os.mkdir(inFolder+'\\'+newFolder)
                except OSError:
                    print ("Creation of the directory %s failed" % inFolder+'\\'+newFolder)
                    return False
        return inFolder+'\\'+newFolder


def multiSearchDirectory(rootDir):
    
    dirQueue = Queue()
    imageQueue = Queue()
    for x in range(16):
        dirworker = directoryCreator(dirQueue,imageQueue)
        dirworker.daemon = True
        dirworker.start()
        
    for dirName, subdirList, fileList in os.walk(rootDir, topdown=False):        
        dirQueue.put((dirName,fileList))
    dirQueue.join()
    
    for x in range(16):
        imgageworker = OrganizerWorker(imageQueue)
        imageworker.daemon = True
        imageworker.start()
    imageQueue.join()           
                


def main(argv):
    multiSearchDirectory(r'F:\User Files\Pictures')

if __name__=="__main__":
    main(sys.argv[1:])


