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

        stage('Test Containers') {
            steps {
                echo "Starting containers with docker compose for testing..."

                // Запускаем контейнеры через docker-compose
                withEnv(["TELEGRAM_TOKEN=${TELEGRAM_TOKEN}"]) {
                    sh 'docker compose up -d'
                }

                // Проверяем, что контейнеры поднялись
                sh 'docker ps'

                echo "Waiting for API container to become healthy..."

                sh '''
                for i in {1..30}; do
                    STATUS=$(docker inspect --format='{{.State.Health.Status}}' music-api 2>/dev/null || echo "starting")
                    echo "Current health status: $STATUS"
                    if [ "$STATUS" = "healthy" ]; then
                        echo "API container is healthy!"
                        exit 0
                    fi
                    sleep 10
                done

                echo "API container failed to become healthy"
                exit 1
                '''
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
        }
    }

    post {
        success {
            echo 'Pipeline succeeded'
        }
        failure {
            echo 'Pipeline failed'
        }
        always {
            echo "Shutting down containers after tests..."
            sh 'docker compose down || true'
        }
    }
}