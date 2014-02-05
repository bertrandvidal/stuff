import os
from uuid import uuid4
from zipfile import ZipFile
import urllib2
import crypt
import spwd
import sys

ZIP_URL = "http://xato.net/files/10k%20most%20common.zip"
PASSWORDS_FILE = "10k most common.txt"
ZIP_FILE = os.path.join(os.path.abspath(os.path.dirname(__file__)), str(uuid4()))

if not os.path.exists(PASSWORDS_FILE):
  # Need this header otherwise get a 403
  req = urllib2.Request(ZIP_URL, headers={"User-Agent": "popo"})
  try:
    # Dump zip from URL
    with open(ZIP_FILE, "wb") as temp_zip:
      temp_zip.write(urllib2.urlopen(req).read())
    # Extract the zip file in the current dir
    with ZipFile(ZIP_FILE) as zip_file:
      zip_file.extractall()
  finally:
    # Remove the zip file
    if os.path.exists(ZIP_FILE):
      os.unlink(ZIP_FILE)

# Read the password from the downloaded file
with open(PASSWORDS_FILE, "r") as password_file:
  passwords = map(lambda x: x.strip(), password_file.readlines())

# Get entries from shadow password database
shadow_entries = [entry[:2] for entry in spwd.getspall()]

# We probably need the root access
if not shadow_entries:
  print "Can't access shadow password database - probably need root access"
  sys.exit(1)

for name, encrypted in shadow_entries:
  print "Processing password for user '%s':" % name,
  # This indicate that the user has no password
  if encrypted in ["*", "!"]:
    print "no hash to process"
    continue
  for password in passwords:
    # We use the encrypted version of the password as salt as adviced by
    # the crypt module's doc
    if crypt.crypt(password, encrypted) == encrypted:
      print "password is '%s'" % password
      break
  else:
    # The little magic of for/else loops
    print "failed to break password"

