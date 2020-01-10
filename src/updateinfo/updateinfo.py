'''
    This is the Updateinfo class
     you will want to add entries to it
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

# not all in use, but makes other imports cleaner
from entry import Entry
from collection import Collection
from package import Package
from reference import Reference

class Updateinfo:
    '''
        This class will accept as many UpdateInfo.Entry objects
        as you wish to add.

        When you try and print it, it will print out the updateinfo.xml
        of the objects you've added

        You can treat it somewhat like a dict, but not completely
    '''
    def __init__(self):
        '''
           This takes no arguments.
           It sets up a container for later and notes the XSD

            Relevant metainfo vars:
             None
        '''
        self.__entries = { }
        self.__xsdfile = '/usr/share/doc/python-Updateinfo/updateinfo.xsd'

        self.__updatefrom = None
        self.__status = None
        self.__release_name = None
        self.__collection_name = None
        self.__collection_short_name = None

    def __str__(self):
        '''
            Basically this is just a wrapper around get_xml
            It pretty prints the output, if you want it otherwise
            I suggest get_xml
        '''
        return self.get_xml(validate=False, pretty=True)

    def __iter__(self):
        '''
            Used for: looping
        '''
        return iter(self.__entries)

    def __getitem__(self, key):
        '''
           Used for: accessing items like a dict
        '''
        return self.__entries[key]

    def __setitem__(self, key, value):
        '''
           Used for: setting items like a dict
        '''
        if key != value.updateid:
            raise KeyError('key does not match id')
        self.add_entry(value)

    def __delitem__(self, key):
        '''
           Used for: removing items like a dict
        '''
        self.del_entry(key)

    def __contains__(self, key):
        '''
            Used for: x in obj
        '''
        return self.has_key(key)

    def has_key(self, key):
        '''
           Used for: checking for values like a dict
        '''
        return self.has_entry(key)

    def keys(self):
        '''
           Used for: listing all entry ids like a dict
        '''
        return self.__entries.keys()

    def force_updatefrom(self, updatefrom):
        '''
            All updates will have the following value as their
            <update from=xxxxx>  value
        '''
        self.__updatefrom = updatefrom
        for entry in self.__entries.keys():
            self.__entries[entry].set_from(self.__updatefrom)

    def force_status(self, status):
        '''
            All updates will have the following value as their
            <update status=xxxx> value
        '''
        self.__status = status
        for entry in self.__entries.keys():
            self.__entries[entry].set_status(self.__status)

    def force_release_name(self, release_name):
        '''
            All updates will have the following value as their
            '<update><release>xxxx</release>' value
        '''
        self.__release_name = release_name
        for entry in self.__entries.keys():
            self.__entries[entry].set_release_name(self.__release_name)

    def force_collection_name(self, collection_name, short_name=None):
        '''
            All updates will have the following value as their
            '<update><collection><name>xxxx</name></collection>' value

            You can also set the 'short' name from here too
        '''
        self.__collection_name = collection_name
        self.__collection_short_name = short_name
        for entry in self.__entries.keys():
            self.__entries[entry].force_collection_name(self.__collection_name,
                                                  self.__collection_short_name)

    def set_xsd(self, new_xsd):
        '''
            If your xsd file is not at the default location
            you can set another one here.
        '''
        self.__xsdfile = new_xsd

    def has_ref_url(self, refurl):
        '''
            You can check and see if a given reference url is within
            this xml already.  Useful for de-duplication based on the
            'self' reference type.
        '''
        for entry in self.__entries.keys():
            if self.__entries[entry].has_reference(refurl):
                return True
        return False

    def has_filename(self, filename, collection=None):
        '''
            Useful for seeing if a given filename is within this xml file
            you can narrow the scope to a particular collection if you wish.
        '''
        for entry in self.__entries.keys():
            if self.__entries[entry].has_filename(filename, collection):
                return True
        return False

    def has_entry(self, entryid):
        '''
           Check and see if a given update id is listed already.
        '''
        return self.__entries.has_key(entryid)

    def del_entry(self, entryid):
        '''
           Remove an entry by its update id.
        '''
        del self.__entries[entryid]

    def add_entry(self, entry, allow_id_merge=False):
        '''
            Add an object of updateinfo.Entry type to the file.

            If you pass in the wrong sort of thing, expect TypeError

            If you've missed some required attributes, expect ValueError

            If you already have this entry loaded you can expect a
             ValueError unless you set allow_id_merge=True
             In that case it will attempt to merge in attributes from
             the new entry not present in the existing entry.
        '''
        if isinstance(entry, Entry):

            if entry.updateid == None:
                print entry
                raise ValueError('no entry id specified, cannot be added')

            if self.has_entry(entry.updateid):
                if not allow_id_merge:
                    raise ValueError('Already added ' + entry.updateid +
                                     " can't do it again")
                else:
                    if self.__collection_name != None:
                        raise RuntimeError("Can't force collection and merge")
                    if self.__collection_short_name != None:
                        raise RuntimeError("Can't force collection and merge")
                    self.__entries[entry.updateid].merge(entry)
            else:

                # if we are forcing 'from' do it
                if self.__updatefrom != None:
                    entry.set_from(self.__updatefrom)

                # if we are forcing 'status' do it
                if self.__status != None:
                    entry.set_status(self.__status)

                # if we are forcing 'release_name' do it
                if self.__release_name != None:
                    entry.set_release_name(self.__release_name)

                # if we are forcing 'collection_name' do it
                if self.__collection_name != None:
                    entry.force_collection_name(self.__collection_name,
                                            self.__collection_short_name)

                self.__entries[entry.updateid] = entry
        else:
            raise TypeError("Should be of type 'updateinfo.Entry'")

    def merge_with_file(self, xml_file):
        '''
            If you've got another updateinfo file you want to merge with
             this one, just specify it here
        '''
        tree = xmletree.parse(xml_file)
        self.merge_with_xmlobj(tree.getroot())

    def merge_with_xmlobj(self, xmlobj):
        '''
            If you've got another updateinfo object you want to merge with
             this one, just specify it here
        '''
        for someentry in xmlobj.getchildren():
            entry = Entry()
            # if I can make an object from this entry
            if entry.from_xml_obj(someentry):
                self.add_entry(entry, allow_id_merge=True)

    def validate_xml_file(self, xml_file):
        '''
            If using lxml, we can validate against the xsd right now
            so lets try it and see how that goes.

            This only works with lxml, so skip out early otherwise.
            If you are worried catch 'DocumentInvalid'
        '''
        if xmletree.__package__ != 'lxml':
            return NotImplemented

        xml_file = open(xml_file, 'r')
        xml_string = xml_file.read()
        xml_file.close()
        self.validate_xml_text(xml_string)

    def validate_xml_text(self, xml_text):
        '''
            If using lxml, we can validate against the xsd right now
            so lets try it and see how that goes.

            This only works with lxml, so skip out early otherwise.
            If you are worried catch 'DocumentInvalid'
        '''
        if xmletree.__package__ != 'lxml':
            return NotImplemented

        from StringIO import StringIO

        xsd_parser = xmletree.XMLSchema(xmletree.parse(self.__xsdfile))
        xml_pseudo_file = StringIO(xml_text)

        my_xml = xmletree.parse(xml_pseudo_file)

        # raises DocumentInvalid if doesn't pass validation
        xsd_parser.assertValid(my_xml)

    def get_xml(self, header=True, comment=None, validate=True, pretty=False):
        '''
            returns the xml generated by this object
            If you are prettyprinting you will automatically get a header
        '''
        if header:
            xml_header = '<?xml version="1.0" encoding="UTF-8"?>\n'
        else:
            xml_header = ''

        if comment != None:
            comment = comment.replace('\\n', '\n')
            xml_header = xml_header + '\n\n<!-- \n' + comment + '\n-->\n\n'

        xml_string = xml_header + xmletree.tostring(self.to_xml_obj(),
                                                    encoding='UTF-8')
        if validate:
            self.validate_xml_text(xml_string)

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
        my_xml = xmletree.Element('updates')
        entry_ids = self.__entries.keys()
        entry_ids.sort()
        for entry in entry_ids:
            entry_xml_obj = self.__entries[entry].to_xml_obj()
            my_xml.append(entry_xml_obj)
        return my_xml

    def to_xml_file(self, filename, validate=True, comment=None, pretty=False):
        '''
            Writes the updateinfo.xml file to 'filename'
        '''
        thisfile = open(filename, 'w')
        thisfile.write(self.get_xml(validate=False,
                                     comment=comment,
                                      pretty=pretty) )
        thisfile.close()

        if validate:
            # validate once it is written
            xml_file = open(filename, 'r')
            xml_string = xml_file.read()
            xml_file.close()
            self.validate_xml_text(xml_string)

    def from_xml_obj(self, xmlobj):
        '''
            Pass in the xml object from a previous run and it will set the
            values in this object for you.

            Note: any xml comments are removed automatically
        '''
        if xmlobj.tag != 'updates':
            raise ValueError("Doesn't look like our xml records")

        for entry in xmlobj.getchildren():
            found_entry = Entry()
            if found_entry.from_xml_obj(entry):
                self.add_entry(found_entry)

    def from_xml_string(self, xmlstring):
        '''
           Pass in an xml string and it will parse it for you

            Note: any xml comments are removed automatically
        '''
        my_xml = xmletree.fromstring(xmlstring)
        self.from_xml_obj(my_xml)

    def from_xml_file(self, xmlfile):
        '''
            Pass in the xml file from a previous run and it will set the
            values in this object for you.

            Note: any xml comments are removed automatically
        '''
        # if it is a remote updateinfo.xml we download the text and pass the
        # string along
        if xmlfile.startswith('http://') or xmlfile.startswith('ftp://'):
            import urllib2
            updateinfo_xml = urllib2.urlopen(xmlfile)
            if xmlfile.endswith('.gz'):
                import gzip
                raw_xml = gzip.GzipFile(fileobj=updateinfo_xml)
                self.from_xml_string(raw_xml.read())
            else:
                self.from_xml_string(updateinfo_xml.read())
        else:
            if xmlfile.endswith('.gz'):
                import gzip
                raw_xml = gzip.GzipFile(filename=xmlfile)
                self.from_xml_string(raw_xml.read())
            else:
                tree = xmletree.parse(xmlfile)
                self.from_xml_obj(tree.getroot())

    def from_repo(self, repobase, meta_attrib=False):
        '''
            Pass in the path to a repo and it will load the updateinfo.xml
            for you.  Makes an empty object if there isn't one

            If you set meta_attrib=True it will import additional metadata
            from the repository and configure your environment.

            You will need to add that metadata to the repository yourself.
            The easiest way is with 'createrepo'
            createrepo --distro can be used to set a string suitable for
             'release_name' and 'collection_name'
            createrepo --content can be used to set a string suitable for
             'status'

            Be careful with meta_attrib=True and be sure you like how it works
             before making it live

            Note: any xml comments are removed automatically
        '''
        if repobase.startswith('http://') or repobase.startswith('https://'):
            import urllib2
            repomd_xml = urllib2.urlopen(repobase + '/repodata/repomd.xml')

        elif repobase.startswith('ftp://'):
            import urllib2
            repomd_xml = urllib2.urlopen(repobase + '/repodata/repomd.xml')

        else:
            repomd_xml = open(repobase + '/repodata/repomd.xml', 'r')

        repomd = xmletree.fromstring(repomd_xml.read())

        xsd_ns = '{http://linux.duke.edu/metadata/repo}'
        myfile = None
        for repometadata in repomd.getchildren():
            if repometadata.attrib.has_key('type'):
                if repometadata.attrib['type'] == 'updateinfo':
                    for inform in repometadata.getchildren():
                        if inform.tag == xsd_ns + 'location':
                            myfile = repobase + '/' + inform.attrib['href']
                            self.from_xml_file(myfile)
            if meta_attrib == True:
                if repometadata.tag == xsd_ns + 'tags':
                    for mytag in repometadata.getchildren():
                        if mytag.tag == xsd_ns + 'content':
                            self.force_status(mytag.text)
                        if mytag.tag == xsd_ns + 'distro':
                            self.force_release_name(mytag.text)
                            self.force_collection_name(mytag.text)
        return myfile

    def just_append_to_existing(self, existing_file, pretty=False):
        '''
            Don't read in this file, don't validate it, don't optimize the xml
            just add whatever we've got to the xml.

            If you want to validate later you can always use validate_xml_file
        '''
        thisfile = open(existing_file, 'r')
        existing = thisfile.read()
        thisfile.close()

        my_text = self.get_xml(header=False, pretty=pretty, validate=False)

        my_text = my_text.replace('<updates>','\n')

        new_text = existing.replace('</updates>', my_text)

        thisfile = open(existing_file, 'w')
        thisfile.write(new_text)
        thisfile.close()
