pipeline {
    agent { label 'AnnaZhuk' }
    environment {
        STACK_NAME = "AZ_server_lab3"
    }

    stages {
        stage('Create Infrastructure') {
            steps {
                script {
                    // Создаём стек в OpenStack через Heat (либо update при существующем)
                    sh '''
                        if openstack stack show ${STACK_NAME}; then
                            echo "Stack exists. Updating..."
                            openstack stack update -t infra/heat.yaml ${STACK_NAME}
                        else
                            echo "Creating stack..."
                            openstack stack create -t infra/heat.yaml ${STACK_NAME}
                        fi
                    '''
                }
            }
        }
        stage('Wait for stack') {
            steps {
                sh 'openstack stack wait ${STACK_NAME}'
            }
        }
        stage('Get server IP') {
            steps {
                script {
                    env.SERVER_IP = sh(
                        script: "openstack stack output show ${STACK_NAME} server_ip -f value",
                        returnStdout: true
                    ).trim()

                    echo "Server IP = ${env.SERVER_IP}"
                }
            }
        }
        stage('Test infrastructure'){
            steps{
                sh "ssh ubuntu@${env.SERVER_IP} 'echo Server ready'"
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