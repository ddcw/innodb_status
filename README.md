

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

| BUG详情                                    | 已修复版本 | 修复时间       | 报错                                       | MYSQL版本 |
| ---------------------------------------- | ----- | ---------- | ---------------------------------------- | ------- |
| 8.0中ROW OPERATIONS 中 state= 而5.7中是state: 的问题 | v0.2  | 2022.10.30 | re.compile(', Main thread ID=(.+), state:').findall(row_operations)[0].strip() | 8.0     |
| [死锁匹配出错](https://github.com/ddcw/innodb_status/issues/1) | v0.3  | 2022.11.15 | s1_info = re.compile('\*\*\* \(1\) TRANSACTION:(.+)\*\*\* \(1\) WAITING FOR THIS LOCK TO',re.S).findall(deadlock)[0].strip() IndexError: list index out of range | 未知      |
|                                          |       |            |                                          |         |



# 版本变更记录

| 版本   | 更新时间       | 更新说明                                     |
| ---- | ---------- | ---------------------------------------- |
| 0.1  | 2022.10.28 | 分析mysql的innodb status. <br />仅支持mysql5.7/8.0. <br />不支持建议提供. <br />不会分析事务和锁. <br />不支持html格式输出. |
| 0.2  | 2022.10.30 | 支持事务分析和死锁<br />系统繁忙程度定义更改: 原: srv_active/srv_idle 变更后: srv_active/(srv_activ+srv_idle)*100 |
| 0.3  | 2022.11.15 | 修复[已知问题1](https://github.com/ddcw/innodb_status/issues/1), 并直接显示回滚事务的事务ID<br />显示优化(总内存显示为GB格式.)<br />不再提供二进制文件, 需要的请自己使用pyinstaller打包. |
|      |            |                                          |



# 使用样例

如下为 mysql 8.0 环境使用样例.

```
说明:
采集时间: 2022-11-15 13:41:16
下面涉及到的 每秒平均值 计算时间均为最近 15 秒内

master线程:
系统繁忙程度(越大越繁忙): 0.1 %
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
产生死锁的时间: 2022-11-15 
事务ID:1347130  锁类型:X  thread_id:8  69 localhost 127.0.0.1 root updating SQL如下:
update t20221115 set name='123' where id=2


事务ID:1347129  锁类型:X  thread_id:9  70 localhost 127.0.0.1 root updating SQL如下:
update t20221115 set name='1' where id=1


回滚事务: 1347129

事务汇总信息
max_trx_id : 1347136
min_trx_id : 1347136
max_undo_id: 0
purge线程状态: running but idle
undo包含的事务数: 0
事务ID:1347130  事务状态:ACTIVE 4352 sec  锁:3  堆大小:1128  锁行数:2  事务中修改或插入的行数:2  MYSQL_PROCESS_ID:8

文件IO
Pending normal 异步IO READ (对应read thread) :  [0, 0, 0, 0, 0, 0, 0, 0]
Pending normal 异步IO WRITE(对应write thread):  [0, 0, 0, 0]
挂起(pending)的redo log flush: 0
挂起(pending)的tablespace flush: 0
OS总读次数: 1053  速度: 0.00 次/秒.  平均每次读 0 字节
OS总写次数: 492  速度: 0.00 次/秒. 
OS总flush次数: 204  速度: 0.00 次/秒. 

insert/change buffer和自适应hash索引
已合并页的数量: 1 页.   ibuf空闲列表长度: 324 页.  ibuf大小: 326 页.  合并插入次数: 0
合并操作次数: insert buffer: 0  delete buffer: 0   purge buffer: 0
无需合并操作的次数: insert buffer: 0  delete buffer: 0   purge buffer: 0
使用hash索引的查询 0.00次/秒  未使用hash使用的查询 0.00次/秒   自适应hash索引使用率0.0%

日志信息(redo)
最新产生的LSN: 4075080066
已刷盘的LSN: 4075080066
最老的LSN: 4075080066
最新检查点LSN: 4075080066
redo已完成的IO次数: 100  速度:0.00次/秒

BUFFER POOL AND MEMORY(不含具体实例的,只含汇总的)
总内存: 0 字节  (0.0 GB)
系统(字典)使用: 518237 字节
buffer pool: 8192 页
free buffer: 7014 页
LRU        : 1172 页
old LRU    : 451 页
脏页(flush list)            : 0 页
等待读入的页(pending read)  : 0 页
等待的写(pending write) : LRU: 0 页.   flush_list(等待刷新的脏页): 0 页.   单页: 0 页
LRU made young(LRU中移动到前部的页数,就是经常使用的页) 0 页(速度:0.00/s),   non-young 0 页(速度:0.00/s)
从磁盘读取的页: 1025(0.00/s)   在内存中创建的页(无数据): 147(0.00/s)     写入磁盘的页: 278(0.00/s)
缓存命中率:数据库太闲,无此数据.
预读速度: 0.00/s   (因未被访问)驱除速度: 0.00/s   随机预读速度: 0.00/s

行操作ROW OPERATIONS
read view:  0
主进程ID: 4186 (sleeping)
插入行数: 2(0.00/s)   更新行数: 1(0.00/s)   删除行数: 2(0.00/s)   读行数: 9(0.00/s)

```

