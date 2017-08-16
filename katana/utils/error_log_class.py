from utils.date_time_stamp_utils import get_current_timestamp


class ErrorLog:

    def __init__(self, log_file):
        """
        Constructor for ErrorLog class

        :param log_file: Absolute path to the log file

        """
        self.log_file = log_file

    def write_log(self, logs):
        """
        This functions writes logs to the log file

        :param logs: Logs to be written into the log file
        """
        print logs
        logs = "{2}-- {0} --{2} {1}".format(get_current_timestamp(), logs, "\n")
        with open(self.log_file, "a") as f:
            f.write(logs)
