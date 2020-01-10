'''
    Generating the updateinfo.xml isn't too bad
     but it can be messy mixing the data gathering with the object structure.

    This is an attempt to clean that up a bit.  Now your database is not part
     if your standard program logic.  This isn't MVC, but it is a stab in that
     general direction.
'''
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

# Version 0.1 by Pat Riehecky <riehecky@fnal.gov> for Scientific Linux

import updateinfo

import ConfigParser
import gzip
import os
import sys

# this is where modifyrepo.py is kept
sys.path.append('/usr/share/createrepo/')
from modifyrepo import RepoMetadata

# we work with either, but better with lxml
try:
    from lxml import etree as xmletree
except ImportError:
    import xml.etree.ElementTree as xmletree

class UpdateinfoHelper:
    '''
        This is a partial skeleton class for making the generation
         of updateinfo.xml really easy

        For this to work at all you will need to inherit this and define
         the following methods:

        add_entry(self, tuv_updateid, my_updateid)
         when it is done gathering the data you need it must call
         self._add_entry with the right args.  Optional things
         should be set to None, bools should be a bool.  Check the
         xsd for whats what.

        add_references(self, tuv_updateid, my_updateid)
         when it is done gathering the data you need it must call
         self._add_references with the right args

        updateid_from_package(self, package)
         it must return a tuple (tuv_updateid, my_updateid)
         if tuv_updateid == None, then this package is skipped

        You will have access to self.config['datastore'] which
         will be a key/value copy of the [datastore] section of your config
    '''
    def __init__(self, config_file):
        '''
            Sets up the containers
        '''
        self.myupdateinfo = updateinfo.Updateinfo()
        self.config = self.read_config(config_file)

        self.unknown_packages = [ ]

    def build(self, verbose=False):
        '''
            Once you've defined the needed methods
            call this function, it will do the rest
        '''
        if self.config['force_updatefrom']:
            self.myupdateinfo.force_updatefrom(self.config['updatefrom'])
        if self.config['force_status']:
            self.myupdateinfo.force_status(self.config['status'])
        if self.config['force_release_name']:
            self.myupdateinfo.force_release_name(self.config['release_name'])
        if self.config['force_collection_name']:
            self.myupdateinfo.force_collection_name(
                                           self.config['collection_name'],
                                           self.config['collection_short_name']
                                           )

        os.chdir(self.config['repobase'])
        if not os.path.exists('./repodata'):
            raise RuntimeError(self.config['repobase'] + " : no repodata")

        if self.config['import_existing']:
            if verbose:
                print 'Loading updateinfo.xml from repo if there is one'
            old_updateinfo = self.myupdateinfo.from_repo('.',
                                                    self.config['has_metainfo'])

        if verbose:
            print 'Parsing packages in repo'
        for package in self.get_filelist('.'):
            if not self.myupdateinfo.has_filename(package):
                if verbose:
                    print '  Adding', package
                self.add_package(package)


        if verbose:
            print 'Writing', self.config['xml']['filename']
        os.chdir(self.config['repobase'] + '/repodata')
        self.myupdateinfo.to_xml_file(self.config['xml']['filename'],
                                      self.config['xml']['validate'],
                                      self.config['xml']['comment'],
                                      self.config['xml']['pretty'])

        if self.config['update_repo']:
            self.add_updateinfo_to_repomd(old_updateinfo)

    def add_updateinfo_to_repomd(self, old_xml=None):
        '''
            Configures the repomd.xml to know about
             this new updateinfo.xml
            It will remove the old one automatically if you tell it
             what it was called.
        '''
        if old_xml != None:
            os.remove(old_xml)

        os.chdir(self.config['repobase'] + '/repodata')
        repomd = RepoMetadata('.')
        repomd.add(self.config['xml']['filename'])

    def read_config(self, thisfile):
        '''
            Unless otherwise specified, you must define all these entries

            #-----------------------------------------------------------
            # Sample config file:
            #-----------------------------------------------------------
            [repo]
            # this MUST be a local path, no urls
            repobase = /path/to/repo/like/in/yum.repos.d/conf
            import_existing = True
            has_metainfo = False
            update_repo = True

            # src_url_base is optional, but encouraged
            src_url_base = http://my.example.com/SRPMS/

            [package_data]
            # set values to find your package
            # data source for building the updateinfo file
            
            # If you set these, you can use them later for modifying the
            # ID of the announcement
            tuv_id_prefix=XX
            my_id_prefix=YY

            [ref_hints]
            # here are some examples
            cve_base = http://cve.mitre.org/cgi-bin/cvename.cgi?name=
            bugzilla_base = https://bugzilla.somesite.tld/show_bug.cgi?id=
            upstream_base = https://path.to.announcement.tld/errata/

            # if you've got this entry it is automatically used
            # for security errata suffixed by the severity
            severity_ref = https://somesite.com/security/classification/#

            [metadata]
            updatefrom = me@example.com
            force_updatefrom = False

            status = final
            force_status = False

            release_name = My Linux
            force_release_name = False

            collection_name = My Linux version
            collection_short_name = ML-V
            force_collection_name = False

            [xml]
            comment = Share - don't steal - this data
            validate = True
            pretty = False
            # relative paths are relative to repobase/repodata
            # absolute paths are absolute
            filename = updateinfo.xml
            merge_ids = False
        '''
        configfile = ConfigParser.SafeConfigParser()

        if not os.path.exists(thisfile):
            print >> sys.stderr, self.read_config.__doc__
            print >> sys.stderr, '\nMissing config file, see above for sample'
            sys.exit(1)

        configfile.read(thisfile)

        values = {}
        # get error later if this is undef
        values['xml'] = {}
        values['datastore'] = {}
        values['ref_hints'] = {}
        for section in configfile.sections():
            if section == 'repo':
                values['repobase'] = configfile.get(section, 'repobase')
                if configfile.has_option(section,'contains_metainfo'):
                    values['has_metainfo'] = configfile.get(section,'has_metainfo')
                    if values['has_metainfo'].lower() == 'false':
                        values['has_metainfo'] = False
                    elif values['has_metainfo'].lower() == 'true':
                        values['has_metainfo'] = True
                    else:
                        values['has_metainfo'] = False
                else:
                    values['has_metainfo'] = False

                if configfile.has_option(section,'update_repo'):
                    values['update_repo'] = configfile.get(section,'update_repo')
                    if values['update_repo'].lower() == 'false':
                        values['update_repo'] = False
                    elif values['update_repo'].lower() == 'true':
                        values['update_repo'] = True
                    else:
                        values['update_repo'] = True
                else:
                    values['update_repo'] = True
                if configfile.has_option(section,'import_existing'):
                    values['import_existing'] = configfile.get(section,'import_existing')
                    if values['import_existing'].lower() == 'false':
                        values['import_existing'] = False
                    elif values['import_existing'].lower() == 'true':
                        values['import_existing'] = True
                    else:
                        values['import_existing'] = True
                else:
                    values['import_existing'] = True

                if configfile.has_option(section,'src_url_base'):
                    values['srpm_url'] = configfile.get(section, 'src_url_base')
                else:
                    values['srpm_url'] = ''

            elif section == 'package_data':
                values['datastore'] = {}
                for entry in configfile.options(section):
                    values['datastore'][entry] = configfile.get(section, entry)
                    if values['datastore'][entry].lower() == 'false':
                        values['datastore'][entry] = False
                    elif values['datastore'][entry].lower() == 'true':
                        values['datastore'][entry] = True

            elif section == 'ref_hints':
                values['ref_hints'] = {}
                for entry in configfile.options(section):
                    values['ref_hints'][entry] = configfile.get(section, entry)
                    if values['ref_hints'][entry].lower() == 'false':
                        values['ref_hints'][entry] = False
                    elif values['ref_hints'][entry].lower() == 'true':
                        values['ref_hints'][entry] = True

            elif section == 'metadata':
                for entry in configfile.options(section):
                    values[entry] = configfile.get(section, entry)
                    if values[entry].lower() == 'false':
                        values[entry] = False
                    elif values[entry].lower() == 'true':
                        values[entry] = True

            elif section == 'xml':
                if configfile.has_option(section,'comment'):
                    values['xml']['comment'] = configfile.get(section, 'comment')
                else:
                    values['xml']['comment'] = None

                if configfile.has_option(section,'validate'):
                    values['xml']['validate'] = configfile.get(section, 'validate')
                    if values['xml']['validate'].lower() == 'false':
                        values['xml']['validate'] = False
                    elif values['xml']['validate'].lower() == 'true':
                        values['xml']['validate'] = True
                    else:
                        # default true for validation
                        values['xml']['validate'] = True
                else:
                    values['xml']['validate'] = True

                if configfile.has_option(section,'pretty'):
                    values['xml']['pretty'] = configfile.get(section, 'pretty')
                    if values['xml']['pretty'].lower() == 'false':
                        values['xml']['pretty'] = False
                    elif values['xml']['pretty'].lower() == 'true':
                        values['xml']['pretty'] = True
                    else:
                        values['xml']['pretty'] = False
                else:
                    values['xml']['pretty'] = False

                if configfile.has_option(section,'filename'):
                    values['xml']['filename'] = configfile.get(section, 'filename')
                else:
                    values['xml']['filename'] = 'updateinfo.xml'

                if configfile.has_option(section,'merge_ids'):
                    values['xml']['merge_ids'] = configfile.get(section, 'merge_ids')
                    if values['xml']['merge_ids'].lower() == 'false':
                        values['xml']['merge_ids'] = False
                    elif values['xml']['merge_ids'].lower() == 'true':
                        values['xml']['merge_ids'] = True
                    else:
                        values['xml']['merge_ids'] = False
                else:
                    values['xml']['merge_ids'] = False

        return values

    @staticmethod
    def get_filelist(repository):
        '''
            Open the filelist from the repository and return
            a list of rpms within the repository.
        '''
        repomd_xml = open(repository + '/repodata/repomd.xml', 'r')

        repomd = xmletree.fromstring(repomd_xml.read())
        xsd_prefix = '{http://linux.duke.edu/metadata'

        for repometadata in repomd.getchildren():
            if repometadata.attrib.has_key('type'):
                if repometadata.attrib['type'] == 'primary':
                    for inform in repometadata.getchildren():
                        if inform.tag == xsd_prefix + '/repo}location':
                            primaryxmlgz = repository + '/'
                            primaryxmlgz = primaryxmlgz + inform.attrib['href']

        primaryxml = open(repository + '/' + primaryxmlgz, 'r')

        raw_primaryxml = gzip.GzipFile(fileobj=primaryxml)

        primaryxml_obj = xmletree.fromstring(raw_primaryxml.read())

        rpm_list = [ ]
        for attribute in primaryxml_obj.getchildren():
            for child in attribute.getchildren():
                if child.tag == xsd_prefix + '/common}location':
                    rpm_list.append(child.attrib['href'])

        return rpm_list

    def _add_entry(self, my_updateid, update_from, update_status, update_type,
                   update_title, update_issue_date, update_modifcation_date,
                   update_description, update_summary, update_rights,
                   update_solution, update_severity, update_reboot,
                   update_restart, update_relogin):
        '''
            Add an entry for this update_id from your data store
            If reboot/restart/relogin are required set them here
             rather than with the packages please, it makes things
             much more clean
        '''
        entry = updateinfo.Entry()
        entry.set_update_metainfo(update_from, update_status, update_type)
        entry.set_title(update_title)
        entry.set_id(my_updateid)
        entry.set_issued_date(update_issue_date)
        entry.set_update_date(update_modifcation_date)

        # clean up white space and new lines in description, it can be
        # a bit free form and really needs to be somewhat less so
        # but I can't really clean it up so this is the best we are
        # going to get, clean it up before you send it in here ok!
        update_description = update_description.lstrip().rstrip()
        entry.set_description(update_description)

        entry.set_release_name(self.config['release_name'])
        entry.set_summary(update_summary)
        entry.set_rights(update_rights)
        entry.set_solution(update_solution)
        entry.set_severity(update_severity)
        entry.set_reboot_suggested(update_reboot)
        entry.set_restart_suggested(update_restart)
        entry.set_relogin_suggested(update_relogin)
    
        self.myupdateinfo.add_entry(entry,
                                 allow_id_merge=self.config['xml']['merge_ids'])
        if update_type == 'security' and update_severity != None:
            if self.config['ref_hints'].has_key('severity_ref'):
                self._add_references(my_updateid, 'other',
                     self.config['ref_hints']['severity_ref'] + update_severity,
                     update_severity, 'Issue Severity Classification')

    def _add_references(self, update_id, reftype, refurl, refid, reftitle):
        '''
            Add references from your data store to this entry
        '''
        if refurl not in self.myupdateinfo[update_id].references():
            ref = updateinfo.Reference(reftype, refurl, refid, reftitle)
            self.myupdateinfo[update_id].add_reference_obj(ref)

    def add_collection(self, update_id):
        '''
            Add a collection to this update_id
        '''
        my_collect = updateinfo.Collection(self.config['collection_name'],
                                           self.config['collection_short_name'])
        coll_id = self.myupdateinfo[update_id].add_collection_obj(my_collect)
        return coll_id

    def add_package(self, package):
        '''
            This function will find out all the infomation it can about a given
             package and add it to the right place in the updateinfo.xml

            If the package id is None it will be instead added to
             self.unknown_packages for you to querry later
        '''
        ids = self.updateid_from_package(package)

        if ids == None:
            self.unknown_packages.append(package)
            return None

        (tuv_updateid, my_updateid) =  ids

        if my_updateid not in self.myupdateinfo:
            self.add_entry(tuv_updateid, my_updateid)

        self.add_references(tuv_updateid, my_updateid)

        if self.config['collection_name'] in self.myupdateinfo[my_updateid]:
            collect_id = self.config['collection_name']
        elif self.config['collection_short_name'] in self.myupdateinfo[my_updateid]:
            collect_id = self.config['collection_short_name']
        else:
            collect_id = self.add_collection(my_updateid)

        pkg_object = updateinfo.Package(src_url_base=self.config['srpm_url'],
                                        rpmfile=package)
        self.myupdateinfo[my_updateid][collect_id].add_package_obj(pkg_object)
