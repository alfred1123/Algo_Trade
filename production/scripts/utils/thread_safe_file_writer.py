#!/usr/bin/python3

import threading

class ThreadSafeFileWriter:
    def __init__(self, file_path):
        self.file_path = file_path
        self.lock = threading.Lock()
        
    def write_data(self, data):
        with self.lock:
            with open(self.file_path, 'a') as file:
                file.write(data)
                
    def __enter__(self):
        return self
    
    def __exit__(self, exec_type, exec_val, exec_tb):
        pass