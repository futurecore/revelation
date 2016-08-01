#!/usr/bin/env bash

set -ev

if [ "${TRAVIS_PULL_REQUEST}" = "false" ] && [ "${TRAVIS_BRANCH}" = "master" ] && [ `ls ${TRAVIS_BUILD_DIR}/bin/* 2>/dev/null | wc -l` = "3" ]; then
    echo -e "Deploying to revelation-bins.\n"

    # Configure git.
    git config --global user.email "travis-ci@travis-ci.org"
    git config --global user.name "Travis CI"

    # Clone revelation binaries repository.
    mkdir ${HOME}/revelation-bins
    cd ${HOME}/revelation-bins
    git init
    git pull https://$GH_TOKEN@github.com/futurecore/revelation-bins.git

    # Copy binary simulators into new repository.
    cp ${TRAVIS_BUILD_DIR}/bin/pydgin-revelation* .

    # Add, commit and push binary files.
    git add pydgin-revelation*
    git commit -m "Travis build ${TRAVIS_BUILD_NUMBER} pushed to master"
    git push --force --quiet https://$GH_TOKEN@github.com/futurecore/revelation-bins master

    echo -e "Deployed to revelation-bins.\n"
fi
