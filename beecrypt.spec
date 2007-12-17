%define name beecrypt
%define version 4.2.0
%define cvs 20070425
%if %cvs
%define release %mkrel 0.%cvs.2
%else
%define release %mkrel 1
%endif
%define	with_python		--with-python
%{expand:%%define with_python_version %(python -V 2>&1| awk '{print $2}'|cut -d. -f1-2)}
%define libname %mklibname beecrypt 7
%define libnamedev %{libname}-devel

Summary:	An open source cryptography library
Name:		%{name}
Version:	%{version}
Release:	%{release}
Group:		System/Libraries
License:	LGPL
URL:		http://beecrypt.sourceforge.net/
%if %cvs
Source0:	%{name}-%{cvs}.tar.bz2
%else
Source0:	http://prdownloads.sourceforge.net/beecrypt/%{name}-%{version}.tar.bz2
%endif
Patch0:		beecrypt-4.1.2-biarch.patch
# AdamW: ugly patch simply defines upstream's odd libaltdir variable to be 
# equal to libdir in various places. Also replaces a similarly weird pythondir
# variable with hardcoded $(libdir)/python2.5 , so will stop working when
# python goes to 2.6. I expect upstream to have a better fix for this issue
# by then, so it won't matter. The problem is that beecrypt tries to set this
# libaltdir variable to /usr/lib or /usr/lib64 depending on the arch in use
# which it tests by grepping the default CFLAGS for --march=x86_64 . Ours
# don't include this, so the test breaks. Upstream should simply be using
# standard libdir variable.
Patch1:		beecrypt-4.2.0-lib64.patch
BuildRequires:	doxygen tetex-dvips tetex-latex graphviz
BuildRequires:	m4
%if %{?with_python:1}0
BuildRequires:	python-devel >= %{with_python_version}
%endif

%description
Beecrypt is a general-purpose cryptography library.

%package -n	%{libname}
Summary:	An open source cryptography library
Group:		System/Libraries

%description -n %{libname}
Beecrypt is a general-purpose cryptography library.

%package -n	%{libnamedev}
Summary:	Files needed for developing applications with beecrypt
Group:		Development/C
Requires:	%{libname} = %{version}
Provides:	lib%{name}-devel = %{version}-%{release}
Conflicts:	%{mklibname beecrypt 6}-devel

%description -n	%{libnamedev}
Beecrypt is a general-purpose cryptography library.  This package contains
files needed for developing applications with beecrypt.

%if %{?with_python:1}0
%package	python
Summary:	Files needed for python applications using beecrypt
Group:		Development/C
Requires:	python >= %{with_python_version}
Requires:	%{libname} = %{version}

%description	python
Beecrypt is a general-purpose cryptography library.  This package contains
files needed for using python with beecrypt.
%endif

%prep
%if %cvs
%setup -q -n %name
%else
%setup -q
%endif
%patch0 -p1 -b .biarch
%patch1 -p0 -b .lib64

%build
%if %cvs
./autogen.sh
%endif

%configure	--enable-shared \
		--enable-static \
		%{?with_python} \
		CPPFLAGS="-I%{_includedir}/python%{with_python_version}"

%make
cd include/beecrypt
doxygen
cd c++
doxygen
cd ../../..

# XXX delete next line to build with legacy, non-check aware, rpmbuild.
%check
make check || :
cat /proc/cpuinfo
make bench || :

%install
rm -fr $RPM_BUILD_ROOT
%{makeinstall_std}

# XXX nuke unpackaged files, artifacts from using libtool to produce module
rm -f ${RPM_BUILD_ROOT}%{_libdir}/python%{with_python_version}/site-packages/_bc.*a

%clean
rm -fr $RPM_BUILD_ROOT

%post -n %libname -p /sbin/ldconfig

%postun -n %libname -p /sbin/ldconfig

%files -n %libname
%defattr(-,root,root)
%doc README BENCHMARKS
%{_libdir}/*.so.*

%files -n %libnamedev
%defattr(-,root,root)
%doc BUGS docs/html docs/latex
%{_includedir}/%{name}
%{_libdir}/*.a
%{_libdir}/*.la
%{_libdir}/*.so

%if %{?with_python:1}0
%files python
%defattr(-,root,root)
%{_libdir}/python%{with_python_version}/site-packages/_bc.so
%endif

