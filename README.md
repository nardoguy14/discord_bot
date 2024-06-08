

```
celery -A celery_worker worker --loglevel=info -P gevent -c 1000
celery -A celery_worker flower
```