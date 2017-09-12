# -*- coding: utf-8 -*-
from shutil import copyfile
import os, time, sys


#konfiguration
source = r"" #quellordner
target = r"" #zielordner
#duerfen nicht identisch sein
#duerfen nicht unterordner von einander sein




#argv:
goahead = 0
argIndex = 1
while argIndex < len(sys.argv):

	if sys.argv[argIndex] == "-h" or sys.argv[argIndex] == "--help":
		print "Script zum Anlegen von Sicherheitskopien mit Versionsnummern"
		print "https://github.com/sezanzeb/Backup-Repository-and-Version-Control-Script"
		print ""
		print "Zu beachten:"
		print "  Der Quellordner darf kein Unterordner des Zielordners sein."
		print "  Der Zielordner darf kein Unterordner des Quellordners sein."
		print "  Quell- und Zielordner dürfen nicht identisch sein."
		print "  Die Pfade von Quell- und Zielordner dürfen nicht leer sein. Der aktuelle Ordner kann so gewählt werden: \"./\"."
		print ""
		print "Verwendung:"
		print "  python repository.sh [optionen]"
		print "  -s  Quellordner"
		print "  -d  Zielordner"
		print "  -y  Automatisch mit \"ja\" Antworten solange kein Fehler erscheint"
		print "  -h  Hilfe"
		print ""
		print "Beispiele:"
		print "  python repository.py -s \"source/\" -d \"destination/\""
		print "  python repository.py -s ./ -d ../ordner/ -y"
		print ""
		exit()

	#-y: tell the script to go ahead without asking
	if sys.argv[argIndex] == "-y":
		goahead = 1

	#-s: source
	if sys.argv[argIndex] == "-s":
		#next arg must be the source
		argIndex += 1
		if argIndex >= len(sys.argv):
			print "nach -s muss der Pfad zum Quellordner angegeben werden!"
			exit()
		source = sys.argv[argIndex]

	#-d: destination
	if sys.argv[argIndex] == "-d":
		#next arg must be the source
		argIndex += 1
		if argIndex >= len(sys.argv):
			print "nach -d muss der Pfad zum Zielordner angegeben werden!"
			exit()
		target = sys.argv[argIndex]

	argIndex += 1

#prepare:
separator = os.path.sep
#make sure the folders end with a separator...
if source != "":
	source = (source+separator).replace(separator+separator,separator)
if target != "":
	target = (target+separator).replace(separator+separator,separator)

#validate step one:
exception = 0
if source == "":
	print("Es wurde keine Quelle angegeben! (z.B. als Argument -s \"quelle/\")");
	exception = 1
if target == "":
	print("Es wurde kein Ziel angegeben! (z.B. als Argument -d \"quelle/\")");
	exception = 1
if exception:
	print
	print("Siehe: python repository.py --help")
	print("beliebige Taste drücken...".decode("iso-8859-1"))
	raw_input()
	exit()

#validate step two:
exception = 0
if source.rfind(target) == 0: #this relies on the path being complete, including a separator at the end
	print("Der Quellordner darf kein Unterordner des Zielordners sein!")
	exception = 1
if target.rfind(source) == 0: #this relies on the path being complete, including a separator at the end
	print("Der Zielordner darf kein Unterordner des Quellordners sein!")
	exception = 1
if source == target:
	print("Quelle und Ziel sind identisch!")
	exception = 1
if not os.path.exists(source):
	print("Der Quellordner existiert nicht!");
	exception = 1
if exception:
	print
	print("Siehe: python repository.py --help")
	print("beliebige Taste drücken...".decode("iso-8859-1"))
	raw_input()
	exit()

#get user confirmation
if goahead == 0:
	yesno = "j"
	if not os.path.exists(target):
		#target folder will be created inside the loop
		yesno = str(raw_input("Der Zieldordner existiert noch nicht. Neu anlegen? [j/n]: "))
	if yesno.lower().rfind("j") == -1:
		print("Siehe: python repository.py --help")
		print("beliebige Taste drücken...".decode("iso-8859-1"))
		raw_input()
		exit()
	print("")
	print("Quelle ist "+source.decode("iso-8859-1"))
	print("Ziel ist "+target.decode("iso-8859-1"))
	yesno = str(raw_input("Fortfahren? [j/n]: "))
	if yesno.lower().rfind("j") == -1:
		print("Siehe: python repository.py --help")
		print("beliebige Taste drücken...".decode("iso-8859-1"))
		raw_input()
		exit()
	else:
		print("")

