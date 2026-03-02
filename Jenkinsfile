pipeline {
    agent { label 'AnnaZhuk' }

    environment {
        TELEGRAM_TOKEN = credentials('TG_Token_AZ') // из Jenkins Credentials
    }

    stages {
        stage('Check server') {
            steps {
                sh 'whoami'
                sh 'hostname'
                sh 'pwd'
                sh 'java -version'
                sh 'docker --version'
                sh 'docker compose version'
            }
        }

//         stage('Build API Image') {
//             steps {
//                 sh 'docker build -t music-api:latest ./api'
//             }
//         }
//
//         stage('Build Bot Image') {
//             steps {
//                 sh 'docker build -t music-bot:latest ./tg_bot'
//             }
//         }
//
//         stage('Save Images') {
//             steps {
//                 sh 'docker save music-api:latest -o music-api.tar'
//                 sh 'docker save music-bot:latest -o music-bot.tar'
//             }
//         }
    }

    post {
//         success {
//             archiveArtifacts artifacts: '*.tar', fingerprint: true
//         }
            success{
                echo 'Success'
            }
            failure{
                echo 'Failure'
            }
    }
}