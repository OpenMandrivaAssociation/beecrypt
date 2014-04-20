%bcond_without	python
%bcond_without	cplusplus
%bcond_with	docs
%ifnarch %{mips} %{arm} aarch64
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
Patch5:         beecrypt_arm_configure_fix.patch

%if %{with docs}
# MD this is really ridiculous
# try bootstrapping a core package with theses BRs
BuildRequires:	doxygen
BuildRequires:	graphviz
BuildRequires:	m4
BuildRequires:	tetex-dvips
BuildRequires:	tetex-latex
BuildRequires:	texlive-doublestroke
%endif
BuildRequires:	gomp-devel
%if %{with python}
BuildRequires:	pkgconfig(python)
%endif
%if %{with cplusplus}
BuildRequires:	pkgconfig(icu-uc)
%endif
%if %{with java}
BuildRequires:	java-rpmbuild
BuildRequires:	java-devel-openjdk
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


for f in config.guess config.sub ; do
        test -f /usr/share/libtool/config/$f || continue
        find . -type f -name $f -exec cp /usr/share/libtool/config/$f \{\} \;
done


./autogen.sh

%build
export OPENMP_LIBS="-lgomp"
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

%if %{with docs}
pushd include/beecrypt
doxygen
cd c++
doxygen
popd
%endif

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
%if %{with docs}
%doc BUGS docs/html docs/latex
%endif
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

