#!/usr/bin/env python
'''
    This is a simple skeleton for making your own implementation class
    for using UpdateinfoHelper to make your updateinfo.xml
'''

from updateinfo.updateinfohelper import UpdateinfoHelper

class MakeUpdateinfo(UpdateinfoHelper):
    def __init__(self, configfile, verbose=False):
        UpdateinfoHelper.__init__(self, configfile)

        self.build(verbose=verbose)

    def updateid_from_package(self, package):
        '''
            Given a package name, what is its
            update id and what my update id?
        '''
               # tuv-id  # My-id
        return ('1234', 'MY-1234')

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
        update_type = 'newpackage'
        update_title = 'its an update'
        update_issue_date = '2011-10-25 16:03:34'
        update_description = 'look it fixes" stuff'
        update_severity = 'low'
        update_summary = None
        update_rights = None
        update_solution = None
        update_modifcation_date = None
        update_reboot = True
        update_restart = False
        update_relogin = False

        self._add_entry(my_updateid, update_from, update_status, update_type,
                   update_title, update_issue_date, update_modifcation_date,
                   update_description, update_summary, update_rights,
                   update_solution, update_severity ,update_reboot,
                   update_restart, update_relogin)

    def add_references(self, tuv_updateid, my_updateid):
        '''
            What references are attached to this update?
             Find them and add them in
        '''

        self._add_references(my_updateid, 'bugzilla',
                             'http://mybugzillaurl.com/?bug=1234', '1234', 'mytitle')
        self._add_references(my_updateid, 'cve',
                             'http://cve.mitre.org/cgi-bin/cvename.cgi?name=' + 'CVE-2012-0000', 'CVE-2012-0000', 'mytitle')

        self._add_references(my_updateid, 'self',
                             'http://path.to.tuv.com/name=' + tuv_updateid, tuv_updateid, tuv_updateid)

print "# "
print "# This isn't really here for you to run it"
print "# You can run it, but you will need a config file"
print "# I've provided a sample, but you will need to edit it first"
print "# or it wont work at all"
print "# "
print "# See simple.cfg in the 'doc' dir for more getting started quickly."
print "# "

import optparse
optparser = optparse.OptionParser()
optparser.add_option('--configfile', help='''What File''')
optparser.add_option('--verbose', action='store_true', help='''Be chatty''')
options = optparser.parse_args()[0]

MakeUpdateinfo(options.configfile, options.verbose)

