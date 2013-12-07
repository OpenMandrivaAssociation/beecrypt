%bcond_without	python
%bcond_without	cplusplus
%ifnarch %{mips} %{arm}
%bcond_without	java
%else
%bcond_with	java
%endif

%define major	7
%define libname %mklibname %{name} %{major}
%define libname_cxx %mklibname %{name}_cxx %{major}
%define libname_java %mklibname %{name}_java %{major}
%define devname %mklibname %{name} -d

Summary:	An open source cryptography library
Name:		beecrypt
Version:	4.2.1
Release:	18
Group:		System/Libraries
License:	LGPLv2+
Url:		http://beecrypt.sourceforge.net/
Source0:	http://prdownloads.sourceforge.net/beecrypt/%{name}-%{version}.tar.gz
Patch0:		beecrypt-4.1.2-biarch.patch
# AdamW: ugly patch simply defines upstream's odd libaltdir variable to be 
# equal to libdir in one places. Also replaces a similarly weird pythondir
# variable with hardcoded $(libdir)/python2.5 , so will stop working when
# python goes to 2.6. I expect upstream to have a better fix for this issue
# by then, so it won't matter. The problem is that beecrypt tries to set this
# libaltdir variable to /usr/lib or /usr/lib64 depending on the arch in use
# which it tests by grepping the default CFLAGS for --march=x86_64 . Ours
# don't include this, so the test breaks. Upstream should simply be using
# standard libdir variable. (This is mostly fixed now (2008/02), only two
# instances left).
Patch1:		beecrypt-4.2.0-lib64.patch
Patch2:		beecrypt-4.2.0-link.patch
Patch3:		beecrypt-4.2.1-py_platsitedir.diff
Patch4:		beecrypt-4.2.1-gcc4.7.patch
Patch5:		beecrypt-aarch64.patch

BuildRequires:	doxygen
BuildRequires:	graphviz
BuildRequires:	m4
BuildRequires:	tetex-dvips
BuildRequires:	tetex-latex
BuildRequires:	texlive-doublestroke
BuildRequires:	gomp-devel
%if %{with python}
BuildRequires:	pkgconfig(python)
%endif
%if %{with cplusplus}
BuildRequires:	pkgconfig(icu-uc)
%endif
%if %{with java}
BuildRequires:	java-rpmbuild
%endif
BuildConflicts:	libreoffice-core

%description
Beecrypt is a general-purpose cryptography library.

%package -n	%{libname}
Summary:	An open source cryptography library
Group:		System/Libraries

%description -n %{libname}
Beecrypt is a general-purpose cryptography library.

%package -n	%{devname}
Summary:	Files needed for developing applications with beecrypt
Group:		Development/C
%if %{with cplusplus}
Requires:	%{libname_cxx} = %{EVRD}
%endif
%if %{with java}
Requires:	%{libname_java} = %{EVRD}
%endif
Requires:	%{libname} = %{EVRD}
Provides:	%{name}-devel = %{EVRD}

%description -n	%{devname}
Beecrypt is a general-purpose cryptography library.  This package contains
files needed for developing applications with beecrypt.

%if %{with python}
%package -n	python-%{name}
Summary:	Files needed for python applications using beecrypt
Group:		Development/C
%rename		%{name}-python

%description -n	python-%{name}
Beecrypt is a general-purpose cryptography library.  This package contains
files needed for using python with beecrypt.
%endif

%if %{with cplusplus}
%package -n	%{libname_cxx}
Summary:	Files needed for C++ applications using beecrypt
Group:		Development/C++

%description -n	%{libname_cxx}
Beecrypt is a general-purpose cryptography library.  This package contains
files needed for using C++ with beecrypt.
%endif

%if %{with java}
%package -n	%{libname_java}
Summary:	Files needed for java applications using beecrypt
Group:		Development/C

%description -n	%{libname_java}
Beecrypt is a general-purpose cryptography library.  This package contains
files needed for using java with beecrypt.
%endif

%prep
%setup -q
%patch0 -p1 -b .biarch
%patch1 -p0 -b .lib64
%patch2 -p1 -b .link
%patch3 -p0
%patch4 -p1
%patch5 -p1

./autogen.sh

%build
%configure2_5x \
	--enable-shared \
	--enable-static \
%if %{with python}
	--with-python=%{_bindir}/python \
%endif
%if %{with cplusplus}
	--with-cplusplus \
%endif
%if %{with java}
	--with-java
%endif

%make
pushd include/beecrypt
doxygen
cd c++
doxygen
popd

# XXX delete next line to build with legacy, non-check aware, rpmbuild.
%check
make check || :
cat /proc/cpuinfo
make bench || :

%install
%makeinstall_std
mkdir %{buildroot}/%{_lib}
mv %{buildroot}%{_libdir}/libbeecrypt.so.%{major}* %{buildroot}/%{_lib}
ln -srf %{buildroot}/%{_lib}/libbeecrypt.so.%{major}.*.* %{buildroot}%{_libdir}/libbeecrypt.so

# XXX nuke unpackaged files, artifacts from using libtool to produce module
rm -f %{buildroot}%{py_platsitedir}/_bc.*a

