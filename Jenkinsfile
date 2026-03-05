pipeline {
    agent { label 'AnnaZhuk' }
    environment {
        STACK_NAME = "AZ_server_lab3"
        OS_CLOUD   = 'mycloud' // for openstack client (without source students-openrc.sh)
    }

    stages {
        stage('Create or update Infrastructure') {
            steps {
                withCredentials([string(credentialsId: 'Openstack_AZ', variable: 'OS_PASSWORD')]) {
                    // Создаём стек в OpenStack через Heat (либо update при существующем)
                    sh '''
                        set -e
                        echo "Check if stack exists..."
                        if openstack stack show ${STACK_NAME} >/dev/null 2>&1; then
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
                withCredentials([string(credentialsId: 'Openstack_AZ', variable: 'OS_PASSWORD')]) {
                     sh '''
                        set -e
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
                            script: """
                                openstack stack output show ${env.STACK_NAME} server_ip -f value
                            """,
                            returnStdout: true
                        ).trim()

                        echo "Server IP = ${env.SERVER_IP}"
                    }
                }
            }
        }
        stage('Test SSH access'){
            steps{
                sshagent(['AnnaZhukSSH']) {
                    sh """
                        echo "Waiting for SSH to become available..."
                        MAX_RETRIES=30
                        COUNT=0
                        until ssh -o StrictHostKeyChecking=no ubuntu@${env.SERVER_IP} "echo Server ready"; do
                            echo "Wait for SSH..."
                            sleep 10
                            COUNT=\$((COUNT+1))
                            if [ \$COUNT -ge \$MAX_RETRIES ]; then
                                echo "SSH unavailable after \$MAX_RETRIES retries"
                                exit 1
                            fi
                        done
                    """
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