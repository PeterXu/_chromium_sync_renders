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
    fi

    GYP_DEFINES+="fastbuild=1"
    GYP_DEFINES+=" target_arch=x64 CONFIGURATION_NAME=Debug"
    GYP_DEFINES+=" ffmpeg_branding=Chrome proprietary_codecs=1"
    export GYP_DEFINES="$GYP_DEFINES"
}

function prepare() {
    #[ $OS = "Linux" ] && cd $CHROME && sudo build/install-build-deps.sh
    cd $CHROME && build/gyp_chromium --depth .
    [ $OS = "Darwin" ] && cd $CHROME && tools/clang/scripts/update.sh
}

function build() {
    #cd $CHROME && ninja -C out/Debug chrome -j4
    cd $CHROME && ninja -C out/Debug blink -j4
}



gsync
initenv
prepare
build
exit 0
