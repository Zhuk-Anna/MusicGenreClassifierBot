pipeline {
    agent { label 'AnnaZhuk' }

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
                withCredentials([usernamePassword(
                    credentialsId: 'Dockerhub_AZ',
                    usernameVariable: 'DOCKERHUB_USER',
                    passwordVariable: 'DOCKERHUB_PASS'
                )]) {
                    withCredentials([string(
                        credentialsId: 'TG_Token_AZ',
                        variable: 'TELEGRAM_TOKEN'
                    )]) {
                        sh '''
                            export DOCKERHUB_USER=$DOCKERHUB_USER
                            docker compose down || true
                            docker compose pull || true
                            docker compose up -d
                        '''
                    }
                }
                // Проверяем, что контейнеры поднялись
                sh 'docker ps'
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