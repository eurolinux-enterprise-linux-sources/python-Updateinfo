#!/usr/bin/env python
'''
    This is a sample script that imports an existing updateinfo file
    and adds a dummy entry.  It then prints the output.
'''
DOCDIR = '/usr/share/doc/python-Updateinfo/samples/'

from updateinfo import Updateinfo
import updateinfo

import sys
if len(sys.argv) != 3:
    print >> sys.stderr, "Usage:"
    print >> sys.stderr, " " + sys.argv[0] + ' <updateinfo.xml> <path_to_rpm>' 
    print >> sys.stderr, " "

    print >> sys.stderr, " You must name an updateinfo"
    print >> sys.stderr, "   I suggest picking one of the samples in"
    print >> sys.stderr, "   " + DOCDIR
    print >> sys.stderr, " "
    print >> sys.stderr, " ie. " + sys.argv[0] + ' ' + DOCDIR + 'simple.xml'
    print >> sys.stderr, " "
    print >> sys.stderr, " You must name a rpm"
    print >> sys.stderr, "   any rpm will do, but you need one for this example"
    sys.exit(1)

MYUPDATEINFO = Updateinfo()

# open an existing updateinfo and add this to it
# to start from scratch you can just skip this line
MYUPDATEINFO.from_xml_file(sys.argv[1])

# make an entry
ENTRY = updateinfo.Entry()
ENTRY.set_update_metainfo('asdf@jkl.com', 'stable', 'recommended')
ENTRY.set_title('some update')
ENTRY.set_id('SLID-12354')
ENTRY.set_issued_date('2012-08-25 16:03:34')
ENTRY.set_description('look it fixes" stuff and Ive described it')
ENTRY.set_release_name('Scientific Linux')
ENTRY.set_reboot_suggested(True)
ENTRY.set_restart_suggested(True)
ENTRY.set_relogin_suggested(True)

# make a reference
REF = updateinfo.Reference('bugzilla',
                           'http://mybugzillaurl.com/bug#1234',
                           '1234',
                           'mytitle')

# add the reference to the entry
ENTRY.add_reference_obj(REF)

# make a collection
COLLECTION = updateinfo.Collection('Scientific Linux 6', 'SL-6')

# make a package
PACKAGE = updateinfo.Package('http://url.for.source.com/',
                             sys.argv[2])
COLLECTION.add_package_obj(PACKAGE)
ENTRY.add_collection_obj(COLLECTION)

MYUPDATEINFO.add_entry(ENTRY)

# this will validate it before returning it (if you've got lxml)
# and then print it, this isn't pretty
MY_COMMENT = 'modifyrepo updateinfo.xml /path/to/repodata/'
print MYUPDATEINFO.get_xml(comment=MY_COMMENT, pretty=True)

