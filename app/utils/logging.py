from functools import wraps

def log_message(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Starting process: {func.__name__}")
        
        result = func(*args, **kwargs)
        
        print(f"Finished process: {func.__name__}")
        return result
    
    return wrapper