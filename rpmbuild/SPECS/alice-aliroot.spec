# no debug info is generated
%global debug_package %{nil}

# version
%define package_name aliroot-an

%define alice_package_version 5.05.25
%define alice_aliroot_post_version 0
%define	alice_fedora_rev 0
#deps versions
%define root_ver 5.34.10
%define root_rev 0
%define root_fedora_rev 0
%define alice_name alice-%{package_name}

%define alice_dir /opt/cern/alice
%define alice_prefix %{alice_dir}/%{package_name}/%{alice_package_version}
%define alice_env_module_dir %{alice_dir}/env_modules

# version and deps
%define rootsys_dir %{alice_dir}/root/%{root_ver}
%define geant3_dir %{alice_dir}/geant3/%{geant3_ver}

Name:		%{alice_name}-%{alice_package_version}
Version:	%{alice_aliroot_post_version}
Release:	%{alice_fedora_rev}%{?dist}
Summary:	AliRoot for ALICE
Group:		System Environment/Daemons
License:	LGPLv2+ 
URL:		http://aliceinfo.cern.ch/
Source0:	%{alice_name}-%{alice_package_version}.tar.gz
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:  alice-environment-modules
BuildRequires:  cmake subversion gcc-gfortran
BuildRequires:  mesa-libGL-devel
BuildRequires:  mesa-libGLU-devel
BuildRequires:  glew-devel
BuildRequires:  alice-root-%{root_ver} = %{root_rev}
Requires:  alice-root-%{root_ver} = %{root_rev}
Requires:  alice-environment-modules
Requires:  libgfortran

# disable automatic lib search
AutoReqProv: no

%description
AliRoot for ALICE

%prep
%setup -q -n %{alice_name}-%{alice_package_version}

%build
export ROOTSYS="%{rootsys_dir}"
export GEANT3="%{geant3_dir}"
export LD_LIBRARY_PATH="%{rootsys_dir}/lib:$LD_LIBRARY_PATH"
export PATH="%{rootsys_dir}/bin:$PATH"
export ALICE_TARGET="$(root-config --arch)"
export ALICE_INSTALL="%{alice_prefix}"
export ALICE_ROOT="${PWD}"
export ALICE="$(dirname ${ALICE_ROOT})"
mkdir build
cd build
cmake $ALICE_ROOT
make %{?_smp_mflags}
cd %{_builddir}

%install
rm -rf %{buildroot}
cd build
make install DESTDIR=%{buildroot}/
export PATH="%{rootsys_dir}/bin:$PATH"
export ALICE_TARGET="$(root-config --arch)"

# creating pars
make par-all
mkdir -p %{buildroot}%{alice_prefix}/pars
mv *.par %{buildroot}%{alice_prefix}/pars/

# copy * from source (TODO copy only headers)
cd ../
rm -Rf build
cp -rf * %{buildroot}%{alice_prefix}

# create module file
mkdir -p %{buildroot}%{alice_prefix}/etc/modulefiles
cat > %{buildroot}%{alice_prefix}/etc/modulefiles/%{alice_name}-%{alice_package_version}-%{version} <<EOF
#%Module 1.0
# 
# AliRoot module for use with 'environment-modules' package:
# 
prepend-path            PATH            %{rootsys_dir}/bin
prepend-path            PATH            %{alice_prefix}/bin/tgt_$ALICE_TARGET
prepend-path            LD_LIBRARY_PATH %{rootsys_dir}/lib
prepend-path            LD_LIBRARY_PATH %{alice_prefix}/lib/tgt_$ALICE_TARGET
setenv                  ROOTSYS         %{rootsys_dir}
setenv                  GEANT3          %{alice_dir}
setenv                  ALICE_ROOT      %{alice_prefix}
setenv                  ALICE           %{alice_dir}
setenv                  ALICE_TARGET    $ALICE_TARGET
setenv                  X509_CERT_DIR   %{rootsys_dir}/share/certificates
setenv                  GSHELL_NO_GCC   1
setenv                  GSHELL_ROOT     %{rootsys_dir}
prepend-path            PYTHONPATH      %{rootsys_dir}/lib
EOF

mkdir -p %{buildroot}/etc/modulefiles
cp %{buildroot}%{alice_prefix}/etc/modulefiles/%{alice_name}-%{alice_package_version}-%{version} %{buildroot}/etc/modulefiles/

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%{alice_prefix}
/etc/modulefiles/%{alice_name}-%{alice_package_version}-%{version}
%changelog
