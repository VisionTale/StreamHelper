# StreamHelper

**This project is still in development. It is not intended to be used in production yet. If you do so, you are on your
own risk and you have been warned.**

## Setup
**Important**: Even tough the application should run on MacOS and Windows, only Linux is actively supported. Feel free 
to open issues if you encounter problems on any OS, but I may or may not be able to solve it without external help. 
Also, make sure whether the problem is related to the actual framework, or if it is related to other plugins. Any help
is welcome. 

### docker-compose (recommended)

+ Make sure you have a recent version of docker and docker-compose installed.
    + https://docs.docker.com/engine/install/
    + https://docs.docker.com/compose/install/
+ Download the files
    + If you want, you can edit tools/docker-compose.yml to adjust the parameters. If you don't know what you are doing, 
    default values should be fine in almost all cases. 
+ Open a terminal in the tools folder
+ Build the container (you can skip this step if you want to develop on the code)
```shell script
docker-compose build
```

### docker

+ Make sure you have a recent version of docker installed.
    + https://docs.docker.com/engine/install/
+ Download the files
+ Open a terminal in the tools folder
+ Build the container manually
    + If you like to change parameters, find them in the args: section within tools/docker-compose.yml and pass them 
    with '--build-args key=value'. You can also change them in tools/Dockerfile directly. If you don't know what you are 
    doing, default values should be fine in almost all cases. 
```shell script
docker build -t visiontale/streamhelper .
```

## Usage

### docker-compose (recommended)

_Make sure to execute all commands within the tools folder_
 
+ Start the server
```shell script
docker-compose up -d
```
+ Rebuild container and start the server
```shell script
docker-compose up -d --build
```
+ Stop the server
```shell script
docker-compose down
```
+ Check the logs of the server
```shell script
docker logs streamhelper
```
+ Check the logs of the server and watch all additions to the logs while watching (Press Ctrl-C to leave)
```shell script
docker logs -f streamhelper
```

### docker

+ Start the server
```shell script
docker run --name streamhelper -it visiontale/streamhelper
```
+ Stop the server
```shell script
docker stop streamhelper && docker rm streamhelper
```
+ Check the logs of the server
```shell script
docker logs streamhelper
```
+ Check the logs of the server and watch all additions to the logs while watching (Press Ctrl-C to leave)
```shell script
docker logs -f streamhelper
```


## License

[MIT License](./LICENSE)

## Credits

[Credits](./CREDITS.md)