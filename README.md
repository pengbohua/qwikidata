# **ElasticSearch** based entity linking system
This project uses ElasticSearch (ES) 7.14.0 to create inverted indexes for fuzzy matching of corresponding entities and properties in the wikidata dump (2020). We use tf-idf to score entities and properties with their context. Entities and properties are stored in ./data/, and we use logstash 7.14.0 to import entities and properties, monitoring and updating them in real time.

## Install and start ElasticSearch
Install ES and visualization tool Kibana with docker-compose, where configuration is stored in docker-compose.yml.
```shell
cd ./qwikidata
docker-compose up -d
```

## Install and start logstash
After successfully starting ES, download Logstash 7.14.0 with the same version as ES from the official website and put it in the directory. Run the following command to import multiple CSV files. Note that each thread monitors a CSV file using an independent path. Merging them will cause failure. The time expense of creating an index increases with the size of the CSV file.
```shell
cp ./logstash_confs/* ./logstash-7.14.0
cd logstash-7.14.0
mkdir entity entityalias property propertyalias
./bin/logstash -f item.conf --path.data=./entity
./bin/logstash -f item_aliases.conf --path.data=./entityalias
./bin/logstash -f property.conf --path.data=./property
./bin/logstash -f property_aliases.conf --path.data=./propertyalias
```
When it comes to indexing, ES is case-insensitive. Please note that when deleting an index, you should completely delete the corresponding path. You can use the following command to find the index, and if the health status is yellow, it means that the backup file is on the same node as the original file, and distributed queries can be used to solve this.
```
http://localhost:9200/_cat/indices?v
```
## Web API
```shell
cd src
python esApp.py
curl --keepalive-time 5 -i http://127.0.0.1:5000/search/property/head-coach # query here, and replace space with -
curl --keepalive-time 5 -i http://127.0.0.1:5000/search/entity/Beijing
```
