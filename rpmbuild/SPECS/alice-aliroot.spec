# no debug info is generated
%global debug_package %{nil}

# version
%define package_name aliroot

%define alice_package_version v5.06.14
%define alice_aliroot_post_version 0
%define	alice_fedora_rev 0
#deps versions
%define root_ver 5.34.30
%define root_rev 0
%define root_fedora_rev 0

%define geant3_ver 2.0
%define geant3_rev 0
#%define geant3_fedora_rev 0

#alice-geant3-1.15a.8.tar.gz
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
Source1:        alice-geant3-%{geant3_ver}.%{geant3_rev}.tar.gz
#Patch0:         geant3_makefile.patch
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:  alice-environment-modules
BuildRequires:  cmake git gcc-gfortran
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
#%setup -q -n %{alice_name}-%{alice_package_version}
%setup -D -q -a 1 -c alice-geant3-%{geant3_ver}.%{geant3_rev}
ln -sfn alice-geant3-%{geant3_ver}.%{geant3_rev} geant3

%build
export ROOTSYS="%{rootsys_dir}"
export GEANT3="%{_builddir}/%{alice_name}-%{alice_package_version}-%{alice_aliroot_post_version}/geant3"
export LD_LIBRARY_PATH="%{rootsys_dir}/lib:$LD_LIBRARY_PATH"
export PATH="%{rootsys_dir}/bin:$PATH"
export ALICE_TARGET="$(root-config --arch)"
export ALICE_INSTALL="%{alice_prefix}"
export LD_LIBRARY_PATH="$GEANT3/lib/tgt_$ALICE_TARGET:$LD_LIBRARY_PATH"
export ALICE_ROOT="%{_builddir}/%{alice_name}-%{alice_package_version}-%{alice_aliroot_post_version}/%{alice_name}-%{alice_package_version}"
export ALICE="$(dirname ${ALICE_ROOT})"

cd $GEANT3
[ -d build ] || mkdir build
cd build
cmake ../
make
cd $ALICE_ROOT
sed -i 's/include(CheckGitVersion)/#include(CheckGitVersion)/g' CMakeLists.txt 

[ -d build ] || mkdir build
cd build
cmake -DROOTSYS=$ROOTSYS -DALIEN=$ROOTSYS -DCMAKE_INSTALL_PREFIX=%{alice_prefix} $ALICE_ROOT
cat > version/ARVersion.h <<EOF
#ifndef ALIROOT_ARVersion
#define ALIROOT_ARVersion
#define ALIROOT_VERSION "%{alice_package_version}"
#define ALIROOT_REVISION "%{alice_aliroot_post_version}"
#define ALIROOT_BRANCH ""
#define ALIROOT_SERIAL 0
#endif
EOF
make %{?_smp_mflags}
cd %{_builddir}

%install
rm -rf %{buildroot}
cd %{_builddir}/%{alice_name}-%{alice_package_version}-%{alice_aliroot_post_version}/%{alice_name}-%{alice_package_version}/build
make install DESTDIR=%{buildroot}/
export PATH="%{rootsys_dir}/bin:$PATH"
export ALICE_TARGET="$(root-config --arch)"

cd ../
rm -Rf %{_builddir}/%{alice_name}-%{alice_package_version}-%{alice_aliroot_post_version}/%{alice_name}-%{alice_package_version}/build
cp -rf * %{buildroot}%{alice_prefix}

cp -f %{_builddir}/%{alice_name}-%{alice_package_version}-%{alice_aliroot_post_version}/geant3/build/libgeant321.so %{buildroot}%{alice_prefix}/lib/
cp -f %{_builddir}/%{alice_name}-%{alice_package_version}-%{alice_aliroot_post_version}/geant3/TGeant3/TGeant3.h %{buildroot}%{alice_prefix}/include/

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%{alice_prefix}
%changelog
