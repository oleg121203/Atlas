"""
Automated Deployment Script for Atlas

This script automates the deployment process for the Atlas application, including
building, packaging, and deploying to specified environments.
"""

import argparse
import os
import subprocess
import sys
import shutil
import logging
from pathlib import Path
from typing import Optional, List, Dict

import requests

from core.logging import get_logger
from core.config import load_config
from security.security_utils import check_environment_security

# Set up logging
logger = get_logger("AtlasDeploy")

class DeploymentError(Exception):
    """Custom exception for deployment errors."""
    pass

class AtlasDeployer:
    """Handles the automated deployment of the Atlas application."""
    def __init__(self, environment: str, config_path: Optional[str] = None):
        """
        Initialize the deployer with target environment and configuration.
        
        Args:
            environment: Target deployment environment (dev, staging, prod)
            config_path: Path to configuration file, if any
        """
        self.environment = environment.lower()
        self.config = load_config(config_path, environment=self.environment)
        self.build_dir = Path(self.config.get("build_dir", "build"))
        self.package_dir = Path(self.config.get("package_dir", "dist"))
        self.version = self.config.get("version", "0.1.0")
        self.app_name = self.config.get("app_name", "atlas")
        self.deployment_targets = self.config.get("deployment_targets", {})
        self.setup_logging()
        logger.info("Initialized AtlasDeployer for environment: %s", self.environment)
    
    def setup_logging(self) -> None:
        """Set up logging configuration for deployment process."""
        log_level = self.config.get("logging", {}).get("level", "INFO")
        log_file = self.config.get("logging", {}).get("file", f"{self.app_name}_deploy.log")
        logging.basicConfig(
            level=getattr(logging, log_level.upper(), logging.INFO),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        logger.info("Logging configured for deployment")
    
    def check_prerequisites(self) -> bool:
        """
        Check if all prerequisites for deployment are met.
        
        Returns:
            bool: True if prerequisites are met, False otherwise
        """
        logger.info("Checking deployment prerequisites")
        
        # Check environment security
        if not check_environment_security():
            logger.warning("Environment security check failed")
            return False
        
        # Check if required tools are installed
        required_tools = ["git", "python", "pip"]
        for tool in required_tools:
            try:
                subprocess.run([tool, "--version"], check=True, capture_output=True, text=True)
                logger.debug("Tool %s is installed", tool)
            except (subprocess.CalledProcessError, FileNotFoundError):
                logger.error("Required tool %s is not installed or not found", tool)
                return False
        
        # Check configuration for target environment
        if self.environment not in self.deployment_targets:
            logger.error("No deployment target configured for environment: %s", self.environment)
            return False
        
        logger.info("All deployment prerequisites met")
        return True
    
    def build(self) -> bool:
        """
        Build the Atlas application.
        
        Returns:
            bool: True if build successful, False otherwise
        """
        logger.info("Starting build process for Atlas")
        try:
            # Ensure build directory exists
            self.build_dir.mkdir(parents=True, exist_ok=True)
            
            # Run build commands from config or default
            build_commands = self.config.get("build_commands", [
                "python -m build"
            ])
            
            for cmd in build_commands:
                logger.info("Executing build command: %s", cmd)
                result = subprocess.run(cmd, shell=True, check=True, text=True,
                                      cwd=Path.cwd(), capture_output=True)
                logger.debug("Build command output: %s", result.stdout)
                if result.stderr:
                    logger.warning("Build command stderr: %s", result.stderr)
            
            logger.info("Build process completed successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error("Build failed: %s", str(e))
            logger.error("Build error output: %s", e.stderr)
            return False
        except Exception as e:
            logger.error("Unexpected error during build: %s", str(e), exc_info=True)
            return False
    
    def package(self) -> bool:
        """
        Package the built application for deployment.
        
        Returns:
            bool: True if packaging successful, False otherwise
        """
        logger.info("Starting packaging process for Atlas")
        try:
            # Ensure package directory exists
            self.package_dir.mkdir(parents=True, exist_ok=True)
            
            # Package the build output (example: create a zip or tarball)
            package_name = f"{self.app_name}-{self.version}-{self.environment}.tar.gz"
            package_path = self.package_dir / package_name
            
            # Create a tarball of the build directory
            logger.info("Creating deployment package: %s", package_name)
            shutil.make_archive(
                str(self.package_dir / f"{self.app_name}-{self.version}-{self.environment}"),
                "gztar",
                self.build_dir
            )
            
            if not package_path.exists():
                logger.error("Package file not created: %s", package_path)
                return False
            
            logger.info("Packaging completed: %s", package_path)
            return True
        except Exception as e:
            logger.error("Error during packaging: %s", str(e), exc_info=True)
            return False
    
    def deploy(self) -> bool:
        """
        Deploy the packaged application to the target environment.
        
        Returns:
            bool: True if deployment successful, False otherwise
        """
        logger.info("Starting deployment to environment: %s", self.environment)
        try:
            target_config = self.deployment_targets.get(self.environment, {})
            deploy_type = target_config.get("type", "local")
            
            if deploy_type == "local":
                return self._deploy_local(target_config)
            elif deploy_type == "sftp":
                return self._deploy_sftp(target_config)
            elif deploy_type == "aws_s3":
                return self._deploy_aws_s3(target_config)
            elif deploy_type == "docker":
                return self._deploy_docker(target_config)
            else:
                logger.error("Unsupported deployment type: %s", deploy_type)
                return False
        except Exception as e:
            logger.error("Deployment failed: %s", str(e), exc_info=True)
            return False
    
    def _deploy_local(self, target_config: Dict) -> bool:
        """
        Deploy to a local directory.
        
        Args:
            target_config: Configuration for the target environment
        
        Returns:
            bool: True if successful, False otherwise
        """
        logger.info("Deploying to local environment")
        deploy_path = Path(target_config.get("path", f"/opt/{self.app_name}/{self.environment}"))
        backup = target_config.get("backup", True)
        
        try:
            # Create backup if requested and deploy_path exists
            if backup and deploy_path.exists():
                backup_file = deploy_path.parent / f"{deploy_path.name}_backup_{self.version}.tar.gz"
                logger.info("Creating backup at: %s", backup_file)
                shutil.make_archive(
                    str(deploy_path.parent / f"{deploy_path.name}_backup_{self.version}"),
                    "gztar",
                    deploy_path
                )
            
            # Ensure deploy directory exists
            deploy_path.mkdir(parents=True, exist_ok=True)
            
            # Extract deployment package to target directory
            package_name = f"{self.app_name}-{self.version}-{self.environment}.tar.gz"
            package_path = self.package_dir / package_name
            if not package_path.exists():
                logger.error("Deployment package not found: %s", package_path)
                return False
            
            logger.info("Extracting package to: %s", deploy_path)
            shutil.unpack_archive(package_path, deploy_path, "gztar")
            
            # Run post-deployment commands if any
            post_deploy_commands = target_config.get("post_deploy_commands", [])
            for cmd in post_deploy_commands:
                logger.info("Executing post-deploy command: %s", cmd)
                result = subprocess.run(cmd, shell=True, check=True, text=True,
                                      cwd=deploy_path, capture_output=True)
                logger.debug("Post-deploy command output: %s", result.stdout)
                if result.stderr:
                    logger.warning("Post-deploy command stderr: %s", result.stderr)
            
            logger.info("Local deployment successful to: %s", deploy_path)
            return True
        except Exception as e:
            logger.error("Local deployment failed: %s", str(e), exc_info=True)
            return False
    
    def _deploy_sftp(self, target_config: Dict) -> bool:
        """
        Deploy via SFTP to a remote server.
        
        Args:
            target_config: Configuration for the target environment
        
        Returns:
            bool: True if successful, False otherwise
        """
        logger.info("Deploying via SFTP")
        try:
            import paramiko
            
            host = target_config.get("host")
            port = target_config.get("port", 22)
            username = target_config.get("username")
            key_path = target_config.get("key_path")
            remote_path = target_config.get("remote_path")
            
            if not all([host, username, key_path, remote_path]):
                logger.error("Missing required SFTP configuration parameters")
                return False
            
            # Connect to remote server
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(host, port=port, username=username, key_filename=key_path)
            sftp = ssh.open_sftp()
            
            # Upload deployment package
            package_name = f"{self.app_name}-{self.version}-{self.environment}.tar.gz"
            package_path = self.package_dir / package_name
            remote_package_path = os.path.join(remote_path, package_name)
            
            if not package_path.exists():
                logger.error("Deployment package not found: %s", package_path)
                ssh.close()
                return False
            
            logger.info("Uploading package to remote server: %s", remote_package_path)
            sftp.put(str(package_path), remote_package_path)
            
            # Run remote commands if any
            post_deploy_commands = target_config.get("post_deploy_commands", [
                f"cd {remote_path} && tar -xzf {package_name}"
            ])
            for cmd in post_deploy_commands:
                logger.info("Executing remote command: %s", cmd)
                stdin, stdout, stderr = ssh.exec_command(cmd)
                output = stdout.read().decode()
                error = stderr.read().decode()
                if output:
                    logger.debug("Remote command output: %s", output)
                if error:
                    logger.warning("Remote command error: %s", error)
            
            sftp.close()
            ssh.close()
            logger.info("SFTP deployment successful to: %s:%s", host, remote_path)
            return True
        except Exception as e:
            logger.error("SFTP deployment failed: %s", str(e), exc_info=True)
            return False
    
    def _deploy_aws_s3(self, target_config: Dict) -> bool:
        """
        Deploy to AWS S3 bucket.
        
        Args:
            target_config: Configuration for the target environment
        
        Returns:
            bool: True if successful, False otherwise
        """
        logger.info("Deploying to AWS S3")
        try:
            import boto3
            from botocore.exceptions import ClientError
            
            bucket_name = target_config.get("bucket_name")
            region = target_config.get("region", "us-east-1")
            s3_path = target_config.get("s3_path", f"deployments/{self.environment}")
            
            if not bucket_name:
                logger.error("Missing S3 bucket name in configuration")
                return False
            
            # Initialize S3 client (assumes credentials are configured via environment or AWS CLI)
            s3_client = boto3.client("s3", region_name=region)
            
            # Upload deployment package to S3
            package_name = f"{self.app_name}-{self.version}-{self.environment}.tar.gz"
            package_path = self.package_dir / package_name
            s3_key = f"{s3_path}/{package_name}"
            
            if not package_path.exists():
                logger.error("Deployment package not found: %s", package_path)
                return False
            
            logger.info("Uploading package to S3 bucket: %s/%s", bucket_name, s3_key)
            s3_client.upload_file(str(package_path), bucket_name, s3_key)
            
            # Optionally trigger a notification or Lambda if configured
            if target_config.get("notify_lambda"):
                lambda_client = boto3.client("lambda", region_name=region)
                lambda_function = target_config.get("lambda_function")
                if lambda_function:
                    logger.info("Invoking Lambda function: %s", lambda_function)
                    lambda_client.invoke(
                        FunctionName=lambda_function,
                        InvocationType="Event",
                        Payload=f'{{"bucket": "{bucket_name}", "key": "{s3_key}", "environment": "{self.environment}" }}'.encode()
                    )
            
            logger.info("AWS S3 deployment successful to: %s/%s", bucket_name, s3_key)
            return True
        except ClientError as e:
            logger.error("AWS S3 deployment failed with client error: %s", str(e))
            return False
        except Exception as e:
            logger.error("AWS S3 deployment failed: %s", str(e), exc_info=True)
            return False
    
    def _deploy_docker(self, target_config: Dict) -> bool:
        """
        Deploy to Docker registry or container environment.
        
        Args:
            target_config: Configuration for the target environment
        
        Returns:
            bool: True if successful, False otherwise
        """
        logger.info("Deploying to Docker environment")
        try:
            registry = target_config.get("registry", "docker.io")
            image_name = target_config.get("image_name", f"{self.app_name}:{self.environment}-{self.version}")
            dockerfile_path = target_config.get("dockerfile", "Dockerfile")
            
            # Build Docker image
            logger.info("Building Docker image: %s", image_name)
            build_cmd = f"docker build -t {image_name} -f {dockerfile_path} ."
            result = subprocess.run(build_cmd, shell=True, check=True, text=True,
                                  cwd=Path.cwd(), capture_output=True)
            logger.debug("Docker build output: %s", result.stdout)
            if result.stderr:
                logger.warning("Docker build stderr: %s", result.stderr)
            
            # Tag image for registry if needed
            full_image_name = image_name
            if registry != "docker.io":
                full_image_name = f"{registry}/{image_name}"
                tag_cmd = f"docker tag {image_name} {full_image_name}"
                logger.info("Tagging Docker image for registry: %s", full_image_name)
                result = subprocess.run(tag_cmd, shell=True, check=True, text=True,
                                      cwd=Path.cwd(), capture_output=True)
                logger.debug("Docker tag output: %s", result.stdout)
                if result.stderr:
                    logger.warning("Docker tag stderr: %s", result.stderr)
            
            # Push image to registry
            logger.info("Pushing Docker image to registry: %s", full_image_name)
            push_cmd = f"docker push {full_image_name}"
            result = subprocess.run(push_cmd, shell=True, check=True, text=True,
                                  cwd=Path.cwd(), capture_output=True)
            logger.debug("Docker push output: %s", result.stdout)
            if result.stderr:
                logger.warning("Docker push stderr: %s", result.stderr)
            
            # Optionally deploy to a container orchestrator like Kubernetes
            if target_config.get("deploy_to_kubernetes", False):
                logger.info("Deploying to Kubernetes cluster")
                kube_config = target_config.get("kube_config")
                namespace = target_config.get("namespace", "default")
                
                if not kube_config:
                    logger.error("Kubernetes configuration not provided")
                    return False
                
                # Write kubeconfig to temporary file if provided as content
                import tempfile
                with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
                    f.write(kube_config)
                    kubeconfig_path = f.name
                
                # Use kubectl to apply deployment
                deploy_cmd = (f"KUBECONFIG={kubeconfig_path} kubectl apply -f "
                            f"{target_config.get('deployment_yaml')} -n {namespace}")
                logger.info("Executing Kubernetes deployment: %s", deploy_cmd)
                result = subprocess.run(deploy_cmd, shell=True, check=True, text=True,
                                      cwd=Path.cwd(), capture_output=True)
                logger.debug("Kubernetes deploy output: %s", result.stdout)
                if result.stderr:
                    logger.warning("Kubernetes deploy stderr: %s", result.stderr)
                
                # Clean up temporary kubeconfig
                os.unlink(kubeconfig_path)
            
            logger.info("Docker deployment successful for image: %s", full_image_name)
            return True
        except subprocess.CalledProcessError as e:
            logger.error("Docker deployment failed with subprocess error: %s", str(e))
            logger.error("Subprocess error output: %s", e.stderr)
            return False
        except Exception as e:
            logger.error("Docker deployment failed: %s", str(e), exc_info=True)
            return False
    
    def monitor_deployment(self) -> bool:
        """
        Monitor the deployment status and health.
        
        Returns:
            bool: True if deployment is healthy, False otherwise
        """
        logger.info("Monitoring deployment for environment: %s", self.environment)
        try:
            target_config = self.deployment_targets.get(self.environment, {})
            health_check_url = target_config.get("health_check_url")
            health_check_cmd = target_config.get("health_check_cmd")
            
            if health_check_url:
                logger.info("Performing health check via URL: %s", health_check_url)
                response = requests.get(health_check_url, timeout=10)
                if response.status_code == 200:
                    logger.info("Health check successful: %s", response.text)
                    return True
                else:
                    logger.error("Health check failed with status code: %d", response.status_code)
                    return False
            elif health_check_cmd:
                logger.info("Performing health check via command: %s", health_check_cmd)
                result = subprocess.run(health_check_cmd, shell=True, check=True, text=True,
                                      cwd=Path.cwd(), capture_output=True)
                logger.debug("Health check command output: %s", result.stdout)
                if result.stderr:
                    logger.warning("Health check command stderr: %s", result.stderr)
                return True
            else:
                logger.warning("No health check configured for environment: %s", self.environment)
                return True  # Assume success if no check is defined
        except Exception as e:
            logger.error("Deployment monitoring failed: %s", str(e), exc_info=True)
            return False
    
    def run(self) -> bool:
        """
        Execute the full deployment pipeline.
        
        Returns:
            bool: True if deployment pipeline completed successfully, False otherwise
        """
        logger.info("Starting deployment pipeline for Atlas to environment: %s", self.environment)
        try:
            if not self.check_prerequisites():
                logger.error("Deployment prerequisites not met, aborting")
                return False
            
            if not self.build():
                logger.error("Build stage failed, aborting deployment")
                return False
            
            if not self.package():
                logger.error("Packaging stage failed, aborting deployment")
                return False
            
            if not self.deploy():
                logger.error("Deployment stage failed")
                return False
            
            if not self.monitor_deployment():
                logger.warning("Deployment monitoring indicates issues, but deployment completed")
                return False
            
            logger.info("Deployment pipeline completed successfully for environment: %s", self.environment)
            return True
        except Exception as e:
            logger.error("Deployment pipeline failed: %s", str(e), exc_info=True)
            return False

def main():
    """Main function to run the deployment script."""
    parser = argparse.ArgumentParser(description="Automated deployment script for Atlas")
    parser.add_argument("--environment", "-e", default="dev",
                        choices=["dev", "staging", "prod"],
                        help="Target deployment environment")
    parser.add_argument("--config", "-c", help="Path to configuration file")
    parser.add_argument("--log-level", default="INFO",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                        help="Set the logging level")
    
    args = parser.parse_args()
    
    # Override log level if specified
    if args.log_level:
        logger.setLevel(getattr(logging, args.log_level.upper(), logging.INFO))
    
    deployer = AtlasDeployer(environment=args.environment, config_path=args.config)
    success = deployer.run()
    
    if success:
        logger.info("Deployment completed successfully")
        sys.exit(0)
    else:
        logger.error("Deployment failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