#in no case should the target or source be a empty "" string by now

#since there was the separator automatically added to the end of target and source,
#the script has to temporarily remove it in this case to be able to split correctly
#repositoryIndicator = str.split(source[0:-1],separator)[-1]+"Rep"
#zur sicherheit, dass nichts falsches ueberschrieben wird
#target = target+separator+repositoryIndicator

changedCount = 0
for filePath, subFolders, fileNames in os.walk(source):

	#iterate over all files (also those that are contained in subdirectories)
	for fileName in fileNames:


		#get the relative path of the file to the source folder
		relativePath = filePath[len(source):]+separator
		if relativePath == separator:
			relativePath = ""


		#set some variables
		#make sure that files that don't have a type work aswell
		fileType = ""
		if fileName.rfind(".") != -1: #if there is a type
			fileType = "."+str.split(fileName,".")[-1:][0]
			fileName = fileName[0:-len(fileType)]
		try:
			fileDateFloat = os.path.getmtime(filePath+separator+fileName+fileType)
		except:
			print("Konnte die Zeit von der Datei "+fileName+" nicht lesen")
			break
		fileDate = time.ctime(fileDateFloat)
		repositoryDate = 0
		#make sure the target folder structure exists
		try:
			if not os.path.exists(target+separator+relativePath):
				os.makedirs(target+separator+relativePath)
		except:
			#to avoid confusion for the user, delete double separators. The OS will handle those correctly usually
			path = (target+separator+relativePath).replace(separator+separator,separator)
			print("Konnte den Ordner "+path+" nicht erstellen")
			break

		#reset file version counter
		versionCounter = 0;
		#get the most recent version in the repository
		#it can be recognized by looking at the (\d*?) part, that should be right before the type
		#that means, just look for the last opening bracket and for the...
		#...closing bracket position (rfind("(")+1 and -len(filetype)-1)
		#inbetween those there should be the number. If not that means the repository contains invalid files
		#make sure that the part before the opening bracket is equal to the original filename
		for candidate in os.listdir(target+separator+relativePath):
			if candidate[0:candidate.rfind("(")+1] == fileName+"(" and candidate[-len(fileType)-1:] == ")"+fileType:
				try:
					newVersionCounter = int(candidate[candidate.rfind("(")+1:-len(fileType)-1])
					#if the found file is the newest file (os.walk does not take care about ordering the filenames)
					if newVersionCounter > versionCounter:
						versionCounter = newVersionCounter
						repositoryDate = time.ctime(os.path.getmtime(target+separator+relativePath+candidate))
				except: #if the version in the filename could not be parsed/found just go on and do nothing.
					path = (target+relativePath+separator+candidate).replace(separator+separator,separator)
					print(("Die Datei "+path+" hat keine oder eine fehlerhafte Versionsnummer!").decode("iso-8859-1"))
					#this is not a criteria to skip that file. It will copy the source file and add a (hopefully) correct version number to it


		#now increment to store a new version
		versionCounter += 1

		#if there is a difference in the modified date and time, create a new backup
		if not (repositoryDate == fileDate):
			cpSrc = (source+separator+relativePath+fileName+fileType).replace(separator+separator,separator)
			cpTrg = (target+separator+relativePath+fileName+"("+str(versionCounter)+")"+fileType).replace(separator+separator,separator)
			cpTrg = cpTrg.decode("iso-8859-1")

			print((cpSrc+" wird neu in den Zielordner kopiert mit Versionsnr. "+str(versionCounter)).decode("iso-8859-1"))
			if repositoryDate != 0:
				print(str(repositoryDate))
			print(str(fileDate))
			#for a better user experience
			changedCount += 1

			try:
				copyfile(cpSrc,cpTrg)
			except:
				print("Fehler beim kopieren der Datei "+cpSrc)
				break
			#python will override the modified date when copying. That's why the script needs to change it back
			os.utime(cpTrg,(fileDateFloat,fileDateFloat))

#end
if changedCount == 0:
	print("Keine neuen Dateien erkannt")
else:
	print
	print(str(changedCount)+" geänderte Dateien wurden erkannt".decode("iso-8859-1"))
print("beliebige Taste drücken...".decode("iso-8859-1"))
raw_input()
