from celery import Celery

# Initialize Celery
celery = Celery(
    'tasks',
    broker='redis://localhost:6379/0',  # Use the appropriate Redis URL
    backend='redis://localhost:6379/0'
)

# Example task
@celery.task
def matchmake(user_id):
    return 1
