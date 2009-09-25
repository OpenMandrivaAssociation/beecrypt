%define cvs 0
%if %cvs
%define release %mkrel 0.%cvs.1
%else
%define release %mkrel 2
%endif

%define	with_python --with-python=%_bindir/python
%define with_cplusplus --with-cplusplus
%ifnarch %mips %java
%define with_java --with-java
%endif

%define major 7
%define libname %mklibname %{name} %{major}
%define libname_cxx %mklibname %{name}_cxx %{major}
%define libname_java %mklibname %{name}_java %{major}
%define develname %mklibname %{name} -d

Summary:	An open source cryptography library
Name:		beecrypt
Version:	4.2.1
Release:	%{release}
Group:		System/Libraries
License:	LGPLv2+
URL:		http://beecrypt.sourceforge.net/
%if %cvs
Source0:	%{name}-%{cvs}.tar.lzma
%else
Source0:	http://prdownloads.sourceforge.net/beecrypt/%{name}-%{version}.tar.gz
%endif
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
BuildRequires:	doxygen
BuildRequires:	tetex-dvips
BuildRequires:	tetex-latex
BuildRequires:	graphviz
BuildRequires:	m4
BuildRequires:	libgomp-devel
%if %{?with_python:1}0
BuildRequires:	python-devel >= %{pyver}
%endif
%if %{?with_cplusplus:1}0
BuildRequires:	icu-devel
%endif
%if %{?with_java:1}0
BuildRequires:	java-rpmbuild
%endif
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
Beecrypt is a general-purpose cryptography library.

%package -n	%{libname}
Summary:	An open source cryptography library
Group:		System/Libraries

%description -n %{libname}
Beecrypt is a general-purpose cryptography library.

%package -n	%{develname}
Summary:	Files needed for developing applications with beecrypt
Group:		Development/C
%if %{?with_cplusplus:1}0
Requires:	%{libname_cxx} = %{version}
%endif
%if %{?with_java:1}0
Requires:	%{libname_java} = %{version}
%endif
Requires:	%{libname} = %{version}
Provides:	%{name}-devel = %{version}-%{release}
Provides:	lib%{name}-devel = %{version}-%{release}
Obsoletes:	%{mklibname beecrypt 7 -d}

%description -n	%{develname}
Beecrypt is a general-purpose cryptography library.  This package contains
files needed for developing applications with beecrypt.

%if %{?with_python:1}0
%package	python
Summary:	Files needed for python applications using beecrypt
Group:		Development/C
Requires:	python >= %{pyver}
Requires:	%{libname} = %{version}

%description	python
Beecrypt is a general-purpose cryptography library.  This package contains
files needed for using python with beecrypt.
%endif

%if %{?with_cplusplus:1}0
%package -n	%{libname_cxx}
Summary:	Files needed for C++ applications using beecrypt
Group:		Development/C++
Requires:	%{libname} = %{version}

%description -n	%{libname_cxx}
Beecrypt is a general-purpose cryptography library.  This package contains
files needed for using C++ with beecrypt.
%endif

%if %{?with_java:1}0
%package -n	%{libname_java}
Summary:	Files needed for java applications using beecrypt
Group:		Development/C
Requires:	%{libname} = %{version}

%description -n	%{libname_java}
Beecrypt is a general-purpose cryptography library.  This package contains
files needed for using java with beecrypt.
%endif

%prep

%if %cvs
%setup -q -n %{name}
%else
%setup -q
%endif
%patch0 -p1 -b .biarch
%patch1 -p0 -b .lib64
%patch2 -p1 -b .link

%build
%if %cvs
./autogen.sh
%endif

%configure2_5x \
    --enable-shared \
    --enable-static \
    %{?with_python} \
    %{?with_cplusplus} \
    %{?with_java} \
    CPPFLAGS="-I%{_includedir}/python%{pyver}"

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
rm -fr %{buildroot}

%makeinstall_std

# XXX nuke unpackaged files, artifacts from using libtool to produce module
rm -f %{buildroot}%{_libdir}/python%{pyver}/site-packages/_bc.*a

%if %mdkversion < 200900
%post -n %{libname} -p /sbin/ldconfig
%endif

%if %mdkversion < 200900
%postun -n %{libname} -p /sbin/ldconfig
%endif

%if %mdkversion < 200900
%post -n %{libname_cxx} -p /sbin/ldconfig
%endif

%if %mdkversion < 200900
%postun -n %{libname_cxx} -p /sbin/ldconfig
%endif

%if %mdkversion < 200900
%post -n %{libname_java} -p /sbin/ldconfig
%endif

%if %mdkversion < 200900
%postun -n %{libname_java} -p /sbin/ldconfig
%endif

%clean
rm -fr %{buildroot}

%files -n %{libname}
%defattr(-,root,root)
%doc README BENCHMARKS
%{_libdir}/libbeecrypt.so.%{major}*

%files -n %{develname}
%defattr(-,root,root)
%doc BUGS docs/html docs/latex
%{_includedir}/%{name}
%if %{?with_cplusplus:1}0
%{_libdir}/%{name}/base.so
%{_libdir}/%{name}/*.*a
%endif
%{_libdir}/*.a
%{_libdir}/*.la
%{_libdir}/*.so

%if %{?with_python:1}0
%files python
%defattr(-,root,root)
%{_libdir}/python%{pyver}/site-packages/_bc.so
%endif

%if %{?with_cplusplus:1}0
%files -n %{libname_cxx}
%defattr(-,root,root)
%config %{_sysconfdir}/beecrypt.conf
%dir %{_libdir}/%{name}
%{_libdir}/%{name}/base.so.*
%{_libdir}/libbeecrypt_cxx.so.%{major}*
%endif

%if %{?with_java:1}0
%files -n %{libname_java}
%defattr(-,root,root)
%{_libdir}/libbeecrypt_java.so.%{major}*
%endif
