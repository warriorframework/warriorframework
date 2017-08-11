from utils.date_time_stamp_utils import get_current_timestamp


class ErrorLog:

    def __init__(self, log_file):
        """
        Constructor for ErrorLog class

        :param log_file: Absolute path to the log file

        """
        self.log_file = log_file
        self.pending_logs = ""

    def write_log(self, logs):
        """
        This functions writed logs to the log file

        :param logs: Logs to be written into the log file
        """
        self.flush()
        print logs
        logs = "{2}-- {0} --{2} {1}".format(get_current_timestamp(), logs, "\n")
        with open(self.log_file, "a") as f:
            f.write(logs)

    def append_log(self, logs):
        """
        This function saves logs in memory to be written into the file later.

        :param logs: Logs to be written into the log file later
        """
        print logs
        self.pending_logs += "{2}-- {0} --{2} {1}".format(get_current_timestamp(), logs, "\n")

    def flush(self):
        """
        This function flushes pending logs into the log file
        """
        with open(self.log_file, "a") as f:
            f.write(self.pending_logs)
        self.pending_logs = ""
