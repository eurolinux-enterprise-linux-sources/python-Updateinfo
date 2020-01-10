'''
    This simply makes the package object for adding.  You can set all
    sorts of things if you want/need to do so.
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

import datetime
import os
import rpm

# we work with either, but better with lxml
try:
    import lxml
    from lxml import etree as xmletree
except ImportError:
    import xml.etree.ElementTree as xmletree

class Package:
    '''
        This object is very simple in its needs.

        You simply give it an rpm and the base for its source url
             or the xml from a previous run.
        It will do the rest.

        Or, if you already have the info you want, you can add it in by hand.

        If setting by hand you must run:
         set_name()
         set_version()
         set_release()
         set_arch()
         set_srpm()
         set_filename()
         set_set_src_url_base()

         You can set, reboot, restart, and relogin per package
          but don't go nuts, it will just make your xml bigger for no reason.

         You can also add checksums, md5, sha1, sha256, sha512 add what you
          need but don't go nuts, it will just make your xml bigger for reason.

            Relevant metainfo vars:
             self.name
             self.epoch
             self.version
             self.release
             self.arch
             self.srpm
             self.builddate
             self.filename
             self.src_url_base
             self.sum
             self.reboot_suggested
             self.restart_suggested
             self.relogin_suggested
    '''
    def __init__(self, src_url_base=None, rpmfile=None):
        '''
            If you just pass in rpm and src_url_base you can be done right here
        '''
        self.name = None
        self.epoch = None
        self.version = None
        self.release = None
        self.arch = None
        self.srpm = None

        # not required, but if you want it....
        self.sum = [ ]

        # we don't need this one, but you can use it for issue date later maybe
        self.builddate = None

        self.filename = None
        self.src_url_base = None

        # seen this here too.....
        self.reboot_suggested = False
        self.restart_suggested = False
        self.relogin_suggested = False

        if rpmfile != None:
            self.set_from_file(rpmfile)

        if src_url_base != None:
            self.set_src_url_base(src_url_base)

    def __str__(self):
        '''
            Simple way of dumping the xml
        '''
        return self.return_xml(header=False, pretty=True)

    def set_from_file(self, thisfile):
        '''
            Open up the rpm file and pull the data we want out of it

            This sets builddate for you, you can query it later
            if you want to for setting other things.
        '''
        self.set_filename(thisfile)

        if thisfile.startswith('http://') or thisfile.startswith('https://'):
            import urllib2
            import tempfile
            rpm_file = urllib2.urlopen(thisfile)

            temp = tempfile.NamedTemporaryFile(bufsize=0)
            temp.write(rpm_file)
            _ts = rpm.TransactionSet()
            hdr = _ts.hdrFromFdno(temp)

            self.get_sum_from_file('sha256', temp.name)

            temp.close()

        elif thisfile.startswith('ftp://'):
            import urllib2
            import tempfile
            rpm_file = urllib2.urlopen(thisfile)

            temp = tempfile.NamedTemporaryFile(bufsize=0)
            temp.write(rpm_file)
            _ts = rpm.TransactionSet()
            hdr = _ts.hdrFromFdno(temp)

            self.get_sum_from_file('sha256', temp.name)

            temp.close()

        else:
            _fd = open(thisfile, 'r')
            _ts = rpm.TransactionSet()
            hdr = _ts.hdrFromFdno(_fd)
            _fd.close()
            self.get_sum_from_file('sha256', thisfile)

        self.set_name(hdr[rpm.RPMTAG_NAME])
        self.set_epoch(hdr[rpm.RPMTAG_EPOCH])
        self.set_version(hdr[rpm.RPMTAG_VERSION])
        self.set_release(hdr[rpm.RPMTAG_RELEASE])
        self.set_arch(hdr[rpm.RPMTAG_ARCH])

        self.set_builddate(hdr[rpm.RPMTAG_BUILDTIME])

        if hdr[rpm.RPMTAG_SOURCERPM]:
            self.set_srpm(hdr[rpm.RPMTAG_SOURCERPM])
            self.set_arch(hdr[rpm.RPMTAG_ARCH])
        else:
            self.set_srpm(self.filename)
            self.set_arch('src')

        hdr.unload()

    def get_sum_from_file(self, sumtype, thisfile):
        '''
            This will get the checksum type you've asked for from a file
            and return a tuple of ('hash', 'sum').  The result is also
            automatically stored within the object.  So you don't need
            to call the set function as well.

            Supported sums are md5, sha1, sha256, sha512
        '''
        import hashlib

        if sumtype == 'md5':
            value = hashlib.md5(thisfile).hexdigest()
        elif sumtype == 'sha':
            value = hashlib.sha1(thisfile).hexdigest()
        elif sumtype == 'sha1':
            value = hashlib.sha1(thisfile).hexdigest()
        elif sumtype == 'sha256':
            value = hashlib.sha256(thisfile).hexdigest()
        elif sumtype == 'sha512':
            value = hashlib.sha512(thisfile).hexdigest()
        else:
            raise ValueError("Not a valid checksum type " + sum)

        self.set_sum(sumtype, value)

        return (sum, value)

    def set_name(self, name):
        '''
           Package name
        '''
        self.name = name

    def set_epoch(self, epoch):
        '''
           Package epoch
        '''
        self.epoch = str(epoch)

    def set_version(self, version):
        '''
           Package version
        '''
        self.version = str(version)

    def set_release(self, release):
        '''
           Package release
        '''
        self.release = str(release)

    def set_arch(self, arch):
        '''
           Package arch
        '''
        self.arch = arch

    def set_srpm(self, srpm):
        '''
           Package srpm
        '''
        self.srpm = srpm

    def set_builddate(self, builddate):
        '''
           Package build date, should be
              an int - unix time
              or a datetime object
        '''
        if isinstance(builddate, (int, long)):
            builddate = datetime.datetime.fromtimestamp(builddate)
            self.builddate = builddate
        elif isinstance(builddate, datetime.datetime):
            self.builddate = builddate
        else:
            raise TypeError("Wrong data type for builddate")

    def get_filename(self):
        '''
           return the filename of the package
        '''
        return self.filename

    def set_filename(self, filename):
        '''
           filename of the package
        '''
        self.filename = filename

    def set_sum(self, whichsum, checksum):
        '''
           Package checksum, need the kind of checksum and its value
        '''
        self.sum.append((whichsum, checksum))

    def set_src_url_base(self, src_url_base):
        '''
            What is the base url for the src.rpm?
            May throw ValueError if you've got some bad data... heads up
        '''
        if src_url_base == None or src_url_base == '':
            return None

        if not src_url_base.startswith('http://'):
            if not src_url_base.startswith('ftp://'):
                raise ValueError("src_url_base doesn't look like a url")

        # ending slash makes things simpler later
        if not src_url_base.endswith('/'):
            src_url_base = src_url_base + '/'

        self.src_url_base = src_url_base

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
            Make sure we've got enough data on the rpm
            Nothing calls this, but this function should help you
             see what you need.  It may be out of sync with the xsd so beware.
        '''
        # epoch and srpm not required
        if self.filename == None or self.name == None or self.version == None:
            return False
        if self.release == None or self.arch == None:
            return False
        return True

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
        xmlobj = xmletree.Element('package')
        if self.epoch == None:
            xmlobj.attrib['epoch'] = str(0)
        elif self.epoch == str(None):
            xmlobj.attrib['epoch'] = str(0)
        else:
            xmlobj.attrib['epoch'] = self.epoch

        if self.name != None:
            xmlobj.attrib['name'] = self.name

        if self.version != None:
            xmlobj.attrib['version'] = self.version

        if self.release != None:
            xmlobj.attrib['release'] = self.release

        if self.arch != None:
            xmlobj.attrib['arch'] = self.arch

        if self.src_url_base != None and self.srpm != None:
            xmlobj.attrib['src'] = self.src_url_base + self.srpm
        elif self.srpm != None:
            xmlobj.attrib['src'] = self.srpm

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

        package_obj = xmletree.Element('filename')
        package_obj.text = self.filename
        xmlobj.append(package_obj)

        if self.sum:
            for checksum in self.sum:
                checksum_obj = xmletree.Element('sum')
                checksum_obj.attrib['type'] = checksum[0]
                checksum_obj.text = checksum[1]
                xmlobj.append(checksum_obj)

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

        if 'epoch' in xmlobj.keys():
            self.epoch = xmlobj.attrib['epoch']
        if 'name' in xmlobj.keys():
            self.name = xmlobj.attrib['name']
        if 'version' in xmlobj.keys():
            self.version = xmlobj.attrib['version']
        if 'release' in xmlobj.keys():
            self.release = xmlobj.attrib['release']
        if 'arch' in xmlobj.keys():
            self.arch = xmlobj.attrib['arch']
        if 'src' in xmlobj.keys():
            self.srpm = xmlobj.attrib['src']
            self.src_url_base = os.path.dirname(self.srpm)
            self.srpm = os.path.basename(self.srpm)

        for subtree in xmlobj.getchildren():
            if subtree.tag == 'filename':
                self.filename = subtree.text
            elif subtree.tag == 'sum':
                self.set_sum(subtree.attrib['type'], subtree.text)
            elif subtree.tag == 'reboot_suggested':
                self.reboot_suggested = True
            elif subtree.tag == 'restart_suggested':
                self.restart_suggested = True
            elif subtree.tag == 'relogin_suggested':
                self.relogin_suggested = True

        return True
