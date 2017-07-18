# Backup-Repository-and-Version-Control-Script

You can set the target and destination folder inside the script at the top. Make sure they are not the same or empty or subfolders of each other. Install python with:

    sudo apt install python

Save the code above to repository.py. Then you can run the sript using a console and:

    python repository.py

All files inside the source folder will be copied to the target folder. When there is already a version existing in the target folder, the script will check if it is old and copy it with an incremented version number in that case.

The script only uses some mkdir and copy code. Of course, copy could overwrite your files, but the script would increment the version number when a conflict is detected. Use it at your own risk. The good thing with open source is, that you can look at the code yourself and decide wether or not you trust it. It would be wise to try it with some dummy files first to see, if it works on your system. Tested with ubuntu and windows 10.
