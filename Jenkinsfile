node {
     lock(inversePrecedence: true, quantity: 1, resource: 'myResource') {
          echo "date:" $(date +'%Y-%m-%d_%H-%M-%S')
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
      echo "date:" $(date +'%Y-%m-%d_%H-%M-%S')
    }
}
