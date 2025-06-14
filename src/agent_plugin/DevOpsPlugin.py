from semantic_kernel.functions.kernel_function_decorator import kernel_function
from datetime import datetime
import textwrap

class DevopsPlugin:
    """A plugin that performs developer operation tasks."""
    
    def append_to_log_file(self, filepath: str, content: str) -> None:
        with open(filepath, 'a', encoding='utf-8') as file:
            file.write('\n' + textwrap.dedent(content).strip())

    @kernel_function(description="A function that restarts the named service")
    def restart_service(self, service_name: str = "", logfile: str = "") -> str:
        log_entries = [
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ALERT  DevopsAssistant: Multiple failures detected in {service_name}. Restarting service.",
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] INFO  {service_name}: Restart initiated.",
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] INFO  {service_name}: Service restarted successfully.",
        ]

        log_message = "\n".join(log_entries)
        self.append_to_log_file(logfile, log_message)
        
        return f"Service {service_name} restarted successfully."

    @kernel_function(description="A function that rollsback the transaction")
    def rollback_transaction(self, logfile: str = "") -> str:
        log_entries = [
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ALERT  DevopsAssistant: Transaction failure detected. Rolling back transaction batch.",
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] INFO   TransactionProcessor: Rolling back transaction batch.",
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] INFO   Transaction rollback completed successfully.",
        ]

        log_message = "\n".join(log_entries)
        self.append_to_log_file(logfile, log_message)
        
        return "Transaction rolled back successfully."

    @kernel_function(description="A function that redeploys the named resource")
    def redeploy_resource(self, resource_name: str = "", logfile: str = "") -> str:
        log_entries = [
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ALERT  DevopsAssistant: Resource deployment failure detected in '{resource_name}'. Redeploying resource.",
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] INFO   DeploymentManager: Redeployment request submitted.",
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] INFO   DeploymentManager: Service successfully redeployed, resource '{resource_name}' created successfully.",
        ]

        log_message = "\n".join(log_entries)
        self.append_to_log_file(logfile, log_message)
        
        return f"Resource '{resource_name}' redeployed successfully."

    @kernel_function(description="A function that increases the quota")
    def increase_quota(self, logfile: str = "") -> str:
        log_entries = [
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ALERT  DevopsAssistant: High request volume detected. Increasing quota.",
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] INFO   APIManager: Quota increase request submitted.",
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] INFO   APIManager: Quota successfully increased to 150% of previous limit.",
        ]

        log_message = "\n".join(log_entries)
        self.append_to_log_file(logfile, log_message)

        return "Successfully increased quota."

    @kernel_function(description="A function that escalates the issue")
    def escalate_issue(self, logfile: str = "") -> str:
        log_entries = [
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ALERT  DevopsAssistant: Cannot resolve issue.",
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ALERT  DevopsAssistant: Requesting escalation.",
        ]
        
        log_message = "\n".join(log_entries)
        self.append_to_log_file(logfile, log_message)
        
        return "Submitted escalation request."