#!/usr/bin/env python3
import subprocess
import time
import os
import img2pdf
import sys

homedir = os.path.expanduser('~')

assert homedir.startswith("/Users/")

folder = f"{homedir}/Pictures/Photo Booth Library/Pictures"
boothfolder = f"{homedir}/Desktop/photobooth"

assert ".." not in boothfolder
assert ".." not in folder

print('Warning: deleting the files in photo booth DOES NOT delete the files in your Desktop.')

if len(sys.argv) > 1 and sys.argv[1] == 'all':
    doesall = True
else:
    doesall = False

try:
    os.stat(boothfolder)
except FileNotFoundError:
    os.system(f'mkdir "{boothfolder}"')
    inp = input('update all the folders? [yes/no]').lower()
    if inp == 'y' or inp == 'yes':
        doesall = True
        print("P.S. rerun the program when it's done")
        print("P.P.S this raises an error, it's fine")

#command_to_run = "rename 's/\#/N/' *" #didnt work before because wrong directory
#print(command_to_run)
#command_to_run = "echo 'aaa'"
import parse
from datetime import datetime

def get_drlist(folder=folder):
    a = subprocess.check_output(["ls", '-U', '-t', folder]).decode('utf-8').strip().split("\n")
    return [i for i in a if '.py' not in i and '.pdf' not in i and 'Movie' not in i]

os.chdir(folder)#.replace(' ', '\ '))
#os.system("ls")

p = parse.compile("Photo on {:d}-{:d}-{:d} at {:d}.{:d} N{:d}")
q = parse.compile("Photo on {:d}-{:d}-{:d} at {:d}.{:d} #{:d}")
r = parse.compile("Photo on {:d}-{:d}-{:d} at {:d}.{:d}")
s = parse.compile("Photo on {:d}-{:d}-{:d} at {:d}.{:d} {}M N{:d}")
t = parse.compile("Photo on {:d}-{:d}-{:d} at {:d}.{:d} {}M")
def createtime(filenamee):
    filename = filenamee.replace('\\',  '').replace('#', 'N')
    updown = 'A' #default to not do anything
    try:
        month, day, year, hour, minute, index = p.parse(filename)
    except Exception as e:
        try:
            month, day, year, hour, minute, index = q.parse(filename)
        except Exception as e: #typeerror
            try:
                month, day, year, hour, minute = r.parse(filename)
                index = 0
            except Exception as e:
                try:
                    month, day, year, hour, minute, updown, index = s.parse(filename)
                except Exception as e:
                    try:
                        month, day, year, hour, minute, updown = t.parse(filename)
                        index = 0
                    except Exception as e:
                        print(filename)
    year = year+2000
    epoch = datetime(1970, 1, 1)
    d = datetime(year, month, day, hour, minute, index) #just use index as seconds because it works
    if updown == "P":
        return (d - epoch).total_seconds()+12*60*60 - 8*60*60
    else:
        return (d - epoch).total_seconds() - 8*60*60
    #timezone

lastrecent = None
def putInFolder(drlist1, boothfolder=boothfolder, folder=folder):
    global lastrecent

    latestbatch = []
    recentfile = drlist1[0]
    recentfilename = recentfile[:recentfile.rfind('.')] #"Photo At 10_10_10 #3"
    recent = createtime(recentfilename)

    #if recentfilename not in get_drlist(boothfolder) or doesall:
    if recentfilename != lastrecent or doesall:
        lastrecent = recentfilename
        #os.system(f'mkdir "{boothfolder}/{recentfilename}"')
        for i in drlist1: #drlist is ordered most recently created first
            filename=i[:i.rfind('.')] #"Photo At 10_10_10 #3"
            type=i[i.rfind('.'):] #".png"

            icreatetime = createtime(filename)
            if recent - icreatetime < 121: #cant be less than 2 minutes because how we're using the dates
                recent = icreatetime
                latestbatch.append(i)
            else:
                break

        assert len(set(latestbatch)) == len(latestbatch)

        boothdr = get_drlist(boothfolder)
        
        oldestbatchname = latestbatch[-1]
        #oldest file name in batch

        oldestbatchname = oldestbatchname[:oldestbatchname.rfind('.')]

        tofoldername = time.ctime(createtime(oldestbatchname))

        boothdr = get_drlist(boothfolder)
        if tofoldername not in boothdr:
            os.system(f'mkdir "{boothfolder}/{tofoldername}"')

        folderdr = get_drlist(f"{boothfolder}/{tofoldername}")

        for i in latestbatch[::-1]:
            filename = i[:i.rfind('.')] #"Photo At 10_10_10 #3"
            #if filename!=recentfilename and filename in boothdr:
            #    os.system(f'rm -r "{boothfolder}/{filename}"')
            #remove older folder
            newfilename = i.replace('#', 'N')
            if newfilename not in folderdr:
                os.system(f'cp "{folder}/{i}" "{boothfolder}/{tofoldername}/{newfilename}"')

        tmp = [i.replace('#', 'N') for i in latestbatch]
        fullpathlatestbatch = [f'{boothfolder}/{tofoldername}/{i}' for i in tmp]
        with open(f'{boothfolder}/{tofoldername}/pdf.pdf', 'wb') as file:
            file.write(img2pdf.convert(fullpathlatestbatch[::-1]))

        return latestbatch

while True:
    drlist1 = get_drlist()

    if doesall:
        todel = putInFolder(drlist1)
        running = drlist1[:]
        while todel:
            running = [i for i in running if i not in todel]
            #print(running)
            todel = putInFolder(running)
        break
    else:
        putInFolder(drlist1)

    time.sleep(2)

