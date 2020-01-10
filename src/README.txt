===========
UpdateInfo
===========

UpdateInfo provides useful objects for creating the updateinfo.xml
for use with yum

This isn't really fancy, but I've included the xsd this validates against.
The xsd should also validate against Fedora or Suse

The resulting xml file should be added to the yum repo metadata.

    modifyrepo updateinfo.xml /path/to/repodata/

I've included an example program that should help get you started.

There are a lot of options and ways of using these objects, so make sure
to read the help that comes with each module.

There is also a helper object you can use which will allow you to very
simply build and update your updateinfo.xml if you wish.  Odds are you will
need to build your own helper object, but this one should at least get you
started with the basics.
