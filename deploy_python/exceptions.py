
class DeploymentError(Exception):
    """Base deployment exception."""

class ConfigurationError(DeploymentError):
    pass

class ValidationError(DeploymentError):
    pass

class GitError(DeploymentError):
    pass

class DatabaseError(DeploymentError):
    pass

class SSHError(DeploymentError):
    pass

class HealthError(DeploymentError):
    pass

class ReportError(DeploymentError):
    pass

class RemoteDeploymentError(DeploymentError):
    pass
