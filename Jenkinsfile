pipeline {
    agent any
    stages {
        stage('No-op') {
            steps {
                echo "stating"
               githubNotify account: 'rjkumar1536', credentialsId: 'rjkumar1536',description: 'This is an example', repo: 'Rajendera', sha: '0b5936eb903d439ac0c0bf84940d73128d5e9487', status: 'SUCCESS', targetUrl: 'https://my-jenkins-instance.com'
            }
        }
    }
    post {
        always {
            echo 'One way or another, I have finished'
            deleteDir() /* clean up our workspace */
        }
        success {
            echo 'I succeeeded!'
            /*job(String name) {
                publishers {
                    gitHubIssueNotifier {
                    }
                }
            }*/
        }
        unstable {
            echo 'I am unstable :/'
        }
        failure {
            echo 'I failed :('
        }
        changed {
            echo 'Things were different before...'
        }
    }
    job(String name) {
  publishers {
    gitHubIssueNotifier {
    }
  }
}
}
