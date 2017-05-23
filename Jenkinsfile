pipeline {
    agent any
    stages {
        stage('No-op') {
            steps {
                echo "stating"
                git credentialsId: '96616f8d-26fc-4ea5-9fc6-ed90a253e4db', url: 'git@github.com:rjkumar1536/Rajendera.git'
                slackSend color: 'danger', message: $BUILD_URL
               //githubNotify account: 'rjkumar1536',credentialsId: '96616f8d-26fc-4ea5-9fc6-ed90a253e4db',description: 'This is an example', repo: 'Rajendera',status: 'SUCCESS', targetUrl: 'https://my-jenkins-instance.com'
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
}
