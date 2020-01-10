'''
    Each update may have various collections of packages.

    For example, SL5 and SL6 might both need an update for nss,
     but the packages for SL5 are not at all alike.
     So you need one collection for SL5 and another for SL6.
     The SL5 packages might require a restart of services
     while the SL6 ones might require you to relogin.
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

from package import Package

class Collection:
    '''
        This object is very simple in its needs.

        You simply attach packages to this collection
             or the xml from a previous run.
        It will do the rest.

        I would encourage you to set the collection name and short name

         set_name()
         set_short_name()

        You will need add_package_obj()
    '''
    def __init__(self, release_name=None, short_name=None):
        '''
            If you just pass in name and short_name you can just add packages

            Relevant metainfo vars:
             self.release_name
             self.short_name
        '''
        self.release_name = None
        self.short_name = None

        self.pkglist = { }

        self.set_name(release_name)
        self.set_short_name(short_name)

    def __str__(self):
        '''
           Simple way of dumping the xml
        '''
        return self.return_xml(header=False, pretty=True)

    def __iter__(self):
        '''
            Used for: looping though packages
        '''
        return iter(self.pkglist)

    def __getitem__(self, key):
        '''
           Used for: treating the packages like a dict
        '''
        return self.pkglist[key]

    def __setitem__(self, key, value):
        '''
           Used for: treating the packages like a dict
        '''
        if key != value.get_filename():
            raise ValueError("Key isn't a recognized filename")
        self.add_package_obj(value)

    def __delitem__(self, key):
        '''
           Used for: treating the packages like a dict
        '''
        self.del_package(key)

    def __contains__(self, key):
        '''
            Used for: x in object
             this covers filenames
        '''
        return self.has_filename(key)

    def merge(self, new_collection):
        '''
            If you've somehow gotten this collection defined
             you can merge a second copy's attributes here if
             you want

            Any values already set will stay the same
             but anything new will be added in.
        '''
        if self.release_name == None:
            self.set_name(new_collection.release_name)
        if self.short_name == None:
            self.set_short_name(new_collection.short_name)

        for newpkg in new_collection.get_filenames():
            if not self.has_filename(newpkg):
                self.add_package_obj(new_collection[newpkg])

    def set_name(self, release_name):
        '''
           set collection name for the package
        '''
        if release_name == None:
            self.release_name = None
        elif isinstance(release_name, str):
            self.release_name = unicode(release_name, encoding='utf-8')
        elif isinstance(release_name, unicode):
            self.release_name = release_name
        else:
            raise TypeError("Can't set name to " + release_name +
                            " type " + type(release_name))

    def set_short_name(self, short_name):
        '''
           set collection short name for the package
        '''
        if short_name == None:
            self.short_name = None
        elif isinstance(short_name, str):
            self.short_name = unicode(short_name, encoding='utf-8')
        elif isinstance(short_name, unicode):
            self.short_name = short_name
        else:
            raise TypeError("Can't set short name to " + short_name +
                            " type " + type(short_name))

    def check_values(self):
        '''
            Make sure we've got enough data.

            Nothing calls this, but this function should help you
             see what you need.  It may be out of sync with the xsd so beware.
        '''
        if not self.pkglist:
            return False

        # you need one
        if self.release_name == None and self.short_name == None:
            return False

        return True

    def has_filename(self, filename):
        '''
            Useful for seeing if a given filename is within this collection
        '''
        if filename in self.get_filenames():
            return True
        return False

    def get_filenames(self):
        '''
            return a list of files in the collection
        '''
        return self.pkglist.keys()

    def add_package_obj(self, pkgobj):
        '''
            Should be an updateinfo.Package object
        '''
        if isinstance(pkgobj, Package):
            if pkgobj.get_filename() == None:
                raise ValueError("Package has no filename")
            else:
                self.pkglist[pkgobj.get_filename()] = pkgobj
        else:
            raise TypeError("Should be of type 'updateinfo.Package'")

    def del_package(self, thispackage):
        '''
            remove a package from this collection
        '''
        del self.pkglist[thispackage]

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
        xmlobj = xmletree.Element('collection')
        if self.short_name != None:
            xmlobj.attrib['short'] = self.short_name
        if self.release_name != None:
            pkg_release_name = xmletree.Element('name')
            pkg_release_name.text = self.release_name
            xmlobj.append(pkg_release_name)
        for pkg_item in self.pkglist.keys():
            xmlobj.append(self.pkglist[pkg_item].to_xml_obj())

        return xmlobj

    def from_xml_obj(self, xmlobj):
        '''
            Pass in the xml object from a previous run and it will set the
            values in this object for you.
        '''
        # lxml comment lines are of this type
        if xmletree.__package__ == 'lxml':
            if isinstance(xmlobj, lxml.etree._Comment):
                return False

        # it seems xml.etree.ElementTree doesn't
        #  do anything with the comment lines, so
        #  I don't need to hunt for them here

        if xmlobj.attrib.has_key('short'):
            self.set_short_name(xmlobj.attrib['short'])
        for child in xmlobj.getchildren():
            if child.tag == 'name':
                self.set_name(child.text)
            elif child.tag == 'package':
                update_package = Package()
                if update_package.from_xml_obj(child):
                    self.add_package_obj(update_package)

        return True
