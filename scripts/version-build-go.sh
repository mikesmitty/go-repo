#!/bin/bash

# Copyright © 2017 Michael Smith <mikejsmitty@gmail.com>
# One of these days I may rewrite this in something other than bash. Maybe.

BUILD_VERSION=${1:-"false"}
UPLOAD=${2:-"false"}

DOWNLOAD_DIR="$HOME/download"
BUILD_DIR="$HOME/rpmbuild"
SPEC_REPO="$HOME/repo"
DOCKER_MOUNT="/tmp/rpmbuild"

if [ "$BUILD_VERSION" = "false" ]; then
    BUILD_VERSION="$(curl -s https://golang.org/ |grep -oPm1 '(?<=Build version go)[0-9.]+(?=\.)')"
    if [ -f $HOME/repo/SRPMS/golang-${BUILD_VERSION}-*.src.rpm ]; then
        echo Go $BUILD_VERSION appears to be already built. Exiting.
        exit 1
    fi
fi

# Direct the build to the correct repo
if echo "$BUILD_VERSION" | egrep -q '^[0-9.]+$'; then
    RELEASE="stable"
else
    RELEASE="unstable"
fi

if [ "$RELEASE" = "stable" ]; then
    REPO_DIR="/srv/go-repo"
elif [ "$RELEASE" = "unstable" ]; then
    REPO_DIR="/srv/unstable-go-repo"
else
    REPO_DIR="$HOME/test-repo"
fi

FILE_NAME="go${BUILD_VERSION}.src.tar.gz"
FILE_VERSION="$(echo $FILE_NAME |grep -oP '.+(?=.src.tar.gz)')"
MAJOR_MINOR_PATCH="$(echo $FILE_VERSION |grep -oP '(?<=go).+')"
MAJOR_MINOR="$(echo $MAJOR_MINOR_PATCH |egrep -o '[0-9]\.[0-9]+')"

function getTarball {
    if [ ! -f $DOWNLOAD_DIR/$FILE_NAME ]; then
        PKG_URL="$(curl -s https://golang.org/dl/ |egrep -om1 "[^\">]+go${BUILD_VERSION}.src.tar.gz")"
        if [ -z "$PKG_URL" ]; then
            echo Could not find tarball for version $BUILD_VERSION
            exit 1
        fi
        
        echo Downloading package: $PKG_URL

        wget -O $DOWNLOAD_DIR/$FILE_NAME "$PKG_URL"
        return $?
    else
        echo "No new package to download, using cached tarball"
        return 0
    fi
}

function cleanBuildEnv {
    rm -rf $BUILD_DIR
    mkdir -p $BUILD_DIR/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
    rm -fv $DOCKER_MOUNT/*.src.rpm
    rm -fv $DOCKER_MOUNT/output/*/*.rpm
    docker system prune --force
}

