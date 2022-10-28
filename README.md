

# 介绍

innodb_status 是用来分析`show engine innodb status`的. 支持mysql5.7/8.0. 支持标准输入.

目前 不会分析事务, 不会提供建议, 还不支持html和png输出.

TODO: trx and suggestion,html,png



# 使用

本工具支持直接连接mysql分析.

也支持其它工具连接mysql, 手动将`show engine innodb status`结果取出来交给本脚本分析.

## 直接连接数据库

```
python innodb_status.py -h 127.0.0.1 -P 3308 -u root -p 123456
```



## 使用其它工具连接数据库

使用mysql命令加管道符.

```
mysql -h127.0.0.1 -P 3308 -p123456 -e 'show engine innodb status' | python innodb_status.py
```

使用`-f`选项

```
mysql -h127.0.0.1 -P 3308 -p123456 -e 'show engine innodb status' > /tmp/innodb_status.txt
python innodb_status.py -f /tmp/innodb_status.txt
```

当然也可以管道符

```
cat /tmp/innodb_status.txt | python innodb_status.py
```





# 打包成可执行文件

只需将上诉的 `python innodb_status.py `修改为/PATH/innodb_status 即可

```
pyinstaller -F innodb_status.py
ls dist/innodb_status
cd dist
```

```
./innodb_status -h 127.0.0.1 -P 3308 -u root -p 123456
```





# 开发说明

innodb_status.py   前台交互接口(暂不支持web端操作)

innodb_status_tool.py  分析`show engine innodb status`结果

innodb_status_display.py  输出分析结果.



## innodb_status_tool

class innodb_status_collector 负责连接mysql,或者读取文件 来获取 `show engine innodb status`结果

class innodb_status_format 负责格式化上述结果, 输出dict格式

class innodb_status_suggestion 负责提供建议.(TODO)



## innodb_status_display

def simple 命令行控制台输出展示

def html 输出html格式结果(TODO)

def json 输出json格式结果

def png 输出png格式结果(TODO)



# BUG修复记录

| BUG详情 | 修复版本 | 修复时间 |
| ----- | ---- | ---- |
|       |      |      |
|       |      |      |
|       |      |      |



# 版本变更记录

| 版本   | 更新时间       | 更新说明                                     |
| ---- | ---------- | ---------------------------------------- |
| 0.1  | 2022.10.28 | 分析mysql的innodb status. <br />仅支持mysql5.7/8.0. <br />不支持建议提供. <br />不会分析事务和锁. <br />不支持html格式输出. |
|      |            |                                          |
|      |            |                                          |



# 使用样例

如下为 mysql 5.7 环境使用样例.

```
[root@ddcw21 innodb_status]# python innodb_status.py -h 127.0.0.1 -P 3308 -p 123456
说明:
采集时间: 2022-10-28 18:59:37
下面涉及到的 每秒平均值 计算时间均为最近 19 秒内

master线程:
系统繁忙程度(越大越繁忙): 0.012
日志写入和刷新次数: 33677

SEMAPHORES信号量:
rw_s_spin_wait_count 0
rw_s_spin_round_count 10383
rw_s_os_wait_count 474
rw_x_spin_wait_count 0
rw_x_spin_round_count 15764
rw_x_os_wait_count 319
rw_sx_spin_wait_count 213
rw_sx_spin_round_count 1345
rw_sx_os_wait_count 11
每次空转等待的锁: rw_s:10383.00  rw_x:15764.00 rw_sx:6.31

事务(含锁)
TODO

文件IO
Pending normal 异步IO READ (对应read thread) :  [0, 0, 0, 0]
Pending normal 异步IO WRITE(对应WRIET thread):  [0, 0, 0, 0]
挂起(pending)的redo log flush: 0
挂起(pending)的tablespace flush: 0
OS总读次数: 10675  速度: 0.11 次/秒.  平均每次读 16384 字节
OS总写次数: 306414  速度: 635.23 次/秒. 
OS总flush次数: 239334  速度: 593.07 次/秒. 

insert/change buffer和自适应hash索引
已合并页的数量: 1 页.   ibuf空闲列表长度: 275 页.  ibuf大小: 277 页.  合并插入次数: 1387
合并操作次数: insert buffer: 6339  delete buffer: 6390   purge buffer: 5769
无需合并操作的次数: insert buffer: 0  delete buffer: 0   purge buffer: 0
使用hash索引的查询 9203.36次/秒  未使用hash使用的查询 11864.17次/秒   自适应hash索引使用率43.69%

日志信息(redo)
最新产生的LSN: 13522154254
已刷盘的LSN: 13522153063
最老的LSN: 13500503412
最新检查点LSN: 13500450829
redo已完成的IO次数: 216975  速度:538.16次/秒

BUFFER POOL AND MEMORY(不含具体实例的,只含汇总的)
buffer pool 实例数(对应参数:innodb_buffer_pool_instances):  8
总内存: 1099431936 字节
系统(字典)使用: 183930 字节
buffer pool: 65528 页
free buffer: 53537 页
LRU        : 11480 页
old LRU    : 4387 页
脏页(flush list)            : 6923 页
等待读入的页(pending read)  : 0 页
等待的写(pending write) : LRU: 0 页.   flush_list(等待刷新的脏页): 0 页.   单页: 0 页
LRU made young(LRU中移动到前部的页数,就是经常使用的页) 14 页(速度:0.00/s),   non-young 0 页(速度:0.00/s)
从磁盘读取的页: 10637(0.00/s)   在内存中创建的页(无数据): 843(0.00/s)     写入磁盘的页: 85175(0.00/s)
缓存命中率:1000 / 1000
预读速度: 0.00/s   (因未被访问)驱除速度: 0.00/s   随机预读速度: 0.00/s

行操作ROW OPERATIONS
read view:  8
主进程ID: 3624 (sleeping)
插入行数: 253438(612.18/s)   更新行数: 502116(1214.30/s)   删除行数: 250977(606.86/s)   读行数: 104693576(252841.96/s)
```

