# 基于ElasticSearch的实体，属性查询系统
本项目使用ElasticSearch (ES) 7.14.0 在wikidata dump (2020)上创建倒排索引模糊匹配相应的实体和属性。在评分方面，使用tf-idf在
描述文本中对实体和属性进行评分。实体和属性存储在./data/下，logstash 7.14.0负责导入实体和属性，建立索引，之后实时监测和更新。

## 安装启动ElasticSearch服务
使用docker-compose安装ES和可视化工具kibana,端口配置在docker-compose.yml中，docker 版本20.10.16。
```shell
cd ./qwikidata
docker-compose up -d
```

## 安装启动logstash服务
成功启动ES后，去logstash官网下载与ES相同版本的logstash 7.14.0放到目录下。运行以下命令导入多个csv,注意每个线程监控一个csv使用独立路径，合并导致数据混乱
创建索引的时间开销随csv大小增加。
```shell
cp ./logstash_confs/* ./logstash-7.14.0
cd logstash-7.14.0
mkdir entity entityalias property propertyalias
./bin/logstash -f item.conf --path.data=./entity
./bin/logstash -f item_aliases.conf --path.data=./entityalias
./bin/logstash -f property.conf --path.data=./property
./bin/logstash -f property_aliases.conf --path.data=./propertyalias
```
ES不区分索引的大小写，不可以有特殊字符，注意删除索引要彻底删除相应的路径。通过如下指令查到索引，健康状态为yellow表示备份文件与原始文件在相同节点，可以采用分布式查询解决。
```
http://localhost:9200/_cat/indices?v
```
## Web API接口
```shell
cd src
python esApp.py
curl --keepalive-time 5 -i http://127.0.0.1:5000/search/head-coach # YOUR QUERY HERE 空格用连字符代替
```