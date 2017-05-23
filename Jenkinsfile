pipeline {
    agent any
    stages {
        stage('No-op') {
            steps {
                echo "stating"
                githubNotify account: 'rjkumar1536',description: 'This is an example', repo: 'Rajendera', sha:'47:1d:1b:43:53:1e:7e:1c:43:cc:9d:8c:40:f9:ca:9a', status: 'SUCCESS', targetUrl: 'https://my-jenkins-instance.com'
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
