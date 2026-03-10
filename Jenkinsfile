pipeline {
    agent { label 'AnnaZhuk' }
    environment {
        APP_VERSION = "1.0"
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
                sh 'terraform --version'
                sh 'ansible --version'
            }
        }

        stage('Build API and Bot Images'){
            steps {
                echo "Building API Docker image..."
                sh 'docker build -t music-api:latest -f api/Dockerfile .'
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
                    sh '''
                        echo $DOCKERHUB_PASS | docker login -u $DOCKERHUB_USER --password-stdin

                        VERSION=${APP_VERSION}.${BUILD_NUMBER}

                        # ===== API IMAGE =====
                        docker tag music-api:latest $DOCKERHUB_USER/music-api:${VERSION}
                        docker push $DOCKERHUB_USER/music-api:${VERSION}

                        docker tag music-api:latest $DOCKERHUB_USER/music-api:latest
                        docker push $DOCKERHUB_USER/music-api:latest

                        # ===== BOT IMAGE =====
                        docker tag music-bot:latest $DOCKERHUB_USER/music-bot:${VERSION}
                        docker push $DOCKERHUB_USER/music-bot:${VERSION}

                        docker tag music-bot:latest $DOCKERHUB_USER/music-bot:latest
                        docker push $DOCKERHUB_USER/music-bot:latest

                        docker logout
                    '''
                }
            }
        }

        stage('Create Infrastructure, Configure, Deploy') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'Dockerhub_AZ',
                        usernameVariable: 'DOCKERHUB_USER',
                        passwordVariable: 'DOCKERHUB_PASS'
                    ),
                    string(
                        credentialsId: 'TG_Token_AZ',
                        variable: 'TELEGRAM_TOKEN'
                    ),
                    string(
                        credentialsId: 'Openstack_AZ',
                        variable: 'OS_PASSWORD')
                ]) {
                    withEnv([
                        "OS_AUTH_URL=https://cloud.crplab.ru:5000",
                        "OS_PROJECT_NAME=students",
                        "OS_USERNAME=master2025",
                        "OS_USER_DOMAIN_NAME=Default",
                        "OS_PROJECT_DOMAIN_ID=default",
                        "OS_REGION_NAME=RegionOne",
                        "OS_INTERFACE=public",
                        "OS_IDENTITY_API_VERSION=3",
                        "VERSION=${APP_VERSION}.${BUILD_NUMBER}"
                    ]) {
                        sshagent(['AnnaZhukSSH']) {
                            sh '''
                                cd infra/ansible
                                ansible-playbook playbook.yml
                            '''
                        }
                    }
                }
            }
        }

//         stage('Destroy Infrastructure') {
//             steps {
//                 withCredentials([
//                     string(
//                         credentialsId: 'Openstack_AZ',
//                         variable: 'OS_PASSWORD')
//                 ]) {
//                     withEnv([
//                         "OS_AUTH_URL=https://cloud.crplab.ru:5000",
//                         "OS_PROJECT_NAME=students",
//                         "OS_USERNAME=master2025",
//                         "OS_USER_DOMAIN_NAME=Default",
//                         "OS_PROJECT_DOMAIN_ID=default",
//                         "OS_REGION_NAME=RegionOne",
//                         "OS_INTERFACE=public",
//                         "OS_IDENTITY_API_VERSION=3"
//                     ]) {
//                         sh """
//                             cd infra/ansible
//                             ansible-playbook destroy.yml
//                         """
//                     }
//                 }
//             }
//         }
    }

    post {
        success {
            echo 'Pipeline succeeded'
        }
        failure {
            echo 'Pipeline failed'
        }
    }
}