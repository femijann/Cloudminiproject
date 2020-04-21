# API to extract Carbon intensity data GB regions

This project provides a python flask based application leveraging AWS, cassandra database and kubernetes engine.
The API provides an indicative trend of regional carbon intensity of the electricity system in Great Britain (GB) for current half hour. 
The implementation provides an application that allows to get carbon intensity data, specifically the region description, region id, intensity, index, fuel and the percentage.The API provides data specifically for a post code (Outward postcode i.e. RG41 or SW1 or TF8). It also allows you to make changes in the percentage of fuel emission for the regions.

The API used is from https://carbon-intensity.github.io/api-definitions/#carbon-intensity-api-v1-0-0

## Features
 1.REST-based service interface.
 2.Interaction with external REST services.
 3.Use of on an external Cloud database(cassandra db) for persisting information.
 4.Support for cloud scalability, deployment in a container environment.
 5.Cloud security measures by running my flask application over HTTPS Using self-signed certificate.

## Interaction with Web Application
###External API
    *GET* @app.route('/regional/<postcode>')
Get the details of the specific postcode using the external API.
###REST-based Service Interface
    *GET* @app.route('/')
Displays the Home page
       
    *GET* @app.route('/regional')
####POST request   
    *POST* @app.route('/regional/')    
This is a POST request and can be executed using the following curl command:
    
    curl -i -H "Content-Type: application/json" -X POST -d '{"key":164,"generationmixfuel":"nuclear","intensityindex":27,"intensityforecast":"low","generationmixpercentage":12.99,"region":"Westminister","regionid":20}' http://0.0.0.0:80/regional/
Response:

    HTTP/1.0 201 CREATED
    Content-Type: application/json
    Content-Length: 37
    Server: Werkzeug/1.0.1 Python/3.7.7

    {"message":"created: /regional/165"}
####PUT request
    *PUT* @app.route('/regional/') 
This is a PUT request and can be executed using the following curl command:
    
    curl -i -H "Content-Type: application/json" -X PUT -d '{"key":164,"generationmixfuel":"nuclear","intensityindex":27,"intensityforecast":"low","generationmixpercentage":12.99,"region":"Westminister","regionid":20}' http://0.0.0.0:80/regional/
Response:
    
    HTTP/1.0 200 OK
    Content-Type: application/json
    Content-Length: 37
    Server: Werkzeug/1.0.1 Python/3.7.7
    
    {"message":"updated: /regional/165"}
    
####DELETE request
     *DELETE* @app.route('/regional/') 
This is a DELETE request and can be executed using the following curl command:

    curl -i -H "Content-Type: application/json" -X DELETE -d '{"key":164,"generationmixfuel":"nuclear","intensityindex":27,"intensityforecast":"low","generationmixpercentage":12.99,"region":"Westminister","regionid":20}' http://0.0.0.0:80/regional/
Response:
    
    HTTP/1.0 200 OK
    Content-Type: application/json
    Content-Length: 37
    Server: Werkzeug/1.0.1 Python/3.7.7
    
    {"message":"deleted: /regional/165"}
    
## Apache Cassandra Database setup
1. Pull the latest Cassandra Docker image after docker installation.
        
        docker pull cassandra:latest
2. Run Cassandra in a Docker and export port 9042.

       sudo docker run --name cassandra-coursework -p 9042:9042 -d cassandra:latest
3. Load data into Cassandra database.
        
        sudo docker cp carbon_intensity.csv cassandra-coursework:/home/carbon.csv        
4. Access Cassandra in interactive mode.

        sudo docker exec -it cassandra-coursework cqlsh
5. Create a keyspace inside cassandra for the Carbon Intensity Database.

        create keyspace carbon_int with replication={'class':'SimpleStrategy','replication_factor':1};
6. Create a database table for carbon_int.stats.

        cqlsh> create table carbon_int.stats (key int PRIMARY KEY, fuel text,int_ind int, intensity text, perc float, region_desc text, region_id int);
7. Copy the contents of carbon_intensity.csv to carbon_int.stats table.

        copy carbon_int.stats(key, fuel, int_ind, intensity, perc, region_desc, region_id) from '/home/carbon_intensity.csv' with delimiter=',' and header=True;

## Cloud Security - HTTPS Implementation
The app is served over https by setting up the self-signed certificates as shown below:
1. Run in your project folder
    
        $ openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

