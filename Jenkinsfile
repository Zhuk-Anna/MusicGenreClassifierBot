pipeline {
    agent { label 'AnnaZhuk' }
    environment {
        STACK_NAME = "AZ_server_lab3"
    }

    stages {
        stage('Infrastructure') {
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

                        sh '''
                            set -e
                            echo "Check if stack exists..."
                            STACK_EXISTS=$(openstack stack list -f value -c "Stack Name" | grep -w "${STACK_NAME}" || true)
                            if [ -n "$STACK_EXISTS" ]; then
                                echo "Stack exists. Updating..."
                                openstack stack update -t infra/heat/heat.yaml ${STACK_NAME}
                            else
                                echo "Creating stack..."
                                openstack stack create -t infra/heat/heat.yaml ${STACK_NAME}
                            fi
                        '''

                        sh '''
                            set -e
                            echo "Waiting for stack to finish..."

                            while true; do
                                STATUS=$(openstack stack show ${STACK_NAME} -f json | jq -r '.stack_status')
                                echo "Current status: $STATUS"

                                case "$STATUS" in
                                    *_IN_PROGRESS)
                                        sleep 10
                                        ;;
                                    *_COMPLETE)
                                        echo "Stack finished successfully"
                                        break
                                        ;;
                                    *_FAILED)
                                        echo "Stack failed!"
                                        openstack stack failures list ${STACK_NAME} || true
                                        exit 1
                                        ;;
                                esac
                            done
                        '''

                        script {
                            def serverIP = sh(
                                script: "openstack stack output show ${env.STACK_NAME} server_ip -f value | tail -n 1",
                                returnStdout: true
                            ).trim()
                            env.SERVER_IP = serverIP
                            echo "Server IP saved: ${env.SERVER_IP}"
                        }
                        sh '''
                        openstack stack output show ${STACK_NAME} server_ip -f json | jq -r '.output_value'
                        '''
                    }
                }
            }
        }

        stage('Test SSH access') {
            steps {
                sshagent(['AnnaZhukSSH']) {

                    withEnv(["TARGET_IP=${env.SERVER_IP}"]) {
                        sh '''
                            MAX_RETRIES=30
                            COUNT=0
                            until ssh -o StrictHostKeyChecking=no ubuntu@$TARGET_IP "echo Server ready"; do
                                echo "Wait for SSH..."
                                sleep 10
                                COUNT= $((COUNT+1))
                                if [ $COUNT -ge $MAX_RETRIES ]; then
                                    echo "SSH unavailable after $MAX_RETRIES retries"
                                    exit 1
                                fi
                            done
                        '''
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