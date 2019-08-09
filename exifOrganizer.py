import exifread,os,sys,re
from queue import Queue
from threading import Thread


newDirectory = r'D:\JPEG'

class OrganizerWorker(Thread):
    
    def __init__(self,queue):
        Thread.__init__(self)
        self.queue=queue

    def run(self):
        pattern=re.compile(r'^.{1,}\.jp[e]{0,1}g',re.IGNORECASE)
        while True:
            directory,fileList = self.queue.get()
            try:
                for fname in fileList:
                    if pattern.match(fname):
                        print(directory+" "+fname)
                        self.processFile(directory,fname)
                    else:
                        print("no match")
            finally:
                self.queue.task_done()

    def overwritePhoto(self,dirName,targetDir,date,fName):
        os.remove(targetDir+'\\'+date+'\\'+fName)
        os.rename(dirName+'\\'+fName,targetDir+'\\'+date+'\\'+fName)
    
    def processFile(self,dirName,fName):
        alwaysOverwrite=False
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
            overwrite=input("Overwrite?")
            if overwrite in ['yes','y'] or alwaysOverwrite:
                self.overwritePhoto(dirName,targetDir,date,fName)
            elif overwrite in ['Always']:
                alwaysOverwrite=True
                self.overwritePhoto(dirName,targetDir,date,fName)
            else:
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

def multiSearchDirectory(rootDir):

    queue = Queue()
    for x in range(8):
        print("worker created")
        worker = OrganizerWorker(queue)
        worker.daemon = True
        worker.start()
    for dirName, subdirList, fileList in os.walk(rootDir, topdown=False):
        #print('Found directory: %s' % dirName)
        queue.put((dirName,fileList))
    queue.join()

def main(argv):
    multiSearchDirectory(r'D:\test')

if __name__=="__main__":
    main(sys.argv[1:])


