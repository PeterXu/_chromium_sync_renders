#!/bin/sh
ROOT=`pwd`
CHROME=$ROOT/src
OS=`uname`

#sudo sysctl -w kern.maxproc=2500
#sudo sysctl -w kern.maxprocperuid=2500

function gsync() {
    gfile=$CHROME/.gclient
    #[ -f $gfile ] && return
    cd $CHROME && gclient config http://git.chromium.org

    if [ $OS = "Darwin" ]; then
        echo "target_os = ['mac']" >> $gfile
    elif [ $OS = "Linux" ]; then
        echo "target_os = ['unix']" >> $gfile
    fi
}

function initenv() {
    GYP_DEFINES=""
    if [ $OS = "Darwin" ]; then
        export GYP_GENERATORS="ninja,xcode-ninja"
        export GYP_GENERATOR_FLAGS="xcode_ninja_main_gyp=build/ninja/all.ninja.gyp"
        #GYP_DEFINES+=" clang=0" 
    elif [ $OS = "Linux" ]; then
        export GYP_GENERATORS="ninja"
        GYP_DEFINES+=" clang=1" 
    fi

    GYP_DEFINES+=" fastbuild=1"
    GYP_DEFINES+=" target_arch=x64"
    GYP_DEFINES+=" CONFIGURATION_NAME=Debug"
    GYP_DEFINES+=" ffmpeg_branding=Chrome proprietary_codecs=1"
    export GYP_DEFINES="$GYP_DEFINES"
}

function prepare() {
    cd $CHROME && build/gyp_chromium --depth .
}

function update() { 
    #cd $CHROME && build/install-build-deps.sh
    # for linux without plugin
    cd $CHROME && tools/clang/scripts/update.sh --force-local-build --without-android
    # for mac/ios
    #cd $CHROME && tools/clang/scripts/update.sh
}

function build() {
    UTIL=$CHROME/build/util
    [ ! -e "$UTIL/LASTCHANGE" ] && cd $UTIL && python lastchange.py -o LASTCHANGE
    [ ! -e "$UTIL/LASTCHANGE.blink" ] && cd $UTIL && python lastchange.py -o LASTCHANGE.blink

    cd $CHROME && ninja -C out/Debug chrome -j16
    #cd $CHROME && ninja -C out/Debug blink -j16
}



#gsync
initenv
#prepare
update
build
exit 0