function buildSrcRpm {
    # Copy in our patches and source files
    cp -fv $SPEC_REPO/SOURCES/* $BUILD_DIR/SOURCES/
    cp -fv $DOWNLOAD_DIR/go${BUILD_VERSION}.src.tar.gz $BUILD_DIR/SOURCES/

    # Choose a spec file
    MMP_DIR="$SPEC_REPO/SPECS/$MAJOR_MINOR_PATCH"
    MM_DIR="$SPEC_REPO/SPECS/$MAJOR_MINOR"

    # Full version number (e.g. 1.8.3)
    if [ -d $MMP_DIR ];then 
        SRC_SPEC="$MMP_DIR/golang.spec"
    # Major and minor version number only (e.g. 1.8)
    elif [ -d $MM_DIR ];then 
        SRC_SPEC="$MM_DIR/golang.spec"
    else
        echo "No usable spec file found"
        return 1
    fi

    # Generate a spec file by replacing the vesion number tokens with this build's go version
    sed -e "s/MAJOR_MINOR_PATCH/$MAJOR_MINOR_PATCH/g" -e "s/MAJOR_MINOR/$MAJOR_MINOR/g" $SRC_SPEC > $BUILD_DIR/SPECS/golang.spec
    rpmbuild -bs $BUILD_DIR/SPECS/golang.spec || return 1
}

function signPackages {
    pkgDir="$1"

/usr/bin/expect <<EOD
set timeout 600
spawn bash -c "rpm --resign $pkgDir/*.rpm"
expect "Enter pass phrase:"
send "$SIGNING_PASSPHRASE\r"
expect eof
EOD
}

function buildTarget {
    dist="$1"
    vers="$2"
    arch="$3"
    opts="$4"

    if [ "$RELEASE" = "test" ]; then
        MOCKOPTS="${MOCKOPTS} --postinstall"
    fi

    if [ "$opts" = "noclean" ]; then
        MOCKOPTS="${MOCKOPTS} --no-clean"
    fi

    CONFIG="$dist-$vers-$arch"
    RESULT_DIR="/var/lib/mock/${CONFIG}/result"

    # Build the rpms
    echo "Building RPMs for distro: $CONFIG"
    mock -r $CONFIG --rebuild $MOCKOPTS ~/rpmbuild/SRPMS/golang-$MAJOR_MINOR_PATCH-*.src.rpm

    postBuild "$RESULT_DIR" "$@" || return 1
}

function dockerBuildTarget {
    dist="$1"
    vers="$2"
    arch="$3"
    opts="$4"

    if [ "$RELEASE" = "test" ]; then
        MOCKOPTS="${MOCKOPTS} -e POST_INSTALL=true"
    fi

    if [ "$opts" = "noclean" ]; then
        MOCKOPTS="${MOCKOPTS} -e NO_CLEANUP=true"
    fi

    CONFIG="$dist-$vers-$arch"
    RESULT_DIR="${DOCKER_MOUNT}/output/${CONFIG}"

    # Build the rpms
    echo "Building RPMs in docker for distro: $CONFIG"
    SRC_RPM="$(basename $BUILD_DIR/SRPMS/golang-$MAJOR_MINOR_PATCH-*.src.rpm)"
    docker run -it --privileged=true -e MOCK_CONFIG=$CONFIG -e SOURCE_RPM=$SRC_RPM $MOCK_OPTS -v $DOCKER_MOUNT:/rpmbuild mock-rpmbuilder

    postBuild "$RESULT_DIR" "$@" || return 1
}

function postBuild {
    RESULT_DIR="$1"
    dist="$2"
    vers="$3"
    arch="$4"
    opts="$5"

    rpmCount=$(ls $RESULT_DIR/*.rpm |wc -l)
    if [ "$RELEASE" != "test" ] && [ $rpmCount = 0 ]; then
        return 1
    fi

    if [ "$dist" = "epel" ]; then
        dist="centos"
    fi

    # Sign our packages and push them to the repo
    echo "Signing RPMs for distro: $CONFIG"
    signPackages "$RESULT_DIR/"
    cp -nv $RESULT_DIR/*.rpm $REPO_DIR/$dist/$vers/$arch/ || return 1

    # Relocate our SRPMs
    mv $REPO_DIR/$dist/$vers/$arch/*.src.rpm $REPO_DIR/$dist/$vers/Source/

    # Update repo metadata
    createrepo --update $REPO_DIR/$dist/$vers/$arch/
    createrepo --update $REPO_DIR/$dist/$vers/Source/
}

echo Building package: $MAJOR_MINOR_PATCH
getTarball

echo -e "\nRefreshing build environment..."
cleanBuildEnv

echo -e "\nBuilding package..."
buildSrcRpm || exit 1

echo -e "\nCopying source RPM to repo dir..."
cp -fv $BUILD_DIR/SRPMS/golang-$MAJOR_MINOR_PATCH-*.src.rpm "$HOME/repo/SRPMS/"
cp -fv $BUILD_DIR/SRPMS/golang-$MAJOR_MINOR_PATCH-*.src.rpm "$DOCKER_MOUNT/"

# Binary rebuilds
# CentOS 7
buildTarget "epel" "7" "x86_64" || exit 2

# CentOS 6
buildTarget "epel" "6" "x86_64" || exit 2
buildTarget "epel" "6" "i386" || exit 2

# Fedora 28
#dockerBuildTarget "fedora" "28" "x86_64" || exit 2

# Fedora 27
dockerBuildTarget "fedora" "27" "x86_64" || exit 2
dockerBuildTarget "fedora" "27" "i386" || exit 2

# Fedora 26
dockerBuildTarget "fedora" "26" "x86_64" || exit 2
dockerBuildTarget "fedora" "26" "i386" || exit 2

## Sign the repos
#for file in $(ls $REPO_DIR/*/*/repodata/repomd.xml); do
#    gpg --detach-sign --armor $file
#done

if [ "$UPLOAD" = "false" ]; then
    echo -e "\nSkipping upload"
    exit
fi

# Upload to server
if [ "$RELEASE" = "stable" ]; then
    rsync -rltoP --delete $REPO_DIR/centos/ $UPLOAD_HOST/centos/
    rsync -rltoP --delete $REPO_DIR/fedora/ $UPLOAD_HOST/fedora/
elif [ "$RELEASE" = "unstable" ]; then
    rsync -rltoP --delete $REPO_DIR/centos/ $UPLOAD_HOST/centos-unstable/
    rsync -rltoP --delete $REPO_DIR/fedora/ $UPLOAD_HOST/fedora-unstable/
fi
