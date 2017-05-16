node {
    step([$class: 'GitHubPRStatusBuilder', statusMessage: [content: '${GITHUB_PR_COND_REF} run started']])
    step([$class: 'GitHubPRCommentPublisher', comment: [content: 'Build ${BUILD_NUMBER} ${BUILD_STATUS}']])
    step([$class: 'GitHubSetCommitStatusBuilder'])
    stage('checkout') {
    // some block
        echo 'Checkout stage'
        checkout([$class: 'GitSCM', branches: [[name: 'arsenal']], doGenerateSubmoduleConfigurations: false, extensions: [], submoduleCfg: [], userRemoteConfigs: [[url: 'https://github.com/rjkumar1536/Rajendera.git']]])
        
    }
   
   stage('build') {
    // some block
        echo 'build stage'

    }
    stage('get server') {
    // some block
         echo 'get server'
    }
    stage('Remove node') {
    // some block
        echo 'remove node'
    }
    stage('Deploy code') {
    // some block
        echo 'Deploy code'
    }
    stage('APi Testing') {
    // some block
        echo 'api testing'
    }
    stage('add node') {
    // some block
        echo 'add node'
    }
    post { 
            always{
                step([$class: 'GitHubPRBuildStatusPublisher', buildMessage: [failureMsg: [content: 'Can\'t set status; build failed.'], successMsg: [content: 'Can\'t set status; build succeeded.']], statusMsg: [content: '${GITHUB_PR_COND_REF} run ended'], unstableAs: 'FAILURE'])
        }
            success { 
                echo 'I Say close this'
                step([$class: 'GitHubPRClosePublisher', errorHandler: [buildStatus: <object of type hudson.model.Result>], statusVerifier: [buildStatus: <object of type hudson.model.Result>]])
        }
    }



}
