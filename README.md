# CS-512-SetSearch


## TODO (Mar.30 -- Apr. 7) 

1. Wenzhuang:
	* familiar with codes and data format
	* index the partial dataset with the same schema
	* familiar with the script codes in ElasticSearch
	
2. Jinfeng & Peifeng
	* Literature survey and writing
	* familiar with the interface codes


## Log into "server", and familiar with data

```
$ ssh -p 8822 cs512@128.174.244.6
```
The default password is *cs512*.

After you log in, the cd into default working directory

```
$ cd /home/jiaming/Desktop/SetSearch/
```

The full dataset will be in 

```
/home/jiaming/Desktop/SetSearch/data
```

The partial dataset (recent 5 million papers), and the codes for generating such partial dataset out of the full dataset, will be in 

```
/home/jiaming/Desktop/SetSearch/data/Results/
```



## src-elasticsearch:

这部分主要是用来ElasticSearch的codes。主要看下面的三个codes

1. /update_20170305/create_index_20170305.py
	* 着重看一下index的schema, 后面search的时候需要基于index schema来search
	
2. /update_20170305/index_data_20170305.py
	* 这部分code包括了data parsing以及bulk indexing

3. /search_data.py:
	* 主要需要修改的search codes在这个部分

## src-interface:

这部分包括我们网站interface的部分，基于Flask和React. 里面有更详细的readme


## references:

包括一个slides介绍我们的setsearch系统以及一个本elasticsearch的书。













