

# 介绍

innodb_status 是用来分析`show engine innodb status`的. 支持mysql5.7/8.0. 支持标准输入.

目前 不会提供建议, 不支持html输出格式

TODO: html



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

| BUG详情                                    | 已修复版本 | 修复时间       | 报错                                       |
| ---------------------------------------- | ----- | ---------- | ---------------------------------------- |
| 8.0中ROW OPERATIONS 中 state= 而5.7中是state: 的问题 | v0.2  | 2022.10.30 | re.compile(', Main thread ID=(.+), state:').findall(row_operations)[0].strip() |
|                                          |       |            |                                          |
|                                          |       |            |                                          |



# 版本变更记录

| 版本   | 更新时间       | 更新说明                                     |
| ---- | ---------- | ---------------------------------------- |
| 0.1  | 2022.10.28 | 分析mysql的innodb status. <br />仅支持mysql5.7/8.0. <br />不支持建议提供. <br />不会分析事务和锁. <br />不支持html格式输出. |
| 0.2  | 2022.10.30 | 支持事务分析和死锁<br />系统繁忙程度定义更改: 原: srv_active/srv_idle 变更后: srv_active/(srv_activ+srv_idle)*100 |
|      |            |                                          |



# 使用样例

如下为 mysql 8.0 环境使用样例.

```
[root@ddcw21 innodb_status]#python innodb_status.py -h 127.0.0.1 -P3314 -p123456  
说明:
采集时间: 2022-10-30 18:50:31
下面涉及到的 每秒平均值 计算时间均为最近 10 秒内

master线程:
系统繁忙程度(越大越繁忙): 0.99 %
日志写入和刷新次数: 0

SEMAPHORES信号量:
rw_s_spin_wait_count 0
rw_s_spin_round_count 0
rw_s_os_wait_count 0
rw_x_spin_wait_count 0
rw_x_spin_round_count 0
rw_x_os_wait_count 0
rw_sx_spin_wait_count 0
rw_sx_spin_round_count 0
rw_sx_os_wait_count 0
每次空转等待的锁: rw_s:0.00  rw_x:0.00 rw_sx:0.00

死锁(最近一条)
事务1:     事务ID:623011  connection_id:37  连接信息: localhost 127.0.0.1 root updating 
事务1的SQL: update t2022 set name='s1' where id=2
事务2:     事务ID:623010  connection_id:38  连接信息: localhost 127.0.0.1 root updating 
事务1的SQL: update t2022 set name='s1' where id=1
回滚事务: 2

事务汇总信息
max_trx_id : 722728
min_trx_id : 722711
max_undo_id: 0
purge线程状态: running but idle
undo包含的事务数: 373
事务ID:722726  事务状态:ACTIVE (PREPARED) 0 sec  锁:6  堆大小:1128  锁行数:3  事务中修改或插入的行数:4  MYSQL_PROCESS_ID:74
事务ID:722725  事务状态:ACTIVE (PREPARED) 0 sec  锁:6  堆大小:1128  锁行数:3  事务中修改或插入的行数:4  MYSQL_PROCESS_ID:81
事务ID:722721  事务状态:ACTIVE (PREPARED) 0 sec  锁:6  堆大小:1128  锁行数:3  事务中修改或插入的行数:4  MYSQL_PROCESS_ID:76

文件IO
Pending normal 异步IO READ (对应read thread) :  [0, 0, 0, 0, 0, 0, 0, 0]
Pending normal 异步IO WRITE(对应WRIET thread):  [0, 0, 0, 0]
挂起(pending)的redo log flush: 0
挂起(pending)的tablespace flush: 18446744073709551615
OS总读次数: 110904  速度: 607.22 次/秒.  平均每次读 16384 字节
OS总写次数: 2069284  速度: 13879.56 次/秒. 
OS总flush次数: 492921  速度: 3065.85 次/秒. 

insert/change buffer和自适应hash索引
已合并页的数量: 4 页.   ibuf空闲列表长度: 321 页.  ibuf大小: 326 页.  合并插入次数: 34317
合并操作次数: insert buffer: 22372  delete buffer: 42949   purge buffer: 24266
无需合并操作的次数: insert buffer: 0  delete buffer: 0   purge buffer: 0
使用hash索引的查询 23722.93次/秒  未使用hash使用的查询 21353.26次/秒   自适应hash索引使用率52.63%

日志信息(redo)
最新产生的LSN: 3538249320
已刷盘的LSN: 3538249320
最老的LSN: 3523077060
最新检查点LSN: 3523077060
redo已完成的IO次数: 1869841  速度:12831.80次/秒

BUFFER POOL AND MEMORY(不含具体实例的,只含汇总的)
总内存: 0 字节
系统(字典)使用: 513567 字节
buffer pool: 8192 页
free buffer: 466 页
LRU        : 7312 页
old LRU    : 2680 页
脏页(flush list)            : 3952 页
等待读入的页(pending read)  : 0 页
等待的写(pending write) : LRU: 0 页.   flush_list(等待刷新的脏页): 0 页.   单页: 0 页
LRU made young(LRU中移动到前部的页数,就是经常使用的页) 204296 页(速度:1266.04/s),   non-young 522516 页(速度:3023.38/s)
从磁盘读取的页: 110856(607.22/s)   在内存中创建的页(无数据): 3541(22.92/s)     写入磁盘的页: 159355(916.13/s)
缓存命中率:998 / 1000
预读速度: 0.00/s   (因未被访问)驱除速度: 0.00/s   随机预读速度: 0.00/s

行操作ROW OPERATIONS
read view:  8
主进程ID: 3589 (sleeping)
插入行数: 201329(1277.57/s)   更新行数: 402658(2554.94/s)   删除行数: 201330(1277.57/s)   读行数: 83955466(532727.33/s)
```

