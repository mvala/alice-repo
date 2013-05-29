%define openssl_ver 0.9.8x
%define xrootd_ver 3.0.5
%define xrootd_ver 3.2.4
%define alien_ver 1.0.14n
%define alien_ver 1.0.14p
%define package_name root
%define package_ver 5.34.07
%define alice_dir /opt/cern/alice
%define alice_prefix %{alice_dir}/root/%{package_ver}
#%define alice_env_module_dir %{alice_dir}/env_modules
%define debug_package %{nil}
#%define _unpackaged_files_terminate_build 0


Name:           alice-%{package_name}-%{package_ver}
Version:        0
Release:        0%{?dist}
Summary:        ROOT for ALICE
Group:          Applications/Engineering
License:        LGPLv2+
URL:            http://root.cern.ch/
Source:         root_v5.34.05.source.tar.gz
Source1:        openssl-%{openssl_ver}.tar.gz
Source2:        xrootd-%{xrootd_ver}.tar.gz
Source3:        xrootd-xalienfs-%{alien_ver}.tar.gz
Patch0:         openssl-0.9.8-no-rpath.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:  coreutils, perl, sed, zlib-devel, autoconf, libtool
BuildRequires:  libX11-devel, libXpm-devel, libXft-devel, libXext-devel
BuildRequires:  mesa-libGL-devel, glew-devel, libxml2-devel
Requires:       coreutils

%description
ROOT for ALICE

%prep
%setup -D -q -n %{package_name}-%{package_ver} -c %{package_name}-%{package_ver}
%setup -D -q -a 1 -n %{package_name}-%{package_ver} -c openssl-%{openssl_ver}
cd openssl-%{openssl_ver}
%patch0 -p1
cd ../
%setup -D -q -a 2 -n %{package_name}-%{package_ver} -c xrootd-%{xrootd_ver}
%setup -D -q -a 3 -n %{package_name}-%{package_ver} -c xrootd-xalienfs-%{alien_ver}

%build

export LD_LIBRARY_PATH="%{_builddir}/%{alice_prefix}/lib:$LD_LIBRARY_PATH"
cd openssl-%{openssl_ver}
./config --prefix=%{alice_prefix} shared
make # don't use _smp_mflags (parallel make)
make INSTALL_PREFIX=%{_builddir} install_sw
rm -rf %{_builddir}/%{alice_prefix}/{bin,ssl}
rm -rf %{_builddir}/%{alice_prefix}/lib/*.a
cd ..

cd xrootd-%{xrootd_ver}
#./configure.classic --prefix=%{_builddir}/%{alice_prefix} --with-ssl-incdir=%{_builddir}/%{alice_prefix}/include --with-ssl-libdir=%{_builddir}/%{alice_prefix}/lib \
#--enable-gsi --enable-secssl --no-arch-subdirs --disable-posix --disable-bonjour

cmake -DOPENSSL_ROOT_DIR=%{_builddir}/%{alice_prefix} ../

make %{?_smp_mflags}
make install DESTDIR=%{_builddir}/%{alice_prefix}
rm -Rf %{_builddir}/%{alice_prefix}/etc/*
cd ..
cd ..

cd xrootd-xalienfs-%{alien_ver}
rm -Rf autom4te.cache
./bootstrap.sh
./configure --prefix=%{alice_prefix} \
  --with-certificate-directory=%{_builddir}/%{alice_prefix}/share \
  --with-xrootd-location=%{_builddir}/%{alice_prefix}
make %{?_smp_mflags}
make install DESTDIR=%{_builddir}
make install-certificates
cd ..

cd root
./configure \
  --with-pythia6-uscore=SINGLE \
  --with-f77=gfortran \
  --with-ssl-incdir=%{_builddir}/%{alice_prefix}/include \
  --with-ssl-libdir=%{_builddir}/%{alice_prefix}/lib \
  --with-xrootd-incdir=%{_builddir}/%{alice_prefix}/include/xrootd \
  --with-xrootd-libdir=%{_builddir}/%{alice_prefix}/lib \
  --with-alien-incdir=%{_builddir}/%{alice_prefix}/include \
  --with-alien-libdir=%{_builddir}/%{alice_prefix}/lib \
  --fail-on-missing
  
make %{?_smp_mflags}
cd ..

%install
cp -Rp %{_builddir}/opt %{buildroot}/
rm -Rf %{_builddir}/opt
cd root
export ROOTSYS="%{buildroot}/%{alice_prefix}"
make install
cd ..

rm -Rf %{buildroot}/%{alice_prefix}/tutorials/pyroot/*
%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%{alice_prefix}

%post
# -p /sbin/ldconfig

%postun
# -p /sbin/ldconfig

%changelog
