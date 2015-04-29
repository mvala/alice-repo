# no debug info is generated
%global debug_package %{nil}

# version
%define package_name aliphysics-an

%define alice_package_version 20150428
%define alice_aliroot_post_version 0
%define	alice_fedora_rev 0
#deps versions
%define aliroot_ver v5.06.14
%define aliroot_rev 0
%define aliroot_fedora_rev 0

#root  versions
%define root_ver 5.34.30
%define root_rev 0
%define root_fedora_rev 0

%define geant3_ver 2.0
%define geant3_rev 0
%define geant3_fedora_rev 0

#alice-geant3-1.15a.8.tar.gz
%define alice_name alice-%{package_name}

%define alice_dir /opt/cern/alice
%define alice_prefix %{alice_dir}/%{package_name}/%{alice_package_version}
%define alice_env_module_dir %{alice_dir}/env_modules

# version and deps
%define rootsys_dir %{alice_dir}/root/%{root_ver}
%define geant3_dir %{alice_dir}/geant3/%{geant3_ver}
%define aliroot_dir %{alice_dir}/aliroot/%{aliroot_ver}

Name:		%{alice_name}-%{alice_package_version}
Version:	%{alice_aliroot_post_version}
Release:	%{alice_fedora_rev}%{?dist}
Summary:	AliPhysics for ALICE
Group:		System Environment/Daemons
License:	LGPLv2+
URL:		http://aliceinfo.cern.ch/
Source0:	%{alice_name}-%{alice_package_version}.tar.gz
#Patch0:         geant3_makefile.patch
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:  alice-environment-modules
BuildRequires:  cmake git gcc-gfortran
#BuildRequires:  mesa-libGL-devel
#BuildRequires:  mesa-libGLU-devel
#BuildRequires:  glew-devel
BuildRequires:  alice-aliroot-%{aliroot_ver} = %{aliroot_rev}

#Requires:  alice-root-%{root_ver} = %{root_rev}
Requires:  alice-aliroot-%{aliroot_ver} = %{aliroot_rev}
Requires:  alice-environment-modules
Requires:  libgfortran

# Turn off the brp-python-bytecompile script
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')

# disable automatic lib search
AutoReqProv: no

%description
AliPhysics for ALICE

%prep
%setup -q -n %{alice_name}-%{alice_package_version}

%build
export ALIPHYSICS_ROOT="%{_builddir}/%{alice_name}-%{alice_package_version}/"

cd $ALIPHYSICS_ROOT
sed -i 's/include(CheckGitVersion)/#include(CheckGitVersion)/g' CMakeLists.txt 
mkdir build
cd build
cmake -DROOTSYS=%{rootsys_dir} -DALIEN=%{rootsys_dir} -DALIROOT=%{aliroot_dir} -DCMAKE_INSTALL_PREFIX=%{alice_prefix} $ALIPHYSICS_ROOT
mkdir version
cat > version/ARVersion.h <<EOF
#ifndef ALIPHYSICS_ARVersion
#define ALIPHYSICS_ARVersion
#define ALIPHYSICS_VERSION "%{alice_package_version}"
#define ALIPHYSICS_REVISION "%{alice_aliroot_post_version}"
#define ALIPHYSICS_BRANCH ""
#define ALIPHYSICS_SERIAL 0
#endif
EOF
make %{?_smp_mflags}
make PWGCFfemtoscopy.par PWGCFfemtoscopyUser.par
cd %{_builddir}

%install
rm -rf %{buildroot}
cd %{_builddir}/%{alice_name}-%{alice_package_version}/build
make install DESTDIR=%{buildroot}/
export PATH="%{rootsys_dir}/bin:$PATH"
export ALICE_TARGET="$(root-config --arch)"

# creating pars
#make par-all
#mkdir -p %{buildroot}%{alice_prefix}/pars
#mv *.par %{buildroot}%{alice_prefix}/pars/

# copy * from source (TODO copy only headers)
cd ../
rm -Rf %{_builddir}/%{alice_name}-%{alice_package_version}/build
cp -rf * %{buildroot}%{alice_prefix}

# create module file
mkdir -p %{buildroot}%{alice_prefix}/etc/modulefiles
cat > %{buildroot}%{alice_prefix}/etc/modulefiles/%{alice_name}-%{alice_package_version}-%{version} <<EOF
#%Module 1.0
#
# AliRoot module for use with 'environment-modules' package:
#
prepend-path            PATH            %{rootsys_dir}/bin
prepend-path            PATH            %{aliroot_dir}/bin
prepend-path            PATH            %{alice_prefix}/bin
prepend-path            LD_LIBRARY_PATH %{rootsys_dir}/lib
prepend-path            LD_LIBRARY_PATH %{aliroot_dir}/lib
prepend-path            LD_LIBRARY_PATH %{alice_prefix}/lib
setenv                  ROOTSYS         %{rootsys_dir}
setenv                  GEANT3          %{alice_dir}
setenv                  ALICE_ROOT      %{aliroot_dir}
setenv                  ALICE_PHYSICS   %{alice_prefix}
setenv                  ALICE           %{alice_dir}
setenv                  X509_CERT_DIR   %{rootsys_dir}/share/certificates
setenv                  GSHELL_NO_GCC   1
setenv                  GSHELL_ROOT     %{rootsys_dir}
prepend-path            PYTHONPATH      %{rootsys_dir}/lib
EOF

mkdir -p %{buildroot}/etc/modulefiles
cp %{buildroot}%{alice_prefix}/etc/modulefiles/%{alice_name}-%{alice_package_version}-%{version} %{buildroot}/etc/modulefiles/
#rm -rf %{buildroot}/opt/cern/alice/aliphysics-an/20150415/PWGJE/EMCALJetTasks/Tracks/analysis/

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%{alice_prefix}
/etc/modulefiles/%{alice_name}-%{alice_package_version}-%{version}
%changelog