2. Configure the certificate as shown below:

        Generating a RSA private key
        .....................................++++
        ....................................................................................++++
        writing new private key to 'key.pem'
        -----
        You are about to be asked to enter information that will be incorporated
        into your certificate request.
        What you are about to enter is what is called a Distinguished Name or a DN.
        There are quite a few fields but you can leave some blank
        For some fields there will be a default value,
        If you enter '.', the field will be left blank.
        
        Country Name (2 letter code) [AU]:UK
        State or Province Name (full name) [Some-State]:England
        Locality Name (eg, city) []:London
        Organization Name (eg, company) [Internet Widgits Pty Ltd]:QMUL 
        Organizational Unit Name (eg, section) []:
        Common Name (e.g. server FQDN or YOUR name) []:localhost
        Email Address []:       
3. Two files cret.pem and key.pem are created. Include these two files in the Coursework.py program file as shown below:
        
        if __name__ == "__main__":
            context = ('cert.pem','key.pem')
            app.run(host='0.0.0.0',port=443,ssl_context=context)
4. Add the certificate to serve the application over https
5. Run curl commands as below :
        
        curl -k -i -H "Content-Type: application/json" -X POST -d '{"key":165,"fuel":"biomass","int_ind":27,"intensity":"low","perc":12.99,"region_desc":"Middlesex","region_id":21}' https://0.0.0.0:443/regional/

        curl -k -i -H "Content-Type: application/json" -X PUT -d '{"key":165,"fuel":"biomass","int_ind":27,"intensity":"low","perc":9,"region_desc":"Middlesex","region_id":21}' https://0.0.0.0:443/regional/

        curl -k -i -H "Content-Type: application/json" -X DELETE -d '{"key":165,"fuel":"biomass","int_ind":27,"intensity":"low","perc":9,"region_desc":"Middlesex","region_id":21}' https://0.0.0.0:443/regional/

## Kubernetes Deployment
The steps to build the docker image and deploy application in kubernetes:
 1.  For private Docker images the docker image must be registered to the built in registry for it to function. Install registry with following command:
    
        sudo microk8s enable registry
 2.  Save the file cassandra-deployment.yaml in the current project directory 
    
        apiVersion: apps/v1
        kind: Deployment
        metadata:
            name: cassandra-deployment
            labels:
                app: Coursework
        spec:
            selector:
                matchLabels:
                    app: Coursework
        replicas: 3
        template:
            metadata:
                labels:
                    app: Coursework
            spec:
                containers:
                - name: coursework
                  image: localhost:32000/mycassandra:registry
                  ports:
                   - containerPort: 443
 3. Build the cassandra docker image and tag it to registry
 
        sudo docker build . -t localhost:32000/mycassandra:registry
 4. Push it to registry
 
        sudo docker push localhost:32000/mycassandra:registry
 5. Pushing to this insecure registry may fail in some versions of Docker unless the daemon is explicitly configured to trust this registry. 
   To address this we need to edit /etc/docker/daemon.json and add:
   
        {
            "insecure-registries" : ["localhost:32000"]
        }
    Note: Optional step to be done only if docker push has failed.
 6. The new configuration should be loaded with a Docker daemon restart
        
        sudo systemectl restart docker
 7. Now that we have restarted our docker daemon all the container instances would have stopped running. This means that the cassandra database docker container 'cassandra-coursework' 
   has stopped running. Re-start the same container instance using below command:
   
        sudo docker start cassandra-coursework
 
 8. Deploy the docker container image 'mycassandra:registry' present in the registry using the configured cassandra-deployment.yaml file:

        sudo microk8s.kubectl apply -f ./cassandra-deployment.yaml  
 9. Check the deployment status                
    
        sudo microk8s.kubectl get deployment
 10. Check the pods status
        
         sudo microk8s.kubectl get pods
 
 11. Create a service and expose the deployment to internet
 
         sudo microk8s kubectl expose deployment cassandra-deployment --type=LoadBalancer --port=443 --target-port=443
 12. Check the service status
    
        By default the kubernetes service allocates a port within range '30000-32767' for nodePort.
        
 The web app can be viewed in the browser using the public DNS of AWS EC2 account along with this Nodeport that starts with '30xxx'.
       
### Cleanup

   Delete the Kubernetes deployment and LoadBalancer service using below commands:

        sudo microk8s.kubectl delete deployment cassandra-deployment
   