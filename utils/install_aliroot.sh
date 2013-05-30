#!/bin/bash


MY_VER_POST="0"
MY_VER_POST_ROOT="0"
FC_VER="18 17"
#FC_VER="18"
FC_VER_SRPM="18"
FC_TYPE="fedora-$FC_VER-x86_64"
FC_TYPE_EXTRA="-alice"

cd

ln -sfn ~/alice-repo-test/rpmbuild 

cd ~/alice-repo
git pull
cd 

#MY_VER="5-04-37"
MY_VER=`cat ~/rpmbuild/SPECS/aliroot-an.spec | grep "define alice_package_version" | awk '{print $3}'`
MY_VER2=$MY_VER
MY_VER=${MY_VER//./-}
MY_ROOT_VER=`cat ~/rpmbuild/SPECS/alice-aliroot.spec | grep "define root_ver" | awk '{print $3}'`
ALICE_REPO_DIR="$HOME/alice-repo"

if [ ! -f ~/rpmbuild/SOURCES/root_v$MY_ROOT_VER.source.tar.gz ];then
  MYPWD=`pwd`
  cd $ALICE_REPO_DIR/utils
  MY_ROOT_VER2=${MY_ROOT_VER//./-}
  ./pull-root.sh $MY_ROOT_VER2 || exit 1
  mv *.tar.gz ~/rpmbuild/SOURCES/
  cd $MYPWD
fi


if [ ! -f ~/rpmbuild/SOURCES/alice-aliroot-an-$MY_VER2.tar.gz ];then
  MYPWD=`pwd`
  cd $ALICE_REPO_DIR/utils
  ./pull-aliroot.sh $MY_VER || exit 1
  mv *.tar.gz ~/rpmbuild/SOURCES/
  cd $MYPWD
fi

function BuildRoot {
  
  FC_TYPE="fedora-$1-x86_64"
  TYPE_DIR=${FC_TYPE//-/\/}
  TYPE_DIR=${TYPE_DIR//fedora/alice} 
  LOCAL_REPO="/var/www/html/fedora/repos/alice/$1/x86_64"
  echo "Checking for rpm $LOCAL_REPO/alice-root-$MY_ROOT_VER-$MY_VER_POST_ROOT-0.fc$1.x86_64.rpm ..."
  if [ -f $LOCAL_REPO/alice-root-$MY_ROOT_VER-$MY_VER_POST_ROOT-0.fc$1.x86_64.rpm ];then
    return 1
  fi
  echo "$LOCAL_REPO/alice-root-$MY_ROOT_VER-$MY_VER_POST_ROOT-0.fc$1.x86_64.rpm not found!!! We are going to build it ..."
  # build rmps
  rpmbuild -bs ~/rpmbuild/SPECS/alice-root.spec 
  mock -r $FC_TYPE$FC_TYPE_EXTRA ~/rpmbuild/SRPMS/alice-root-$MY_ROOT_VER-$MY_VER_POST_ROOT-0.fc$FC_VER_SRPM.src.rpm || exit 1
  
}

function BuildAliRoot {
  
  FC_TYPE="fedora-$1-x86_64"
  TYPE_DIR=${FC_TYPE//-/\/}
  TYPE_DIR=${TYPE_DIR//fedora/alice} 
  LOCAL_REPO="/var/www/html/fedora/repos/$TYPE_DIR"
  echo "Checking for rpm $LOCAL_REPO/aliroot-an-${MY_VER2}-$MY_VER_POST-0.fc$1.x86_64.rpm ..."
  if [ -f $LOCAL_REPO/aliroot-an-${MY_VER2}-$MY_VER_POST-0.fc$1.x86_64.rpm ];then
    return 1
  fi
  echo "$LOCAL_REPO/aliroot-an-${MY_VER2}-$MY_VER_POST-0.fc$1.x86_64.rpm not found!!! We are going to build it ..."
  # build rmps
  rpmbuild -bs ~/rpmbuild/SPECS/alice-aliroot.spec
  rpmbuild -bs ~/rpmbuild/SPECS/aliroot-an.spec
  mock -r $FC_TYPE$FC_TYPE_EXTRA ~/rpmbuild/SRPMS/alice-aliroot-an-$MY_VER2-$MY_VER_POST-0.fc$FC_VER_SRPM.src.rpm || exit 1
  mock -r $FC_TYPE$FC_TYPE_EXTRA --no-clean ~/rpmbuild/SRPMS/aliroot-an-${MY_VER2}-$MY_VER_POST.fc$FC_VER_SRPM.src.rpm || exit 1
  
}

function RsyncWith {

  FC_TYPE="fedora-$1-x86_64"
  TYPE_DIR=${FC_TYPE//-/\/}
  TYPE_DIR=${TYPE_DIR//fedora/alice}
  LOCAL_REPO="/var/www/html/fedora/repos/$TYPE_DIR"
  mkdir -p $LOCAL_REPO
  mv /var/lib/mock/$FC_TYPE$FC_TYPE_EXTRA/result/*.rpm $LOCAL_REPO/
  if [ "$?" = "0" ];then
    createrepo $LOCAL_REPO
  fi
  cat hosts.txt
  echo "prsync -ar -A -h hosts.txt $LOCAL_REPO /var/www/html/fedora/repos/$TYPE_DIR/"
  #prsync -ar -A -h hosts.txt $LOCAL_REPO `dirname /var/www/html/fedora/repos/$TYPE_DIR/`
  prsync -ar -h hosts.txt $LOCAL_REPO `dirname /var/www/html/fedora/repos/$TYPE_DIR/`
  
}

echo "Building AliRoot v$MY_VER-AN ..."
for MY_FC_VER in $FC_VER;do
#  echo "$MY_FC_VER"
  BuildRoot $MY_FC_VER
  RsyncWith $MY_FC_VER
  BuildAliRoot $MY_FC_VER
  RsyncWith $MY_FC_VER
done
