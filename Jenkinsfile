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

        stage('Build API Image') {
            steps {
                echo "Building API Docker image..."
                sh 'docker build -t music-api:latest -f api/Dockerfile .'
            }
        }

        stage('Build Bot Image') {
            steps {
                echo "Building Telegram Bot Docker image..."
                sh 'docker build -t music-bot:latest -f tg_bot/Dockerfile .'
            }
        }

        stage('Save Images') {
            steps {
                echo "Saving Docker images as tar files..."
                sh 'docker save music-api:latest -o music-api.tar'
                sh 'docker save music-bot:latest -o music-bot.tar'
            }
        }

        stage('Optional: Test Containers') {
            steps {
                echo "Starting containers with docker-compose for testing..."

                // Запускаем контейнеры через docker-compose
                sh 'TELEGRAM_TOKEN=${TELEGRAM_TOKEN} docker-compose up -d'

                // Проверяем, что контейнеры поднялись
                sh 'docker ps'

                echo "Wait some time to check app..."
                sh 'sleep 300' //  5 minutes
                sh 'docker-compose down'
            }
        }
    }

    post {
        success {
            archiveArtifacts artifacts: '*.tar', fingerprint: true
        }
        failure{
            echo 'Failure'
        }
    }
}