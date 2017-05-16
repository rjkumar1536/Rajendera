node {
    stage 'CHECKOUT'
    echo 'Hello World'
    checkout([$class: 'GitSCM', branches: [[name: 'arsenal']], doGenerateSubmoduleConfigurations: false, extensions: [], submoduleCfg: [], userRemoteConfigs: [[url: 'https://github.com/rjkumar1536/Rajendera.git']]])
   
   
    stage 'BUILD'
    step([$class: 'GitHubPRStatusBuilder', statusMessage: [content: '${GITHUB_PR_COND_REF} run started']])
    echo 'Hello from build'
}