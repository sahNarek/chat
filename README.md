The application is using MongoDB atlass as a data storage.
You should create a .env file in your local machine and add the keys as shown in .env.example
There are two types of servers, standard and premium, scripts run_standard.sh and run_premium.sh trigger the according configuration for servers. 
If you want to run two types simultaneously use run.sh

```
# Will run on port 3002
./run_premium.sh 
```

```
# Will run on port 3001
./run_standard.sh
```


```
# Will run both simultaneously
./run.sh
```
