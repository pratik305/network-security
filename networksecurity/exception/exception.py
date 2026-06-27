import sys
from networksecurity.logging import logger

class NetworkSecurityException(Exception):
    def __init__(self, error_message, error_detail: sys):
        super().__init__(error_message)

        # Extract execution details
        _,_, exc_tb = error_detail.exc_info()

        self.lineno = exc_tb.tb_lineno
        self.file_name = exc_tb.tb_frame.f_code.co_filename
        self.error_message = error_message

    def __str__(self):
        return(
            "Error occurred in python script: [{0}]"
            "at line number: [{1}]"
            "with error message: [{2}]".format(
                self.file_name, self.lineno, self.error_message
        ))
    
# Test block to demonstrate the usage of NetworkSecurityException
if __name__ == "__main__":  
    try:
        logger.logging.info("Entered the try block")
        result =1/0
        print(result)
    except Exception as e:
        raise NetworkSecurityException(e, sys)
    



