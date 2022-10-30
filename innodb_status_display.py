class display:
	def __init__(self,*args,**kwargs):
		self.innodb_status_dict = kwargs['innodb_status_dict']
		self.suggestion = kwargs['suggestion'] if 'suggestion' in kwargs else []

	def simple(self):
		#print(self.innodb_status_dict)
		print("说明:")
		print("采集时间:",self.innodb_status_dict['date'])
		print("下面涉及到的 每秒平均值 计算时间均为最近 {t} 秒内".format(t=self.innodb_status_dict['valid_time']))
		print("")

		print("master线程:")
		print("系统繁忙程度(越大越繁忙): {t} %".format(t=round(int(self.innodb_status_dict['background_thread']['srv_active'])/(int(self.innodb_status_dict['background_thread']['srv_idle'])+int(self.innodb_status_dict['background_thread']['srv_active']))*100,2)))
		print("日志写入和刷新次数:",self.innodb_status_dict['background_thread']['log_flush_and_writes'])
		print("")

		print("SEMAPHORES信号量:")
		#Print info about the sync array(s) TODO
		#Prints wait info of the sync system
		print('rw_s_spin_wait_count',self.innodb_status_dict['semaphores']['rw_shared_spins']) #number of spin waits on rw-latches,resulted during shared (read) locks
		print('rw_s_spin_round_count',self.innodb_status_dict['semaphores']['rw_shared_rounds']) #number of spin loop rounds on rw-latches resulted during shared (read) locks
		print('rw_s_os_wait_count',self.innodb_status_dict['semaphores']['rw_shared_os_waits']) #number of OS waits on rw-latches, resulted during shared (read) locks
		print('rw_x_spin_wait_count',self.innodb_status_dict['semaphores']['rw_excl_spins'])
		print('rw_x_spin_round_count',self.innodb_status_dict['semaphores']['rw_excl_rounds'])
		print('rw_x_os_wait_count',self.innodb_status_dict['semaphores']['rw_excl_os_waits'])
		print('rw_sx_spin_wait_count',self.innodb_status_dict['semaphores']['rw_sx_spins'])
		print('rw_sx_spin_round_count',self.innodb_status_dict['semaphores']['rw_sx_rounds'])
		print('rw_sx_os_wait_count',self.innodb_status_dict['semaphores']['rw_sx_os_waits'])

		print('每次空转等待的锁: rw_s:{rw_s}  rw_x:{rw_x} rw_sx:{rw_sx}'.format(rw_s=self.innodb_status_dict['semaphores']['spin_rounds_per_wait_rw_s'],rw_x=self.innodb_status_dict['semaphores']['spin_rounds_per_wait_rw_x'], rw_sx=self.innodb_status_dict['semaphores']['spin_rounds_per_wait_rw_sx']))
		print("")


		if self.innodb_status_dict['dead_lock']['rollback_trx'] is not None:
			print("死锁(最近一条)") #回滚产生死锁的事务. 就是 执行哪条sql会产生死锁, 就回滚那条SQL所在的事务.(对于show engine innodb 来说永远是session 2)
			print('事务1:     事务ID:{trx_id}  connection_id:{thread_id}  连接信息:{user} \n事务1的SQL: {sql}'.format(trx_id=self.innodb_status_dict['dead_lock']['s1']['trx_id'], thread_id=self.innodb_status_dict['dead_lock']['s1']['thread_id'], user=self.innodb_status_dict['dead_lock']['s1']['user'], sql=self.innodb_status_dict['dead_lock']['s1']['sql']))
			print('事务2:     事务ID:{trx_id}  connection_id:{thread_id}  连接信息:{user} \n事务1的SQL: {sql}'.format(trx_id=self.innodb_status_dict['dead_lock']['s2']['trx_id'], thread_id=self.innodb_status_dict['dead_lock']['s2']['thread_id'], user=self.innodb_status_dict['dead_lock']['s2']['user'], sql=self.innodb_status_dict['dead_lock']['s2']['sql']))
			print("回滚事务: {trx}".format(trx=self.innodb_status_dict['dead_lock']['rollback_trx']))
			#print(self.innodb_status_dict['dead_lock'])
		else:
			print("无死锁信息")

		print("")
		print("事务汇总信息")
		print("max_trx_id :",self.innodb_status_dict['transactions']['sumary']['max_trx_id'])
		print("min_trx_id :",self.innodb_status_dict['transactions']['sumary']['min_trx_id'])
		print("max_undo_id:",self.innodb_status_dict['transactions']['sumary']['max_undo_id'])
		print("purge线程状态:",self.innodb_status_dict['transactions']['sumary']['purge_state'])
		print('undo包含的事务数:',self.innodb_status_dict['transactions']['sumary']['history_list_length_for_undo'])
		for x in self.innodb_status_dict['transactions']['trx_list']:
			if x['trx_state'] != 'not started':
				print('事务ID:{trx_id}  事务状态:{trx_state}  锁:{n_lock}  堆大小:{heap_size}  锁行数:{row_locks}  事务中修改或插入的行数:{undo_no}  MYSQL_PROCESS_ID:{thread_id}'.format(trx_id=x['trx_id'],trx_state=x['trx_state'], n_lock=x['n_locks'], heap_size=x['heap_size'], row_locks=x['row_locks'], undo_no=x['undo_no'], thread_id=x['thread_id']))

		print("")
		print("文件IO")
		print("Pending normal 异步IO READ (对应read thread) : ",self.innodb_status_dict['file_io']['pending_normal_aio_reads'] )
		print("Pending normal 异步IO WRITE(对应WRIET thread): ",self.innodb_status_dict['file_io']['pending_normal_aio_writes'] )
		#insert buffer TODO
		print('挂起(pending)的redo log flush:',self.innodb_status_dict['file_io']['pending_flushes_log'])
		print('挂起(pending)的tablespace flush:',self.innodb_status_dict['file_io']['buffer_pool'])
		print('OS总读次数: {r}  速度: {rp} 次/秒.  平均每次读 {rpb} 字节'.format(r=self.innodb_status_dict['file_io']['os_file_reads'],rp=self.innodb_status_dict['file_io']['reads'],rpb=self.innodb_status_dict['file_io']['avg_bytes_per_read']))
		print('OS总写次数: {w}  速度: {wp} 次/秒. '.format(w=self.innodb_status_dict['file_io']['os_file_writes'], wp=self.innodb_status_dict['file_io']['writes']))
		print('OS总flush次数: {flush}  速度: {flushp} 次/秒. '.format(flush=self.innodb_status_dict['file_io']['os_fsyncs'], flushp=self.innodb_status_dict['file_io']['fsyncs']))
		print("")

		#insert buffer内存结构: struct ibuf_t
		print("insert/change buffer和自适应hash索引")
		print("已合并页的数量: {s} 页.   ibuf空闲列表长度: {f} 页.  ibuf大小: {ibuf_szie} 页.  合并插入次数: {merge}".format(s=self.innodb_status_dict['insert_buffer_and_adaptive_hash_index']['ibuf_size'],f=self.innodb_status_dict['insert_buffer_and_adaptive_hash_index']['ibuf_free_list_len'],ibuf_szie=self.innodb_status_dict['insert_buffer_and_adaptive_hash_index']['ibuf_seg_size'],merge=self.innodb_status_dict['insert_buffer_and_adaptive_hash_index']['ibuf_merges'])) #size:current size of the ibuf index
		print("合并操作次数: insert buffer: {ib}  delete buffer: {db}   purge buffer: {pb}".format(ib=self.innodb_status_dict['insert_buffer_and_adaptive_hash_index']['merged_operations_insert'], db=self.innodb_status_dict['insert_buffer_and_adaptive_hash_index']['merged_operations_delete_mark'], pb=self.innodb_status_dict['insert_buffer_and_adaptive_hash_index']['merged_operations_delete'])) #delete mark 只是标记删除,使用delete buffer,  delete才是真正的删除,使用purge buffer
		print("无需合并操作的次数: insert buffer: {ib}  delete buffer: {db}   purge buffer: {pb}".format(ib=self.innodb_status_dict['insert_buffer_and_adaptive_hash_index']['discarded_operations_insert'], db=self.innodb_status_dict['insert_buffer_and_adaptive_hash_index']['discarded_operations_delete_mark'], pb=self.innodb_status_dict['insert_buffer_and_adaptive_hash_index']['discarded_operations_delete'])) #表示合并之前,该数据就已经被删了
		print("使用hash索引的查询 {h}次/秒  未使用hash使用的查询 {nh}次/秒   自适应hash索引使用率{hp}%".format(h=self.innodb_status_dict['insert_buffer_and_adaptive_hash_index']['hash_searche_per_second'],nh=self.innodb_status_dict['insert_buffer_and_adaptive_hash_index']['non_hash_searche_per_second'],hp=round(float(self.innodb_status_dict['insert_buffer_and_adaptive_hash_index']['hash_searche_per_second'])/(float(self.innodb_status_dict['insert_buffer_and_adaptive_hash_index']['hash_searche_per_second'])+float(self.innodb_status_dict['insert_buffer_and_adaptive_hash_index']['non_hash_searche_per_second'])+0.00001)*100,2))) #防止除数为0的情况 加了个0.00001
		print("")	


		print("日志信息(redo)")
		print("最新产生的LSN:",self.innodb_status_dict['log']['log_sequence_number'])
		print("已刷盘的LSN:",self.innodb_status_dict['log']['log_flushed_up_to'])
		print("最老的LSN:",self.innodb_status_dict['log']['pages_flushed_up_to'])
		print("最新检查点LSN:",self.innodb_status_dict['log']['last_checkpoint_at'])
		print("redo已完成的IO次数: {io}  速度:{iop}次/秒".format(io=self.innodb_status_dict['log']['log_io_done'],iop=self.innodb_status_dict['log']['log_io_per_second']))
		print("")
		

		print("BUFFER POOL AND MEMORY(不含具体实例的,只含汇总的)")
		instance_count = len(self.innodb_status_dict['buffer_pool_and_memory']['buffer_pool_info_detail'])
		if instance_count > 0:
			print("buffer pool 实例数(对应参数:innodb_buffer_pool_instances): ",instance_count)
		print("总内存: {total} 字节".format(total=self.innodb_status_dict['buffer_pool_and_memory']['buffer_pool_info_total']['total_large_memory_allocated']))
		print("系统(字典)使用: {sysmem} 字节".format(sysmem=self.innodb_status_dict['buffer_pool_and_memory']['buffer_pool_info_total']['dictionary_memory_allocated']))
		print("buffer pool: {s} 页".format(s=self.innodb_status_dict['buffer_pool_and_memory']['buffer_pool_info_total']['instance']['buffer_pool_size']))
		print("free buffer: {s} 页".format(s=self.innodb_status_dict['buffer_pool_and_memory']['buffer_pool_info_total']['instance']['free_buffers']))
		print("LRU        : {s} 页".format(s=self.innodb_status_dict['buffer_pool_and_memory']['buffer_pool_info_total']['instance']['database_pages']))
		print("old LRU    : {s} 页".format(s=self.innodb_status_dict['buffer_pool_and_memory']['buffer_pool_info_total']['instance']['old_database_pages']))
		print("脏页(flush list)            : {s} 页".format(s=self.innodb_status_dict['buffer_pool_and_memory']['buffer_pool_info_total']['instance']['modified_db_pages']))
		print("等待读入的页(pending read)  : {s} 页".format(s=self.innodb_status_dict['buffer_pool_and_memory']['buffer_pool_info_total']['instance']['pending_reads']))
		print("等待的写(pending write) : LRU: {lru} 页.   flush_list(等待刷新的脏页): {f} 页.   单页: {s} 页".format(lru=self.innodb_status_dict['buffer_pool_and_memory']['buffer_pool_info_total']['instance']['pending_writes_lru'], f=self.innodb_status_dict['buffer_pool_and_memory']['buffer_pool_info_total']['instance']['pending_writes_flush_list'], s=self.innodb_status_dict['buffer_pool_and_memory']['buffer_pool_info_total']['instance']['pending_writes_single_page']))
		print("LRU made young(LRU中移动到前部的页数,就是经常使用的页) {y} 页(速度:{yp}/s),   non-young {ny} 页(速度:{nyp}/s)".format(y=self.innodb_status_dict['buffer_pool_and_memory']['buffer_pool_info_total']['instance']['pages_made_young'], ny=self.innodb_status_dict['buffer_pool_and_memory']['buffer_pool_info_total']['instance']['pages_made_not_young'],yp=self.innodb_status_dict['buffer_pool_and_memory']['buffer_pool_info_total']['instance']['pages_made_youngs_per_second'], nyp=self.innodb_status_dict['buffer_pool_and_memory']['buffer_pool_info_total']['instance']['pages_made_non_youngs_per_second']))
		print("从磁盘读取的页: {r}({rp}/s)   在内存中创建的页(无数据): {c}({cp}/s)     写入磁盘的页: {w}({wp}/s)".format(r=self.innodb_status_dict['buffer_pool_and_memory']['buffer_pool_info_total']['instance']['pages_read'], rp=self.innodb_status_dict['buffer_pool_and_memory']['buffer_pool_info_total']['instance']['pages_read_per_second'], c=self.innodb_status_dict['buffer_pool_and_memory']['buffer_pool_info_total']['instance']['pages_created'],cp=self.innodb_status_dict['buffer_pool_and_memory']['buffer_pool_info_total']['instance']['pages_create_per_second'], w=self.innodb_status_dict['buffer_pool_and_memory']['buffer_pool_info_total']['instance']['pages_written'],wp=self.innodb_status_dict['buffer_pool_and_memory']['buffer_pool_info_total']['instance']['pages_written_per_second']))
		print("缓存命中率:{bhr}".format(bhr=self.innodb_status_dict['buffer_pool_and_memory']['buffer_pool_info_total']['instance']['buffer_pool_hit_rate']))
		print("预读速度: {rap}   (因未被访问)驱除速度: {evp}   随机预读速度: {rrap}".format(rap=self.innodb_status_dict['buffer_pool_and_memory']['buffer_pool_info_total']['instance']['pages_read_ahead'], evp=self.innodb_status_dict['buffer_pool_and_memory']['buffer_pool_info_total']['instance']['pages_evicted_without_access'], rrap=self.innodb_status_dict['buffer_pool_and_memory']['buffer_pool_info_total']['instance']['pages_random_read_ahead']))
		print("")

		print("行操作ROW OPERATIONS")
		print("read view: ",self.innodb_status_dict['row_operations']['read_views_open_inside_innodb'])
		print("主进程ID: {pid} ({stat})".format(pid=self.innodb_status_dict['row_operations']['process_id'], stat=self.innodb_status_dict['row_operations']['state']))
		print("插入行数: {i}({ip}/s)   更新行数: {u}({up}/s)   删除行数: {d}({dp}/s)   读行数: {r}({rp}/s)".format(i=self.innodb_status_dict['row_operations']['number_of_rows_inserted'], ip=self.innodb_status_dict['row_operations']['insert_per_second'], u=self.innodb_status_dict['row_operations']['number_of_rows_updated'], up=self.innodb_status_dict['row_operations']['update_per_second'], d=self.innodb_status_dict['row_operations']['number_of_rows_deteled'], dp=self.innodb_status_dict['row_operations']['delete_per_second'], r=self.innodb_status_dict['row_operations']['number_of_rows_read'], rp=self.innodb_status_dict['row_operations']['read_per_second']))

		print("")
		if self.suggestion is not None:
			print("建议如下:")
			for x in self.suggestion:
				print(x)
			print("")

	def html(self):
		print("to be continued...")

	def json(self):
		print(self.innodb_status_dict)

	def png(self):
		print("难度较大,以后再说.")
