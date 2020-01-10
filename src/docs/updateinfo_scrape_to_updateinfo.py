#!/usr/bin/env python
'''
    This will import data from one updateinfo.xml into another.
    It is provided as another sample for how to use UpdateinfoHelper
'''

import sys
import re

from updateinfo.updateinfohelper import UpdateinfoHelper
from updateinfo.updateinfo import Updateinfo

class MakeUpdateinfo(UpdateinfoHelper):
    '''
        This is the class doing all the work
    '''
    def __init__(self, configfile, verbose=False):
        UpdateinfoHelper.__init__(self, configfile)

        self.infosrc = Updateinfo()
        self.infosrc.from_xml_file(self.config['datastore']['scrapefile'])

        self.build(verbose=verbose)

        self.unknown_packages.sort()
        for i in self.unknown_packages:
            print i

    def updateid_from_package(self, package):
        '''
            Given a package name, what is its update id?
        '''
        if self.config['datastore'].has_key('tuv_id_prefix'):
           prefix = self.config['datastore']['tuv_id_prefix']
        else:
           prefix = ''

        if self.config['datastore'].has_key('my_id_prefix'):
           my_prefix = self.config['datastore']['my_id_prefix']
        else:
           my_prefix = ''

        for entry in self.infosrc:
            if self.infosrc[entry].has_filename(package):
                my_id = self.infosrc[entry].updateid.replace(prefix,my_prefix)
                return (self.infosrc[entry].updateid, my_id)

    def add_entry(self, tuv_updateid, my_updateid):
        '''
            What do we know about this update id.
            We don't care about collections, packages, or references here
             just stuff that pertains to this update

            Once you've got the data here, simply add the entry in

            Descriptions of these values can be found in the
             updateinfo.xsd
        '''
        update_from = self.config['updatefrom']
        update_status = self.config['status']

        if re.findall('EA', tuv_updateid):
            update_type = 'enhancement'
        elif re.findall('BA', tuv_updateid):
            update_type = 'bugfix'
        elif re.findall('SA', tuv_updateid):
            update_type = 'security'
        else:
            update_type = self.infosrc[tuv_updateid].updatetype

        update_title = self.infosrc[tuv_updateid].title
        update_issue_date = self.infosrc[tuv_updateid].issued_date
        update_severity = self.infosrc[tuv_updateid].severity
        update_description = self.infosrc[tuv_updateid].description

        update_modifcation_date = None
        update_summary = None
        update_rights = None
        update_solution = None

        update_reboot = False
        update_restart = False
        update_relogin = False

        if 'desktop must be restarted' in update_description:
            update_relogin = True
        elif 'must be restarted' in update_description:
            update_restart = True
        if 'system must be rebooted' in update_description:
            update_reboot = True
        elif 'system rebooted' in update_description:
            update_reboot = True

        self._add_entry(my_updateid, update_from, update_status, update_type,
                       update_title, update_issue_date, update_modifcation_date,
                       update_description, update_summary, update_rights,
                       update_solution, update_severity, update_reboot,
                       update_restart, update_relogin)

    def add_references(self, tuv_updateid, my_updateid):
        '''
            What references are attached to this update?
             Find them and add them in
        '''

        for refurl in self.infosrc[tuv_updateid].list_references():
            myref = self.infosrc[tuv_updateid].get_reference(refurl)
            self._add_references(my_updateid, myref.reftype, myref.href,
                                   myref.refid, myref.title)

#############################################################################

import optparse
optparser = optparse.OptionParser()
optparser.add_option('--configfile', help='''What File''')
optparser.add_option('--verbose', action='store_true', help='''Be chatty''')
options = optparser.parse_args()[0]

if options.configfile == None:
    optparser.print_help()
    print '\nMissing arg --configfile'
    sys.exit(1)

MakeUpdateinfo(options.configfile, options.verbose)

