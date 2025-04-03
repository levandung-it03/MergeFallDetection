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