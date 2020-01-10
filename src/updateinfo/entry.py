'''
    Each update requires an entry describing it.  The entry
    has a few parts.  The doc in this module will help you with
    what you need.
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

# we work with either, but better with lxml
try:
    import lxml
    from lxml import etree as xmletree
except ImportError:
    import xml.etree.ElementTree as xmletree

import datetime

from collection import Collection
from reference import Reference

class Entry:
    '''
        For each entry you want to add to Updateinfo you must first
        create an instance of this object.  It will help guide you into
        adding all the attributes you need.

        You will need some collections, that comes from another object
        You might need some references, that comes from another object

        You can sorta treat this like a dict for collections.
    '''
    def __init__(self):
        '''
            This takes no arguments.  So you will need all the various
            'set_*' methods for fixing this up.

            You will need:
             set_update_metainfo()
             set_id()
             set_title()
             set_issued_date()
             set_description()
             set_release_name()

            You can use set_[id|title|description] to combine those
             if you wish.  It may make your code more easy to understand.

            Techically description seems to be optional, but don't abuse that.
            Leaving it out is sad!

            You will need to add a collection of packages.
            You might want to add a reference for the update.

            Relevant metainfo vars:
             self.status
             self.updatefrom
             self.updatetype
             self.updateinfo_version
             self.release_name
             self.update_id
             self.title
             self.severity
             self.issued_date
             self.update_date
             self.description
             self.solution
             self.rights
             self.summary
             self.reboot_suggested
             self.restart_suggested
             self.relogin_suggested
        '''
        self.status = None
        self.updatefrom = None 
        self.updatetype = None

        # pulled from Fedora, but we are also compatible with Suse too...
        self.updateinfo_version = '1.4'

        self.release_name = None

        self.updateid = None
        self.title = None
        self.severity = None
        self.issued_date = None
        self.update_date = None
        self.description = None
        self.solution = None
        self.rights = None
        self.summary = None

        self.reboot_suggested = False
        self.restart_suggested = False
        self.relogin_suggested = False

        self.reference = { }
        self.pkgcolllist = { }

        self.__collection_name = None
        self.__collection_short_name = None

    def __str__(self):
        '''
            Simple way of dumping the xml
        '''
        return self.return_xml(header=False, pretty=True)

    def __iter__(self):
        '''
            Used for: looping though collections
        '''
        return iter(self.pkgcolllist)

    def __getitem__(self, key):
        '''
            Used for: collection accessing items like a dict
        '''
        return self.pkgcolllist[key]

    def __contains__(self, key):
        '''
            Used for: x in obj
             this tracks collections
        '''
        if key in self.collections():
            return True
        return False

    def merge(self, new_entry):
        '''
            If you've got two entries with the same ID but some
             different data, like say an extra collection or
             different packages in a given collection,
             this function can merge the two entries.

            Any values already set in your entry will stay the same
             but anything new will be added in.

            You can't use 'merge' when the force_collection stuff
             is active
        '''
        if self.__collection_name != None:
            raise RuntimeError("Can't force collections and merge them")
        if self.__collection_short_name != None:
            raise RuntimeError("Can't force collections and merge them")

        if not isinstance(new_entry, Entry):
            raise TypeError("Should be of type 'updateinfo.Entry'")

        if self.release_name == None:
            self.set_release_name(new_entry.release_name)
        if self.updateid == None:
            self.set_id(new_entry.updateid)
        if self.title == None:
            self.set_title(new_entry.title)
        if self.severity == None:
            self.set_severity(new_entry.severity)
        if self.issued_date == None:
            self.set_issued_date(new_entry.issued_date)
        if self.update_date == None:
            self.set_update_date(new_entry.update_date)
        if self.description == None:
            self.set_description(new_entry.description)
        if self.solution == None:
            self.set_solution(new_entry.solution)
        if self.rights == None:
            self.set_rights(new_entry.rights)
        if self.summary == None:
            self.set_summary(new_entry.summary)

        if self.reboot_suggested == False:
            self.set_reboot_suggested(new_entry.reboot_suggested)
        if self.restart_suggested == False:
            self.set_restart_suggested(new_entry.restart_suggested)
        if self.relogin_suggested == False:
            self.set_relogin_suggested(new_entry.relogin_suggested)

        for refurl in new_entry.reference.keys():
            if not self.has_reference(refurl):
                self.add_reference_obj(new_entry.reference[refurl])

        for collect in new_entry.collections():
            this_key = self.has_package_collection(collect)
            if this_key == None:
                self.add_collection_obj(new_entry[collect])
            else:
                self.pkgcolllist[this_key].merge(new_entry[collect])

    def set_update_metainfo(self, updatefrom, status, updatetype):
        '''
            This is just a wrapper around:
             entry.set_from()
             entry.set_status()
             entry.set_updatetype()
            for cleaning up your required methods
        '''
        self.set_from(updatefrom)
        self.set_status(status)
        self.set_updatetype(updatetype)

    def set_summary(self, summary):
        '''
            For setting
               <update><summary>xxxx</summary>
            I'm optional
        '''
        if summary != None:
            if isinstance(summary, str):
                self.summary = unicode(summary, encoding='utf-8')
            elif isinstance(summary, unicode):
                self.summary = summary
            else:
                raise TypeError("Wrong type " + summary +
                                " type " + type(summary))
        else:
            self.summary = None

    def set_rights(self, rights):
        '''
            For setting
               <update><rights>xxxx</rights>
            I'm optional
        '''
        if rights != None:
            if isinstance(rights, str):
                self.rights = unicode(rights, encoding='utf-8')
            elif isinstance(rights, unicode):
                self.rights = rights
            else:
                raise TypeError("Wrong type " + rights +
                                " type " + type(rights))
        else:
            self.rights = None

    def set_solution(self, solution):
        '''
            For setting
               <update><solution>xxxx</solution>
            I'm optional
        '''
        if solution != None:
            if isinstance(solution, str):
                self.solution = unicode(solution, encoding='utf-8')
            elif isinstance(solution, unicode):
                self.solution = solution
            else:
                raise TypeError("Wrong type " + solution +
                                " type " + type(solution))
        else:
            self.solution = None

    def set_release_name(self, release_name):
        '''
            For setting
               <update><release>xxxx</release>
        '''
        if release_name != None:
            if isinstance(release_name, str):
                self.release_name = unicode(release_name, encoding='utf-8')
            elif isinstance(release_name, unicode):
                self.release_name = release_name
            else:
                raise TypeError("Wrong type " + release_name +
                                " type " + type(release_name))
        else:
            self.release_name = None

    def set_status(self, status):
        '''
            For setting
               <update status="xxxxxx">

            Should this be consistant throughout the whole file?
            That depends....
        '''
        if status != None:
            if isinstance(status, str):
                self.status = unicode(status, encoding='utf-8')
            elif isinstance(status, unicode):
                self.status = status
            else:
                raise TypeError("Wrong type " + status +
                                " type " + type(status))
        else:
            self.status = None

    def set_from(self, updatefrom):
        '''
            For setting
               <update from="xxxxxx">

            Should this be consistant throughout the whole file?
            That depends....
        '''
        if updatefrom != None:
            if isinstance(updatefrom, str):
                self.updatefrom = unicode(updatefrom, encoding='utf-8')
            elif isinstance(updatefrom, unicode):
                self.updatefrom = updatefrom
            else:
                raise TypeError("Wrong type " + updatefrom + " type " +
                                type(updatefrom))
        else:
            self.updatefrom = None

    def set_xmlversion(self, version):
        '''
            For setting
               <update version="xxxxxx">

            Should this be consistant throughout the whole file?
            That depends....

            Odds are you shouldn't ever set this, the default is fine
        '''
        self.updateinfo_version = version

    def set_updatetype(self, updatetype):
        '''
            For setting
               <update type="xxxxxx">
        '''
        if updatetype != None:
            if isinstance(updatetype, str):
                self.updatetype = unicode(updatetype, encoding='utf-8')
            elif isinstance(updatetype, unicode):
                self.updatetype = updatetype
            else:
                raise TypeError("Wrong type " + updatetype +
                                " type " + type(updatetype))
        else:
            self.updatetype = None

    def set_severity(self, severity):
        '''
            For setting
               <update><severity>xxxxxxxxx</severity>
            security updates only
        '''
        if severity != None:
            if isinstance(severity, str):
                self.severity = unicode(severity.lower(), encoding='utf-8')
            elif isinstance(severity, unicode):
                self.severity = severity.lower()
            else:
                raise TypeError("Wrong type " + severity +
                                " type " + type(severity))
        else:
            self.severity = None

    def set_id(self, updateid, title=None, description=None):
        '''
            For setting
               <update><id>xxxxxxxxxx</id>

            You can also set title and description from here
             trying to cleanup the methods to make them look pretty
             when you call them
        '''
        self.updateid = updateid

        if title != None:
            self.set_title(title)
        if description != None:
            self.set_description(description)

    def set_title(self, title, updateid=None, description=None):
        '''
            For setting
               <update><title>xxxxxxxxxx</title>

            Don't make this more than 65 chars, it makes it hard to read

            You can also set id and description from here
             trying to cleanup the methods to make them look pretty
             when you call them.

            I'm optional, but set me ok!
        '''
        if title != None:
            if isinstance(title, str):
                self.title = unicode(title, encoding='utf-8')
            elif isinstance(title, unicode):
                self.title = title
            else:
                raise TypeError("Wrong type " + title +
                                " type " + type(title))
        else:
            self.title = None

        if updateid != None:
            self.set_id(updateid)
        if description != None:
            self.set_description(description)

    def set_issued_date(self, issued_date):
        '''
           Note, this shoule be in format
                    2011-10-25 16:03:34
                 or 2011-10-25
                 or epoch time
                 or a datetime.datetime object
        '''
        # epoch time
        if isinstance(issued_date, int):
            self.issued_date = datetime.datetime.fromtimestamp(issued_date)
        elif isinstance(issued_date, str):
            try:
                self.issued_date = datetime.datetime.strptime(issued_date, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                self.issued_date = datetime.datetime.strptime(issued_date, '%Y-%m-%d')
        elif isinstance(issued_date, datetime.datetime):
            self.issued_date = issued_date
        else:
            raise ValueError('Wrong format for date string')

    def set_update_date(self, update_date):
        '''
           Note, this shoule be in format
                    2011-10-25 16:03:34
                 or 2011-10-25
                 or epoch time
                 or a datetime.datetime object
            I'm optional
        '''
        # epoch time
        if isinstance(update_date, int):
            self.update_date = datetime.datetime.fromtimestamp(update_date)
        elif isinstance(update_date, str):
            try:
                self.update_date = datetime.datetime.strptime(update_date, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                self.update_date = datetime.datetime.strptime(update_date, '%Y-%m-%d')
        elif isinstance(update_date, datetime.datetime):
            self.update_date = update_date
        elif update_date == None:
            self.update_date = update_date
        else:
            raise ValueError('Wrong format for date string')

    def set_description(self, description, updateid=None, title=None):
        '''
            For setting
               <update><description>xxxxxxxxxx</description>

            This is a description of why this update exists, not
            the package itself!

            You can also set id and title from here
             trying to cleanup the methods to make them look pretty
             when you call them

            I'm optional, but set me ok!
        '''
        if description != None:
            if isinstance(description, str):
                self.description = unicode(description, encoding='utf-8')
                self.description = self.description.replace('\r','')
            elif isinstance(description, unicode):
                self.description = description
                self.description = self.description.replace('\r','')
            else:
                raise TypeError("Wrong type " + description +
                                " type " + type(description))
        else:
            self.description = None

        if updateid != None:
            self.set_id(updateid)
        if title != None:
            self.set_title(title)

    def set_reboot_suggested(self, value):
        '''
            suggest rebooting the whole system?
            Set to True/False, default is False
        '''
        if value == True:
            self.reboot_suggested = True
        else:
            self.reboot_suggested = False

    def set_restart_suggested(self, value):
        '''
            suggest restarting the processes provided?
            Set to True/False, default is False
        '''
        if value == True:
            self.restart_suggested = True
        else:
            self.restart_suggested = False

    def set_relogin_suggested(self, value):
        '''
            suggest logout and login?
            Set to True/False, default is False
        '''
        if value == True:
            self.relogin_suggested = True
        else:
            self.relogin_suggested = False

    def check_values(self):
        '''
            Make sure we've got everything we need set.
            May throw ValueError if you've got some bad data... heads up

            Nothing calls this, but this function should help you
             see what you need.  It may be out of sync with the xsd so beware.
        '''
        if self.status == None or self.updatefrom == None:
            return False
        if self.updatetype == None or self.updateid == None:
            return False
        if self.issued_date == None:
            return False

        if not self.pkgcolllist:
            return False

        # release name might be in collection, so it isn't required

        # A title is not actually required..... :(
        # A description is not actually required..... :(

        if self.severity != None or self.updatetype == 'security':
            if self.severity not in ['critical', 'important',
                                         'moderate', 'low']:
                raise ValueError('''severity not 'critical', 'important',
                                    'moderate', or 'low''')

        if self.status not in ['stable', 'testing', 'final']:
            raise ValueError("Status type not 'stable', 'testing' or 'final'")

        if self.updatetype not in ['recommended', 'security', 'optional',
                              'feature', 'bugfix', 'enhancement', 'newpackage']:
            raise ValueError("""Update type not 'recommended' ,'security',
                                'optional', 'feature', 'bugfix', 'enhancement',
                                 or 'newpackage'""")

        return True

    def has_reference(self, refurl):
        '''
            Is a given url already in the reference list?
        '''
        return self.reference.has_key(refurl)

    def list_references(self):
        '''
            Return a list of all reference urls
        '''
        return self.reference.keys()

    def add_reference_obj(self, refobj):
        '''
            Should be an updateinfo.Reference object

            NOTE: each reference for an entry requires a unique URL!!!
                  so keep that in mind when you make them
        '''
        if isinstance(refobj, Reference):
            if refobj.href != None:
                if not self.has_reference(refobj.href):
                    self.reference[refobj.href] = refobj
                else:
                    print self
                    raise ValueError("Already have this url", refobj.href)
            else:
                raise ValueError("No url for reference object")
        else:
            raise TypeError("Should be of type 'updateinfo.Reference'")

    def del_reference(self, refurl):
        '''
            Removes a reference (by url) from this entry
        '''
        del self.reference[refurl]

    def get_reference(self, refurl='all'):
        '''
            Returns the reference requested.
            You can either request a given url or 'all'
            If you ask for 'all', you will get back all reference objects as a
             tuple.  Otherwise it is just the reference object itself.
        '''
        if refurl == 'all':
            reflist = [ ]
            for key in self.reference.keys():
                reflist.append(self.reference[key])
            return tuple(reflist)

        return self.reference[refurl]

    def add_collection_obj(self, pkgcollobj):
        '''
            Should be an updateinfo.Collection object
        '''
        if isinstance(pkgcollobj, Collection):
            # if force do it
            if self.__collection_name != None:
                pkgcollobj.set_name(self.__collection_name)
                pkgcollobj.set_short_name(self.__collection_short_name)

            if pkgcollobj.short_name != None:
                name = pkgcollobj.short_name
                self.pkgcolllist[pkgcollobj.short_name] = pkgcollobj
            elif pkgcollobj.release_name != None:
                name = pkgcollobj.release_name
                self.pkgcolllist[pkgcollobj.release_name] = pkgcollobj
            else:
                print self
                print pkgcollobj
                raise ValueError("Collection contains no release names")

            # return the shortcut name we used
            return name
        else:
            raise TypeError("Should be of type 'updateinfo.Collection'")

    def has_package_collection(self, collectionname):
        '''
            Check for a given collection by name, short or long

            returns the key containing the collection, or None
        '''
        for collect in self.pkgcolllist.keys():
            if self.pkgcolllist[collect].release_name == collectionname:
                return collect
            elif self.pkgcolllist[collect].short_name == collectionname:
                return collect
        return None

    def del_package_collection(self, collection):
        '''
            Remove a given collection by name
        '''
        del self.pkgcolllist[collection]

    def force_collection_name(self, collection_name, short_name=None):
        '''
            All updates will have the following value as their
            '<update><collection><name>xxxx</name></collection>' value

            Be careful with this, if you've got multiple collections
            this will destroy them!
        '''
        # if we were called but not passed good values
        if collection_name == None and short_name == None:
            return True

        self.__collection_name = collection_name
        self.__collection_short_name = short_name

        for this in self.pkgcolllist.keys():
            self.pkgcolllist[this].set_name(self.__collection_name)
            self.pkgcolllist[this].set_short_name(self.__collection_short_name)

    def collections(self):
        '''
            return the collections within this entry
            This is basically the 'keys' method for collections as a dict
        '''
        return self.pkgcolllist.keys()

    def references(self):
        '''
            return all the reference urls
        '''
        return self.reference.keys()

    def has_filename(self, filename, collection=None):
        '''
            Useful for seeing if a given filename is within this entry
            you can narrow the scope to a particular collection if you wish
        '''
        if filename in self.get_filenames(collection):
            return True
        return False

    def get_filenames(self, collection=None):
        '''
            return a list of files in the entry
            you can narrow the scope to a particular collection if you wish
        '''
        mylist = [ ]
        if collection == None:
            for this in self.pkgcolllist.keys():
                collect_rpms = self.pkgcolllist[this].get_filenames()
                for package in collect_rpms:
                    mylist.append(package)
        elif collection in self.collections():
            collect_rpms = self.pkgcolllist[collection].get_filenames()
            for package in collect_rpms:
                mylist.append(package)
        else:
            coll_list = self.collections()
            raise ValueError('No such collection', collection,
                                              'current entries', coll_list)
        return mylist

    def return_xml(self, header=True, pretty=False):
        '''
            returns the xml generated by this object
        '''
        if header:
            xml_header = '<?xml version="1.0" encoding="UTF-8"?>\n'
        else:
            xml_header = ''
        xml_string = xml_header + xmletree.tostring(self.to_xml_obj())

        if pretty:
            # since we don't have to require lxml, we are doing this
            # with the 'native' dom objects.  It is a bit ugly
            # but should be pure python and therefore portable.
            from xml.dom import minidom
            from xml.dom.ext import PrettyPrint
            from StringIO import StringIO
            dom_string = minidom.parseString(xml_string)
            tmpstream = StringIO()
            PrettyPrint(dom_string, stream=tmpstream, encoding='UTF-8')
            xml_string = tmpstream.getvalue()
            tmpstream.close()

        return xml_string

    def to_xml_obj(self):
        '''
            returns an xml.etree.ElementTree.Element object of the package
        '''
        xmlobj = xmletree.Element('update')
        if self.updatetype != None:
            xmlobj.attrib['type'] = self.updatetype

        if self.updatefrom != None:
            xmlobj.attrib['from'] = self.updatefrom

        if self.status != None:
            xmlobj.attrib['status'] = self.status

        if self.updateinfo_version != None:
            xmlobj.attrib['version'] = self.updateinfo_version

        id_obj = xmletree.Element('id')
        if self.updateid != None:
            id_obj.text = self.updateid
        xmlobj.append(id_obj)
        
        if self.title != None:
            title_obj = xmletree.Element('title')
            title_obj.text = self.title
            xmlobj.append(title_obj)
        
        if self.description != None:
            description_obj = xmletree.Element('description')
            description_obj.text = self.description
            xmlobj.append(description_obj)

        if self.severity != None:
            severity_obj = xmletree.Element('severity')
            severity_obj.text = self.severity
            xmlobj.append(severity_obj)

        if self.summary != None:
            summary_obj = xmletree.Element('summary')
            summary_obj.text = self.summary
            xmlobj.append(summary_obj)
        
        if self.rights != None:
            rights_obj = xmletree.Element('rights')
            rights_obj.text = self.rights
            xmlobj.append(rights_obj)
        
        if self.solution != None:
            solution_obj = xmletree.Element('solution')
            solution_obj.text = self.solution
            xmlobj.append(solution_obj)
        
        if self.release_name != None:
            release_obj = xmletree.Element('release')
            release_obj.text = self.release_name
            xmlobj.append(release_obj)

        issued_date_obj = xmletree.Element('issued')
        if self.issued_date != None:
            issued_date_obj.attrib['date'] = str(self.issued_date)
        xmlobj.append(issued_date_obj)

        if self.update_date != None:
            update_date_obj = xmletree.Element('updated')
            update_date_obj.attrib['date'] = str(self.update_date)
            xmlobj.append(update_date_obj)
        
        if self.reboot_suggested:
            reboot_obj = xmletree.Element('reboot_suggested')
            reboot_obj.text = 'true'
            xmlobj.append(reboot_obj)
        if self.restart_suggested:
            restart_obj = xmletree.Element('restart_suggested')
            restart_obj.text = 'true'
            xmlobj.append(restart_obj)
        if self.relogin_suggested:
            relogin_obj = xmletree.Element('relogin_suggested')
            relogin_obj.text = 'true'
            xmlobj.append(relogin_obj)

        ref_obj = xmletree.Element('references')
        for ref_item in self.reference.keys():
            ref_obj.append(self.reference[ref_item].to_xml_obj())
        xmlobj.append(ref_obj)

        pkg_obj = xmletree.Element('pkglist')
        for pkg_coll in self.pkgcolllist.keys():
            pkg_obj.append(self.pkgcolllist[pkg_coll].to_xml_obj())

        xmlobj.append(pkg_obj)

        return xmlobj

    def from_xml_obj(self, xmlobj):
        '''
            Pass in the xml object from a previous run and it will set the
             values in this object for you.

            Comment elements will return 'False' so don't try and add them
             in ok?  Anything else returns 'True'

            Comments cannot be preserved, it gets too messy... way too messy
        '''

        # lxml comment lines are of this type
        if xmletree.__package__ == 'lxml':
            if isinstance(xmlobj, lxml.etree._Comment):
                return False

        # it seems xml.etree.ElementTree doesn't
        #  do anything with the comment lines, so
        #  I don't need to hunt for them here

        if xmlobj.attrib.has_key('status'):
            self.status = xmlobj.attrib['status']
        if xmlobj.attrib.has_key('from'):
            self.updatefrom = xmlobj.attrib['from']
        if xmlobj.attrib.has_key('type'):
            self.updatetype = xmlobj.attrib['type']

        for subtree in xmlobj.getchildren():
            if subtree.tag == 'id':
                self.updateid = subtree.text
            elif subtree.tag == 'title':
                self.title = subtree.text
            elif subtree.tag == 'severity':
                self.severity = subtree.text
            elif subtree.tag == 'issued':
                self.issued_date = subtree.attrib['date']
            elif subtree.tag == 'updated':
                self.update_date = subtree.attrib['date']
            elif subtree.tag == 'description':
                self.description = subtree.text
            elif subtree.tag == 'release':
                self.release_name = subtree.text
            elif subtree.tag == 'summary':
                self.summary = subtree.text
            elif subtree.tag == 'solution':
                self.solution = subtree.text
            elif subtree.tag == 'rights':
                self.rights = subtree.text
            elif subtree.tag == 'reboot_suggested':
                self.reboot_suggested = True
            elif subtree.tag == 'restart_suggested':
                self.restart_suggested = True
            elif subtree.tag == 'relogin_suggested':
                self.relogin_suggested = True
            elif subtree.tag == 'pkglist':
                for collection in subtree.getchildren():
                    collection_obj = Collection()
                    if collection_obj.from_xml_obj(collection):
                        self.add_collection_obj(collection_obj)
            elif subtree.tag == 'references':
                for ref in subtree.getchildren():
                    ref_entry = Reference()
                    if ref_entry.from_xml_obj(ref):
                        self.add_reference_obj(ref_entry)

        return True
