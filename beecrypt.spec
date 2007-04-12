%define	with_python		--with-python
%{expand:%%define with_python_version %(python -V 2>&1| awk '{print $2}'|cut -d. -f1-2)}

%define libname %mklibname beecrypt 6
%define libnamedev %{libname}-devel

Summary:	An open source cryptography library
Name:		beecrypt
Version:	3.1.0
Release:	7mdk
Group:		System/Libraries
License:	LGPL
URL:		http://beecrypt.virtualunlimited.com/
Source0:	http://prdownloads.sourceforge.net/beecrypt/%{name}-3.1.0.tar.bz2
Patch0:		beecrypt-3.1.0-rh.patch
Patch1:		beecrypt-3.1.0-automake1.7.patch
Patch2:		beecrypt-3.1.0-configure.patch
BuildPreReq:	doxygen
%if %{?with_python:1}0
BuildPreReq:	python-devel >= %{with_python_version}
%endif
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildRequires:	automake1.7

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
Provides:	libbeecrypt-devel = %{version}-%{release}

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
%setup -q
%patch0 -p1 -b .rh
%patch1 -p1 -b .automake1.7
%patch2 -p1 -b .configure

./autogen.sh

%build

%configure2_5x	--enable-shared \
		--enable-static \
		%{?with_python} \
		CPPFLAGS="-I%{_includedir}/python%{with_python_version}"

%make
doxygen

# XXX delete next line to build with legacy, non-check aware, rpmbuild.
#%check
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

