%define package_name an
%define alice_name aliphysics-%{package_name}
%define alice_package_version 20151117
%define alice_package_fedora_rev 0

Name:		%{alice_name}
Version:	%{alice_package_version}
Release:	%{alice_package_fedora_rev}%{?dist}
Summary:	Virtual env package for ALICE
Group:		System Environment/Daemons
License:	LGPLv2+
URL:		http://aliceinfo.cern.ch
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Requires:	alice-aliphysics-an-%{alice_package_version} = %{alice_package_fedora_rev}

%description
Virtual package to for latest AliPhysics

%prep

%build

%install

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)

%changelog
