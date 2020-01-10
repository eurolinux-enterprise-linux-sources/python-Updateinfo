Summary: Classes for making the yum updateinfo.xml.
Name: python-Updateinfo
Version: 0.1.5
Release: 3.sl6
Source0: python-Updateinfo.tar.gz
License: GPL
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Pat Riehecky <riehecky@fnal.gov>
Url: http://www.scientificlinux.org/
# creatrepo provides modifyrepo which is what we really need
Requires: python python-hashlib python-lxml PyXML createrepo

%description
UpdateInfo provides useful objects for creating the updateinfo.xml
for use with yum

This includes the xsd the xml should validate against to work correctly.
The xsd should also validate against EPEL, Fedora, and Suse

%prep
%setup -n %{name}

%build
python setup.py build

%install
python setup.py install -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES
mkdir -p $RPM_BUILD_ROOT/usr/share/doc/python-Updateinfo/
cp -pr docs/* $RPM_BUILD_ROOT/usr/share/doc/python-Updateinfo/

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)
%doc /usr/share/doc/python-Updateinfo/

%changelog
* Thu Nov 15 2012 Pat Riehecky <riehecky@fnal.gov> 0.1.5-3.sl6
- the example scripts can now be run with much more limited knowledge
- there are some sample updateinfo.xml files included for review
- a more feature rich example is provided
- 'prerelease' has been added to the updateinfo.xsd for package status
- the Package object can now review remote packages

* Thu Nov 15 2012 Pat Riehecky <riehecky@fnal.gov> 0.1.5-2.1.sl6
- Entry.set_update_date now responds correctly to values of 'None'

* Wed Nov 7 2012 Pat Riehecky <riehecky@fnal.gov> 0.1.5-2.sl6
- More documentation now avalible for how these objects interact
- You can now remove a reference from an entry
- the issued_date and update_date are now datetime objects

* Fri Nov 1 2012 Pat Riehecky <riehecky@fnal.gov> 0.1.5-1.sl6
- The Updateinfo class can now easily ask about reference urls for all
   loaded entries.

* Thu Oct 11 2012 Pat Riehecky <riehecky@fnal.gov> 0.1.5-0.sl6
- Added entry merge capibilities for merging entries with common
   data, such as an ID that applies to two different collections

* Wed Oct 3 2012 Pat Riehecky <riehecky@fnal.gov> 0.1.4-2.sl6
- Added more 'convenience' functions for asking about object status
- Comments are now handled correctly

* Fri Sep 28 2012 Pat Riehecky <riehecky@fnal.gov> 0.1.4-1.sl6
- misc bug fixes and typos
- You can now simply append to an unparsed updateinfo.xml if you want
- You can now skip the import of updateinfo.xml in updateinfohelper
- Requires are now more complete, I'm forcing lxml as it is much faster
   and has validate but this should continue to work in a pure python
   deployment if you just extract the source.

* Fri Sep 28 2012 Pat Riehecky <riehecky@fnal.gov> 0.1.4-0.sl6
- You can now do much more complex things with updateinfohelper.py
   such as track unused packages or have a distinction between TUV
   and non-TUV ids

* Fri Sep 21 2012 Pat Riehecky <riehecky@fnal.gov> 0.1.3-0.sl6
- Input can now be UTF-8
- updateinfohelper.py now has easy ways of dealing with unlisted
   packages.  You can return 'None' if you want to ignore them
   or 'raise' it is up to you.
- PrettyPrint now prints in a way that will actually still work
   with the validator functions
- another update to the xsd

* Wed Sep 19 2012 Pat Riehecky <riehecky@fnal.gov> 0.1.2-0.sl6
- misc bug fixes
- now includes a helper class for abstracting away some of the
   messy details.  See helper_example.py in %doc

* Mon Sep 17 2012 Pat Riehecky <riehecky@fnal.gov> 0.1.1-0.sl6
- now includes 'summary', 'solution', and 'rights' as valid for setting
- the xsd is now more fully documented
- the xml can now be pretty printed
- you can now force settings down the stack to make stuff consistant
- you can now load metadata from the repo itself to help with things
- some objects can be utilized like a dict now
- All xml output is now UTF-8

* Fri Sep 7 2012 Pat Riehecky <riehecky@fnal.gov> 0.1.0-2.sl6
- now uses lxml for performance and validation

* Fri Aug 31 2012 Pat Riehecky <riehecky@fnal.gov> 0.1.0-1.sl6
- xsd can now validate lots more in the wild (EPEL, OpenSUSE).
- the xsd is now actually installed into %doc along with the example script
- The import functions can now import all sorts of things

* Thu Aug 20 2012 Pat Riehecky <riehecky@fnal.gov> 0.0.1
- initial build
