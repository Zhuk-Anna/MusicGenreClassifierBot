pipeline {
    agent { label 'AnnaZhuk' }
    environment {
        STACK_NAME = "AZ_server_lab3"
    }

    stages {
        stage('Get server IP') {
            steps {
                withCredentials([string(credentialsId: 'Openstack_AZ', variable: 'OS_PASSWORD')]) {
                    withEnv([
                        "OS_AUTH_URL=https://cloud.crplab.ru:5000",
                        "OS_PROJECT_NAME=students",
                        "OS_USERNAME=master2025",
                        "OS_USER_DOMAIN_NAME=Default",
                        "OS_PROJECT_DOMAIN_ID=default",
                        "OS_REGION_NAME=RegionOne",
                        "OS_INTERFACE=public",
                        "OS_IDENTITY_API_VERSION=3"
                    ]) {
                        script {
                            env.SERVER_IP = sh(
                                script: "openstack stack output show ${env.STACK_NAME} server_ip -f json | jq -r '.output_value'",
                                returnStdout: true
                            ).trim()
                            echo "Server IP: ${env.SERVER_IP}"
                        }
                    }
                }
            }
        }

        stage('Deploy') {
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
                    )]) {

                    sshagent(['AnnaZhukSSH']) {

                        sh """
                        scp -o StrictHostKeyChecking=no docker-compose.yml ubuntu@$SERVER_IP:~

                        ssh -o StrictHostKeyChecking=no ubuntu@$SERVER_IP "
                            export DOCKERHUB_USER=${DOCKERHUB_USER};
                            export DOCKERHUB_PASS=${DOCKERHUB_PASS};
                            export TELEGRAM_TOKEN=${TELEGRAM_TOKEN};
                            echo \$DOCKERHUB_PASS | docker login -u \$DOCKERHUB_USER --password-stdin;

                            docker compose down || true;
                            docker compose pull;
                            docker compose up -d;

                            docker ps
                        "
                        """
                    }
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
    }
}