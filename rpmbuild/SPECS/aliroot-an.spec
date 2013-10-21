%define package_name an
%define alice_name aliroot-%{package_name}
%define alice_package_version 5.05.28
%define alice_package_fedora_rev 0

Name:		%{alice_name}
Version:	%{alice_package_version}
Release:	%{alice_package_fedora_rev}%{?dist}
Summary:	Virtual env package for ALICE
Group:		System Environment/Daemons
License:	LGPLv2+
URL:		http://aliceinfo.cern.ch
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Requires:	alice-aliroot-an-%{alice_package_version} = %{alice_package_fedora_rev}

%description
Virtual package to have NEW AliRoot

%prep

%build

%install

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)

%changelog
