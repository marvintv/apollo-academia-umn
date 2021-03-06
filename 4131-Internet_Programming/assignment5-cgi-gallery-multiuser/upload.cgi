#!/usr/bin/python

import cgi
import os
import glob
import time  # time for file name
import Image # for thumbnails :)
from shared import * # import common templates and variables
from database import *

# https://docs.python.org/2/library/cgi.html # Only instantiate only and exactly once 
form = cgi.FieldStorage()

#  onClick="(function(){document.form["uploadForm"].onSubmit="return true";})

uploadForm ="""
<form name="uploadForm" action="upload.cgi" method="POST" enctype="multipart/form-data" onSubmit="return checkFile()">
%(msg)s
Title: <input name="title" type="text"></br>
File: <input name="file" type="file" ></br>
<input name="submit" type="submit" value="Upload">
<a href="gallery.cgi"> <button type="button">Cancel</button></a>
</form>
""" 

clientSideCheckScript = """
<script>
	function checkFile(){
		var fileName = document.forms["uploadForm"]["file"].value;
		var ext = fileName.split('.').pop().toString().toLowerCase();
		if (ext == null || (ext != "jpg" && ext != "jpeg")){
			var x = document.createElement('div');
			x.id = "message";
                        x.innerHTML = "Please select a valid JPG/JPEG image";	
			if(document.getElementById("message") == null){
				document.forms["uploadForm"].insertBefore(x, document.forms["uploadForm"].firstChild);
			}
                        else {
                                var old = document.getElementById("message");
                                old.parentNode.replaceChild(x, old);
                        }
			return false;
		}
		return true;
	}
</script>
"""

strings = {
	'windowTitle': "Upload New Photo",
	'title': "Upload A New JPEG Picture",
	'body': "" # populated by functions
}


def generate_thumbnail(imageFile, saveThumbPathName):
	Image.LOAD_TRUNCATED_IMAGES = True
	img = Image.open(imageFile)
	img.thumbnail(THUMBNAIL_SIZE)
	img.save(saveThumbPathName, 'JPEG')

def save_title(filename, title):
	with open(filename, 'w') as file:
		file.write(title)

def save_uploaded_file (form_field, upload_dir):
    fileName = str(time.time())
    saveFilePathName = os.path.join(upload_dir, fileName + ".jpg")
    saveThumbPathName = os.path.join(upload_dir, fileName + "_tn.jpg")
    saveTitlePathName = os.path.join(upload_dir, fileName + ".txt")
    if not form.has_key(form_field): 
        msg = """<div id="message">Error: Please Try Again, File Not Uploaded Correctly. </div>"""
    	strings['body'] =  (uploadForm % {'msg' : msg }) + clientSideCheckScript
        print 'content-type: text/html\n'
        print HTML_TEMPLATE % strings
        return
    fileitem = form[form_field]
    if not fileitem.file or len(fileitem.filename) ==0: 
        msg = """<div id="message">Error: Please Try Again, Empty or Invalid File. </div>"""
    	strings['body'] = (uploadForm % {'msg' : msg }) + clientSideCheckScript 
        print 'content-type: text/html\n'
        print HTML_TEMPLATE % strings
        return
    try:

        with open(saveFilePathName, 'wb') as file:
    	    chunk = fileitem.file.read(100000)
            if not chunk:
        	    return
            file.write(chunk)

        generate_thumbnail(saveFilePathName,saveThumbPathName)
        save_title(saveTitlePathName, form['title'].value)
        # strings["body"] = "File Uploaded Successfully"
        # print HTML_TEMPLATE % strings
        REDIRECT('gallery.cgi')
        return
    except Exception as e:
        for aFile in glob.glob(os.path.join(upload_dir, fileName + "*")): # much cleaner
                os.remove(aFile)
        msg = """<div id="message">Error: Please Try Again, File Might not be a valid JPEG.</div>"""
    	strings['body'] = (uploadForm % {'msg' : msg }) + clientSideCheckScript 

        print 'content-type: text/html\n'
        print HTML_TEMPLATE % strings
        print "Python Image Library:" 
        print e # comment this to hide exception/errors

## This is what makes the cgi self contained and post to itself.
# Credit: http://www-users.cs.umn.edu/~tripathi/python/LectureExamples/helloSingleFile.py

# only logged in, admins can use this
if not isLoggedIn():
    REDIRECT('login.html')
else:
    db = Database()
    if not db.isOwnerFromCookie():
        REDIRECT('gallery.cgi')



# Client side check has removed need for nested ifs, but keeping this to ensure server has total control.
if 'file' in form and 'title' in form:
	if form['file'].file:
		if len(form['title'].value) > 0 and len(form['title'].value) < 100: # validate title is not empty (won't be in form if empty)
			save_uploaded_file ("file", UPLOAD_DIR)
		else:
                        msg = """<div id="message">Picture Title Cannot Be Empty or Too Long.</div>"""
            #            filename = "" # cannot repopulate file submission field server side, security issue
            #            if form['file'].file:
            #                    filename = form['file'].filename
                        strings['body'] = (uploadForm % {'msg' : msg}) + clientSideCheckScript 

                        print 'content-type: text/html\n'
			print HTML_TEMPLATE % strings
	else:
                strings['body'] = (uploadForm % {'msg' : "" }) + clientSideCheckScript
                print 'content-type: text/html\n'
		print HTML_TEMPLATE % strings
else:
	strings['body'] = (uploadForm % {'msg' : "" }) + clientSideCheckScript
        print 'content-type: text/html\n'
	print HTML_TEMPLATE % strings