%files -n %{libname}
%doc README BENCHMARKS
/%{_lib}/libbeecrypt.so.%{major}*

%files -n %{devname}
%doc BUGS docs/html docs/latex
%{_includedir}/%{name}
%if %{with cplusplus}
%{_libdir}/%{name}/base.so
%{_libdir}/%{name}/*.a
%endif
%{_libdir}/*.a
%{_libdir}/*.so

%if %{with python}
%files -n python-%{name}
%{py_platsitedir}/_bc.so
%endif

%if %{with cplusplus}
%files -n %{libname_cxx}
%config %{_sysconfdir}/beecrypt.conf
%dir %{_libdir}/%{name}
%{_libdir}/%{name}/base.so.*
%{_libdir}/libbeecrypt_cxx.so.%{major}*
%endif

%if %{with java}
%files -n %{libname_java}
%{_libdir}/libbeecrypt_java.so.%{major}*
%endif

%changelog
* Sat Apr 07 2012 Bernhard Rosenkraenzer <bero@bero.eu> 4.2.1-9
+ Revision: 789768
- Rebuild for icu 49.1

* Tue Dec 20 2011 Per Øyvind Karlsen <peroyvind@mandriva.org> 4.2.1-8
+ Revision: 743977
- '%%ifnarch %%mips %%java' should more likely be '%%ifnarch %%mips %%arm'
- drop unnecessary setting of CPPFLAGS & OPENMP_FLAGS
- add 'texlive-doublestroke' to buildrequires
- use %%{EVRD} macro
- ditch 'lib%%{name}-devel' provides
- s/libgomp-devel/gomp-devel/
- remove some deprecated rpm stuff
- add back *.la files, it's still required as the package has no pkgconfig file
- use %%bcond and do some cleaning..
- do autogen.sh in %%prep
- drop ugly cvs conditonal stuff..
- ditch *.la files

* Sun Jun 05 2011 Funda Wang <fwang@mandriva.org> 4.2.1-7
+ Revision: 682823
- rebuild for new icu

* Tue May 03 2011 Oden Eriksson <oeriksson@mandriva.com> 4.2.1-6
+ Revision: 663319
- mass rebuild

* Mon Mar 14 2011 Funda Wang <fwang@mandriva.org> 4.2.1-5
+ Revision: 644529
- rebuild for new icu
- rebuild for new icu

  + Per Øyvind Karlsen <peroyvind@mandriva.org>
    - get rid of scriptlets for ancient releases

* Thu Nov 04 2010 Götz Waschk <waschk@mandriva.org> 4.2.1-4mdv2011.0
+ Revision: 593333
- fix patch for python 2.7

* Sun Mar 21 2010 Funda Wang <fwang@mandriva.org> 4.2.1-4mdv2010.1
+ Revision: 526044
- rebuild for new icu

* Tue Mar 16 2010 Oden Eriksson <oeriksson@mandriva.com> 4.2.1-3mdv2010.1
+ Revision: 521389
- fix python stuff
- fix build
- rebuilt for 2010.1

* Fri Sep 25 2009 Olivier Blin <blino@mandriva.org> 4.2.1-2mdv2010.0
+ Revision: 448804
- disable java on mips & arm (from Arnaud Patard)

* Sun Jul 12 2009 Frederik Himpe <fhimpe@mandriva.org> 4.2.1-1mdv2010.0
+ Revision: 395313
- Fix Java BuildRequires
- Add libgomp BuildRequires
- Update to new version 4.2.1
- Add patch to fix unresolved libgomp symbols

* Thu Feb 05 2009 Tomasz Pawel Gajc <tpg@mandriva.org> 4.2.0-0.20090205.1mdv2009.1
+ Revision: 337901
- update to new snapshot 20090205
- patch 2 was merged upstream

* Sat Dec 27 2008 Funda Wang <fwang@mandriva.org> 4.2.0-0.20080216.3mdv2009.1
+ Revision: 319837
- rebuild for new python

* Tue Jul 29 2008 Oden Eriksson <oeriksson@mandriva.com> 4.2.0-0.20080216.2mdv2009.0
+ Revision: 253481
- fix silly summary-ended-with-dot
- fix release...
- fix spec file errors
- fix packaging after peeking a bit at arklinux, but with a twist

* Mon Jun 16 2008 Thierry Vignaud <tv@mandriva.org> 4.2.0-0.20080216.1mdv2009.0
+ Revision: 220480
- rebuild

  + Pixel <pixel@mandriva.com>
    - do not call ldconfig in %%post/%%postun, it is now handled by filetriggers

* Sat Feb 16 2008 Adam Williamson <awilliamson@mandriva.org> 4.2.0-0.20080216.1mdv2008.1
+ Revision: 169321
- specify location of python in --with-python parameter, configure test seems to be broken somehow
- use system %%pyver macro
- add typo.patch that fixes build when C++ stuff is built (not in our default build but might affect people doing rebuilds)
- rediff lib64.patch
- minor cleanups
- new devel policy
- new snapshot
- build all docs

  + Thierry Vignaud <tv@mandriva.org>
    - rebuild
    - kill re-definition of %%buildroot on Pixel's request

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

  + Pixel <pixel@mandriva.com>
    - add explicit conflict on libbeecrypt6-devel

* Wed Apr 25 2007 Adam Williamson <awilliamson@mandriva.org> 4.2.0-0.20070425.1mdv2008.0
+ Revision: 18192
- reorder patches, add new patch1 to fix x86-64 build
- enable tests
- major has gone up to 7 upstream
- use CVS to see if it builds right on x86-64
- sync spec and patches with Fedora
- buildrequires graphviz for doc generation
- 4.1.2


* Fri May 12 2006 Stefan van der Eijk <stefan@eijk.nu> 3.1.0-7mdk
- rebuild for sparc

* Sat Dec 31 2005 Mandriva Linux Team <http://www.mandrivaexpert.com/> 3.1.0-6mdk
- Rebuild

* Mon Jan 31 2005 Frederic Lepied <flepied@mandrakesoft.com> 3.1.0-5mdk
-

* Sat Dec 25 2004 Per Øyvind Karlsen <peroyvind@linux-mandrake.com> 3.1.0-4mdk
- fix build with current python
- fix group
- cosmetics

* Sun Jun 20 2004 Stefan van der Eijk <stefan@mandrake.org> 3.1.0-3mdk
- patch2: alpha doesn't use lib64

* Wed Feb 18 2004 Gwenole Beauchesne <gbeauchesne@mandrakesoft.com> 3.1.0-2mdk
- automake1.7

* Fri Jan 16 2004 Frederic Lepied <flepied@mandrakesoft.com> 3.1.0-1mdk
- initial Mandrake Linux packaging

* Mon Dec 22 2003 Jeff Johnson <jbj@jbj.org> 3.1.0-1
- upgrade to 3.1.0.
- recompile against python-2.3.3.

* Mon Jun 30 2003 Jeff Johnson <jbj@redhat.com> 3.0.1-0.20030630
- upstream fixes for DSA and ppc64.

* Mon Jun 23 2003 Jeff Johnson <jbj@redhat.com> 3.0.0-2
- upgrade to 3.0.0 final.
- fix for DSA (actually, modulo inverse) sometimes failing.

* Fri Jun 20 2003 Jeff Johnson <jbj@redhat.com> 3.0.0-1.20030619
- avoid asm borkage on ppc64.

* Thu Jun 19 2003 Jeff Johnson <jbj@redhat.com> 3.0.0-1.20030618
- rebuild for release bump.

* Tue Jun 17 2003 Jeff Johnson <jbj@redhat.com> 3.0.0-1.20030616
- try to out smart libtool a different way.
- use $bc_target_cpu, not $bc_target_arch, to detect /usr/lib64.

* Mon Jun 16 2003 Jeff Johnson <jbj@redhat.com> 3.0.0-1.20030615
- use -mcpu=powerpc64 on ppc64.

* Fri Jun 13 2003 Jeff Johnson <jbj@redhat.com> 3.0.0-1.20030613
- upgrade to latest snapshot.

* Fri Jun 06 2003 Jeff Johnson <jbj@redhat.com> 3.0.0-1.20030605
- rebuild into another tree.

* Wed Jun 04 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue Jun 03 2003 Jeff Johnson <jbj@redhat.com> 3.0.0-0.20030603
- update to 3.0.0 snapshot, fix mpmod (and DSA) on 64b platforms.

* Mon Jun 02 2003 Jeff Johnson <jbj@redhat.com> 3.0.0-0.20030602
- update to 3.0.0 snapshot, merge patches, fix gcd rshift and ppc problems.

* Thu May 29 2003 Jeff Johnson <jbj@redhat.com> 3.0.0-0.20030529
- update to 3.0.0 snapshot, fix ia64/x86_64 build problems.

* Wed May 28 2003 Jeff Johnson <jbj@redhat.com> 3.0.0-0.20030528
- upgrade to 3.0.0 snapshot, adding rpm specific base64.[ch] changes.
- add PYTHONPATH=.. so that "make check" can test the just built _bc.so module.
- grab cpuinfo and run "make bench".
- continue ignoring "make check" failures, LD_LIBRARY_PATH needed for _bc.so.
- skip asm build failure on ia64 for now.
- ignore "make bench" exit codes too, x86_64 has AES segfault.

* Wed May 21 2003 Jeff Johnson <jbj@redhat.com> 3.0.0-0.20030521
- upgrade to 3.0.0 snapshot, including python subpackage.
- ignore "make check" failure for now.

* Fri May 16 2003 Jeff Johnson <jbj@redhat.com> 3.0.0-0.20030516
- upgrade to 3.0.0 snapshot, including ia64 and x86_64 fixes.
- add %%check.
- ignore "make check" failure on ia64 for now.

* Mon May 12 2003 Jeff Johnson <jbj@redhat.com> 3.0.0-0.20030512
- upgrade to 3.0.0 snapshot.
- add doxygen doco.
- use /dev/urandom as default entropy source.
- avoid known broken compilation for now.

