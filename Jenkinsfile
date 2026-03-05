pipeline {
    agent { label 'AnnaZhuk' }
    environment {
        STACK_NAME = "AZ_server_lab3"
    }

    stages {
        stage('Create or update Infrastructure') {
            steps {
                withCredentials([string(credentialsId: 'Openstack_AZ', variable: 'OS_PASSWORD')]) {
                    // Создаём стек в OpenStack через Heat (либо update при существующем)
                    sh '''
                        . ~/students-openrc.sh

                        if openstack stack show ${STACK_NAME}; then
                            echo "Stack exists. Updating..."
                            openstack stack update -t infra/heat.yaml ${STACK_NAME}
                        else
                            echo "Creating stack..."
                            openstack stack create -t infra/heat.yaml ${STACK_NAME}
                        fi
                        openstack stack wait ${STACK_NAME}
                    '''
                }
            }
        }
        stage('Wait for stack') {
            steps {
                withCredentials([string(credentialsId: 'Openstack_AZ', variable: 'OS_PASSWORD')]) {
                     sh '''
                        . ~/students-openrc.sh

                        echo "Waiting for stack to finish..."
                        openstack stack wait ${STACK_NAME}
                     '''
                }
            }
        }
        stage('Get server IP') {
            steps {
                withCredentials([string(credentialsId: 'Openstack_AZ', variable: 'OS_PASSWORD')]) {
                    script {
                        env.SERVER_IP = sh(
                            script: '''
                                . ~/students-openrc.sh
                                openstack stack output show ${STACK_NAME} server_ip -f value
                            ''',
                            returnStdout: true
                        ).trim()

                        echo "Server IP = ${env.SERVER_IP}"
                    }
                }
            }
        }
        stage('Test infrastructure'){
            steps{
                sshagent(['AnnaZhukSSH']) {
                    sh '''
                        echo "Waiting for SSH to become available..."
                        sleep 30

                        ssh -o StrictHostKeyChecking=no ubuntu@${SERVER_IP} "echo Server ready"
                    '''
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