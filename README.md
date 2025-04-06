# RUN DOCKER #
1. Tải Docker Desktop
2. Vào Terminal
> docker run --name mysql-local -p 3306:3306 -e MYSQL_ROOT_PASSWORD=sa -d mysql:8.0-debian

*Next*
> docker exec -it mysql-local mysql -u root -p
> 
*Password: <Nhập **sa**>*

> mysql> CREATE DATABASE merge_fall_detection;
> mysql> exit

# RUN APPLICATION #

- Run server in terminal with command line as (.venv) administration:
> uvicorn app.main:app --host 0.0.0.0 --port 8000 --timeout-keep-alive 60

### Others Command ###
> uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level debug

> uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload