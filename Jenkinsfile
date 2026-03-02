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

        stage('Login to Docker Hub and push Images') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'Dockerhub_AZ',
                    usernameVariable: 'DOCKERHUB_USER',
                    passwordVariable: 'DOCKERHUB_PASS'
                )]) {
                    sh 'echo $DOCKERHUB_PASS | docker login -u $DOCKERHUB_USER --password-stdin'

                    // ===== API IMAGE =====
                    sh 'docker tag music-api:latest $DOCKERHUB_USER/music-api:${BUILD_NUMBER}'
                    sh 'docker push $DOCKERHUB_USER/music-api:${BUILD_NUMBER}'
                    sh 'docker tag music-api:latest $DOCKERHUB_USER/music-api:latest'
                    sh 'docker push $DOCKERHUB_USER/music-api:latest'

                    // ===== BOT IMAGE =====
                    sh 'docker tag music-bot:latest $DOCKERHUB_USER/music-bot:${BUILD_NUMBER}'
                    sh 'docker push $DOCKERHUB_USER/music-bot:${BUILD_NUMBER}'
                    sh 'docker tag music-bot:latest $DOCKERHUB_USER/music-bot:latest'
                    sh 'docker push $DOCKERHUB_USER/music-bot:latest'

                    sh 'docker logout'
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
            echo 'Pipeline succeeded'
        }
        failure{
            echo 'Pipeline failed'
        }
    }
}