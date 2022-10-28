import pymysql
import re
class innodb_status_collector:
	def __init__(self,*args,**kwargs):
		self.innodb_status_str = ""
		self.status = False
		if 'file' in kwargs:
			#print("解析文件:",kwargs['file'])
			try:
				with open(kwargs['file'], 'r', encoding="utf-8") as f:
					self.innodb_status_str= f.readline()
					#避免第一行为表头信息
					if len(self.innodb_status_str) < 50:
						self.innodb_status_str= f.readline()
				self.status = True
			except Exception as e:
				print(e)
				self.status = False
		else:
			#print("连接mysql, 并获取innodb status信息")
			try:
				conn = pymysql.connect(
				host=kwargs['host'] if 'host' in kwargs else None,
				port=kwargs['port'] if 'port' in kwargs else None,
				user=kwargs['user'] if 'user' in kwargs else None,
				password=kwargs['password'] if 'password' in kwargs else None,
				unix_socket=kwargs['socket'] if 'socket' in kwargs else None,
				)
				cursor = conn.cursor()
				cursor.execute("show engine innodb status")
				self.innodb_status_str = cursor.fetchall()[0][2]
				self.status = True
			except Exception as e:
				print(e)
				self.status = False

	
	def is_ok(self):
		return self.status

	def get_innodb_status_str(self):
		return self.innodb_status_str

class innodb_status_format:
	def __init__(self,innodb_status_str):
		self.innodb_status_str = innodb_status_str.replace('\\n','\n') #兼容  xxx.txt
		self.innodb_status_dict = {}
		#self.innodb_status_dict['date'] = re.compile('=====================================[\n](.+)INNODB MONITOR OUTPUT[\n]=====================================[\n]Per second averages calculated from').findall(self.innodb_status_str)
		try:
			self.innodb_status_dict['date'] = re.compile('=====================================[\n](.+)0x').findall(self.innodb_status_str)[0].strip()
		except:
			tmp_str = re.compile('=====================================[\n](.+)').findall(self.innodb_status_str)[0].strip()
			self.innodb_status_dict['date'] = tmp_str.split()[0] + " " + tmp_str.split()[1] 
		self.innodb_status_dict['valid_time'] = re.compile('Per second averages calculated from the last(.+)seconds').findall(self.innodb_status_str)[0].strip()

	def get_innodb_status_dict(self):
		return self.innodb_status_dict

	def set_file_io(self):
		#storage/innobase/srv/srv0srv.cc os_aio_print
		file_io_pattern = re.compile('FILE I/O[\n]--------[\n](.+)-------------------------------------[\n]INSERT BUFFER AND ADAPTIVE HASH INDEX',re.S) #re.S表示 . 能匹配 \n
		file_io = file_io_pattern.findall(self.innodb_status_str)[0]
		insert_buffer_thread_pattern = re.compile("state:(.+)\(insert buffer thread\)")

		insert_buffer_thread = insert_buffer_thread_pattern.findall(file_io)
		read_thread = re.compile("state:(.+)\(read thread\)").findall(file_io)
		write_thread = re.compile("state:(.+)\(write thread\)").findall(file_io)
		log_thread = re.compile("state:(.+)\(log thread\)").findall(file_io)

		
		pending_normal_aio_reads = re.compile("Pending normal aio reads:(.+), aio writes:").findall(file_io)[0].strip()
		pending_normal_aio_writes = re.compile(", aio writes:(.+),").findall(file_io)[0].strip()
		ibuf_aio_reads = re.compile("ibuf aio reads:(.+), log i/o's:").findall(file_io)
		log_io_per_second = re.compile("log i/o's:(.+), sync i/o's:").findall(file_io)
		sync_io_per_second = re.compile(", sync i/o's:(.+)").findall(file_io)

		pending_flushes_log = re.compile("Pending flushes \(fsync\) log:(.+); buffer pool:").findall(file_io)[0].strip()
		buffer_pool = re.compile("; buffer pool:(.+)").findall(file_io)[0].strip()

		os_file_reads = re.compile("[\n](.+)OS file reads,").findall(file_io)[0].strip()
		os_file_writes = re.compile("OS file reads,(.+)OS file writes,").findall(file_io)[0].strip()
		os_fsyncs = re.compile("OS file writes,(.+)OS fsyncs").findall(file_io)[0].strip()

		#TODO pending preads
		
		reads = re.compile("(.+)reads/s,").findall(file_io)[0].strip()
		writes = re.compile("read,(.+)writes/s,").findall(file_io)[0].strip()
		fsyncs = re.compile("writes/s,(.+)fsyncs/s").findall(file_io)[0].strip()
		avg_bytes_per_read = re.compile(",(.+)avg bytes/read,").findall(file_io)[0].strip()

		

		self.innodb_status_dict['file_io'] = {
			'insert_buffer_thread':insert_buffer_thread,
			'read_thread':read_thread,
			'write_thread':write_thread,
			'log_thread':log_thread,

			'pending_normal_aio_reads':pending_normal_aio_reads,
			'pending_normal_aio_writes':pending_normal_aio_writes,
			'ibuf_aio_reads':ibuf_aio_reads,
			'log_io_per_second':log_io_per_second,
			'sync_io_per_second':sync_io_per_second,

			'pending_flushes_log':pending_flushes_log,
			'buffer_pool':buffer_pool,

			'os_file_reads':os_file_reads,
			'os_file_writes':os_file_writes,
			'os_fsyncs':os_fsyncs,

			'reads':reads,
			'writes':writes,
			'fsyncs':fsyncs,
			'avg_bytes_per_read':avg_bytes_per_read,
		}
		

	def set_background_thread(self,):
		background_thread = re.compile('BACKGROUND THREAD[\n]-----------------[\n](.+)[\n]----------[\n]SEMAPHORES',re.S).findall(self.innodb_status_str)[0]
		srv_active = re.compile(":(.+)srv_active").findall(background_thread)[0].strip()
		srv_shutdown = re.compile("srv_active,(.+)srv_shutdown").findall(background_thread)[0].strip()
		srv_idle = re.compile("srv_shutdown,(.+)srv_idle").findall(background_thread)[0].strip()
		log_flush_and_writes = re.compile("log flush and writes:(.+)").findall(background_thread)[0].strip()
		self.innodb_status_dict['background_thread'] = {
			'srv_active':srv_active,
			'srv_shutdown':srv_shutdown,
			'srv_idle':srv_idle,
			'log_flush_and_writes':log_flush_and_writes,
		}
		

	def set_semaphores(self,):
		#storage/innobase/srv/srv0srv.cc sync_array_print sync_print_wait_info
		semaphores = re.compile('SEMAPHORES[\n]----------[\n](.+)[\n]------------[\n]TRANSACTIONS',re.S).findall(self.innodb_status_str)[0]
		self.innodb_status_dict['semaphores'] = {
			'os_wait_array_info_reservation_count' : re.compile("OS WAIT ARRAY INFO: reservation count(.+)").findall(semaphores)[0].strip(),
			'os_wait_array_info_signal_count' : re.compile("OS WAIT ARRAY INFO: signal count(.+)").findall(semaphores)[0].strip(),

			'rw_shared_spins' : re.compile("RW-shared spins(.+), rounds").findall(semaphores)[0].strip(),
			'rw_shared_rounds' : re.compile("RW-shared spins.+rounds(.+), OS waits").findall(semaphores)[0].strip(),
			'rw_shared_os_waits' : re.compile("RW-shared spins.+OS waits(.+)").findall(semaphores)[0].strip(),
			
			'rw_excl_spins' : re.compile("RW-excl spins(.+), rounds").findall(semaphores)[0].strip(),
			'rw_excl_rounds' : re.compile("RW-excl spins.+rounds(.+), OS waits").findall(semaphores)[0].strip(),
			'rw_excl_os_waits' : re.compile("RW-excl spins.+OS waits(.+)").findall(semaphores)[0].strip(),
			
			'rw_sx_spins' : re.compile("RW-sx spins(.+), rounds").findall(semaphores)[0].strip(),
			'rw_sx_rounds' : re.compile("RW-sx spins.+rounds(.+), OS waits").findall(semaphores)[0].strip(),
			'rw_sx_os_waits' : re.compile("RW-sx spins.+OS waits(.+)").findall(semaphores)[0].strip(),
			
			'spin_rounds_per_wait_rw_s' : re.compile("Spin rounds per wait:(.+)RW-shared,").findall(semaphores)[0].strip(),
			'spin_rounds_per_wait_rw_x' : re.compile("RW-shared,(.+)RW-excl,").findall(semaphores)[0].strip(),
			'spin_rounds_per_wait_rw_sx' : re.compile("RW-excl,(.+)RW-sx").findall(semaphores)[0].strip(),
		}

	#TODO LATEST FOREIGN KEY ERROR
	def set_latest_foreign_key_error(self,):
		return

	def set_transactions(self,):
		#TODO
		#storage/innobase/srv/srv0srv.cc lock_print_info_summary   lock_print_info_all_transactions lock_trx_print_locks trx_print_low 涉及函数太多... 慢慢完善...
		transactions = re.compile('TRANSACTIONS[\n]------------[\n](.+)[\n]--------[\n]FILE I/O',re.S).findall(self.innodb_status_str)[0]
		self.innodb_status_dict['transactions'] = {}

	def set_insert_buffer_and_adaptive_hash_index(self,):
		#ibuf_print ha_print_info
		insert_buffer_and_adaptive_hash_index = re.compile('INSERT BUFFER AND ADAPTIVE HASH INDEX[\n]-------------------------------------[\n](.+)[\n]---[\n]LOG',re.S).findall(self.innodb_status_str)[0]
		self.innodb_status_dict['insert_buffer_and_adaptive_hash_index'] = {
			'ibuf_size' : re.compile("Ibuf: size(.+), free list len").findall(insert_buffer_and_adaptive_hash_index)[0].strip(),
			'ibuf_free_list_len' : re.compile(", free list len(.+), seg size").findall(insert_buffer_and_adaptive_hash_index)[0].strip(),
			'ibuf_seg_size' : re.compile(", seg size(.+),.+merges").findall(insert_buffer_and_adaptive_hash_index)[0].strip(),
			'ibuf_merges' : re.compile(".+,(.+)merges").findall(insert_buffer_and_adaptive_hash_index)[0].strip(),

			'merged_operations_insert' : re.compile("merged operations:.+insert(.+), delete mark.+discarded operations",re.S).findall(insert_buffer_and_adaptive_hash_index)[0].strip(),
			'merged_operations_delete_mark' : re.compile("merged operations:.+delete mark(.+), delete.+discarded operations",re.S).findall(insert_buffer_and_adaptive_hash_index)[0].strip(),
			'merged_operations_delete' : re.compile("merged operations:.+delete(.+).+discarded operations",re.S).findall(insert_buffer_and_adaptive_hash_index)[0].strip(),

			'discarded_operations_insert' : re.compile("discarded operations:.+insert(.+), delete mark",re.S).findall(insert_buffer_and_adaptive_hash_index)[0].strip(),
			'discarded_operations_delete_mark' : re.compile("discarded operations:.+delete mark(.+), delete",re.S).findall(insert_buffer_and_adaptive_hash_index)[0].strip(),
			'discarded_operations_delete' : re.compile("discarded operations:[\n].+delete(.+)[\n]").findall(insert_buffer_and_adaptive_hash_index)[0].strip(),

			#hash table ignore

			'hash_searche_per_second' : re.compile("(.+)hash searches/s,").findall(insert_buffer_and_adaptive_hash_index)[0].strip(),
			'non_hash_searche_per_second' : re.compile("hash searches/s,(.+)non-hash searches/s").findall(insert_buffer_and_adaptive_hash_index)[0].strip(),
		}
		
	def set_log(self,):
		#log_prin
		log = re.compile('LOG[\n]---[\n](.+)[\n]----------------------[\n]BUFFER POOL AND MEMORY',re.S).findall(self.innodb_status_str)[0]
		try:
			pending_log_flushes = re.compile("(.+)pending log flushes,").findall(log)[0].strip()
			pending_chk_writes = re.compile("pending log flushes,(.+)pending chkp writes").findall(log)[0].strip()
		except:
			#8.0 storage/innobase/log/log0log.cc log_print()
			pending_log_flushes = '8.0 无'
			pending_chk_writes = '8.0 无'

		self.innodb_status_dict['log'] = {
			'log_sequence_number' : re.compile("Log sequence number(.+)").findall(log)[0].strip(),
			'log_flushed_up_to' : re.compile("Log flushed up to(.+)").findall(log)[0].strip(),
			'pages_flushed_up_to' : re.compile("Pages flushed up to(.+)").findall(log)[0].strip(),
			'last_checkpoint_at' : re.compile("Last checkpoint at(.+)").findall(log)[0].strip(),

			'pending_log_flushes' : pending_log_flushes,
			'pending_chk_writes' : pending_chk_writes,

			'log_io_done' : re.compile("(.+)log i/o's done,").findall(log)[0].strip(),
			'log_io_per_second' : re.compile("log i/o's done,(.+)log i/o's/second").findall(log)[0].strip(),
			
		}

	def __buffer_pool_format(self,buffer_pool):
		#storage/innobase/srv/srv0srv.cc buf_print_io_instance
		try:
			buffer_pool_hit_rate = re.compile('Buffer pool hit rate(.+), young-making rate').findall(buffer_pool)[0].strip()
			young_marking_rate = re.compile(', young-making rate(.+)not').findall(buffer_pool)[0].strip()
			not_young_marking_rate = re.compile('Buffer pool hit rate.+not(.+)').findall(buffer_pool)[0].strip()
		except:
			msg = "数据库太闲,无此数据."
			buffer_pool_hit_rate = msg
			young_marking_rate = msg
			not_young_marking_rate = msg
		return {
			'buffer_pool_size':re.compile('Buffer pool size(.+)').findall(buffer_pool)[0].strip(),
			'free_buffers':re.compile('Free buffers(.+)').findall(buffer_pool)[0].strip(),
			'database_pages':re.compile('Database pages(.+)').findall(buffer_pool)[0].strip(),
			'old_database_pages':re.compile('Old database pages(.+)').findall(buffer_pool)[0].strip(),
			'modified_db_pages':re.compile('Modified db pages(.+)').findall(buffer_pool)[0].strip(),
			'pending_reads':re.compile('Pending reads(.+)').findall(buffer_pool)[0].strip(),
			'pending_writes_lru':re.compile('LRU(.+), flush list').findall(buffer_pool)[0].strip(),
			'pending_writes_flush_list':re.compile('flush list(.+), single page').findall(buffer_pool)[0].strip(),
			'pending_writes_single_page':re.compile('single page(.+)').findall(buffer_pool)[0].strip(),

			'pages_made_young':re.compile('Pages made young(.+),').findall(buffer_pool)[0].strip(),
			'pages_made_not_young':re.compile('not young(.+)').findall(buffer_pool)[0].strip(),
			'pages_made_youngs_per_second':re.compile('(.+)youngs/s,').findall(buffer_pool)[0].strip(),
			'pages_made_non_youngs_per_second':re.compile(',(.+)non-youngs/s').findall(buffer_pool)[0].strip(),
			'pages_read':re.compile('Pages read(.+), created').findall(buffer_pool)[0].strip(),
			'pages_created':re.compile('created(.+), written').findall(buffer_pool)[0].strip(),
			'pages_written':re.compile('written(.+)').findall(buffer_pool)[0].strip(),
			'pages_read_per_second':re.compile('(.+)reads/s,').findall(buffer_pool)[0].strip(),
			'pages_create_per_second':re.compile('reads/s,(.+)creates/s,').findall(buffer_pool)[0].strip(),
			'pages_written_per_second':re.compile('creates/s, (.+)writes/s').findall(buffer_pool)[0].strip(),

			#n_page_get_delta  TODO No buffer pool page gets since the last printout  Buffer pool hit rate %lu / 1000,young-making rate %lu / 1000 not %lu / 1000\n
			#buffer pool 的命中率
			'buffer_pool_hit_rate':buffer_pool_hit_rate,
			'young_marking_rate':young_marking_rate,
			'not_young_marking_rate':not_young_marking_rate,
			

			#/* Statistics about read ahead algorithm */
			'pages_read_ahead':re.compile('Pages read ahead(.+), evicted without access').findall(buffer_pool)[0].strip(),
			'pages_evicted_without_access':re.compile('evicted without access(.+), Random read ahead').findall(buffer_pool)[0].strip(),
			'pages_random_read_ahead':re.compile('Random read ahead(.+)').findall(buffer_pool)[0].strip(),

			#/* Print some values to help us with visualizing what is happening with LRU eviction. */
			'lru_len':re.compile('LRU len:(.+), unzip_LRU len:').findall(buffer_pool)[0].strip(),
			'unzip_lru_len':re.compile(', unzip_LRU len:(.+)').findall(buffer_pool)[0].strip(),
			'io':re.compile('I/O (.+), unzip ').findall(buffer_pool)[0].strip(),
			'unzip':re.compile(', unzip (.+)').findall(buffer_pool)[0].strip(),
		}
		
	def set_buffer_pool_and_memory(self):
		#TODO 注意多实例
		#storage/innobase/srv/srv0srv.cc srv_printf_innodb_monitor
		buffer_pool_and_memory = re.compile('BUFFER POOL AND MEMORY[\n]----------------------[\n](.+)[\n]--------------[\n]ROW OPERATIONS',re.S).findall(self.innodb_status_str)[0]
		buffer_pool_info_total_str = buffer_pool_and_memory

		buffer_pool_info = re.compile('INDIVIDUAL BUFFER POOL INFO[\n]----------------------[\n](.+)',re.S).findall(buffer_pool_and_memory)
		buffer_pool_info_detail = []
		if len(buffer_pool_info) > 0:
			#也就是使用了多个buffer pool instance
			buffer_pool_info_total_str = re.compile('(.+)----------------------[\n]INDIVIDUAL BUFFER POOL INFO',re.S).findall(buffer_pool_and_memory)[0]
			buffer_pool_list = buffer_pool_info[0].split('---BUFFER POOL ')
			for x in range(1,len(buffer_pool_list)):
				buffer_pool_info_detail.append(self.__buffer_pool_format(buffer_pool_list[x]))
				
		buffer_pool_info_total = {
			'total_large_memory_allocated' : re.compile('Total large memory allocated(.+)').findall(buffer_pool_info_total_str)[0].strip(),
			'dictionary_memory_allocated' : re.compile('Dictionary memory allocated(.+)').findall(buffer_pool_info_total_str)[0].strip(),
			'instance' : self.__buffer_pool_format(buffer_pool_info_total_str),
		}

		self.innodb_status_dict['buffer_pool_and_memory'] = {
			'buffer_pool_info_detail':buffer_pool_info_detail,
			'buffer_pool_info_total':buffer_pool_info_total,
		}

	def set_row_operations(self):
		row_operations = re.compile('ROW OPERATIONS[\n]--------------[\n](.+)[\n]----------------------------[\n]END OF INNODB MONITOR OUTPUT',re.S).findall(self.innodb_status_str)[0]

		self.innodb_status_dict['row_operations'] = {
			'queries_inside_innodb' : re.compile('(.+)queries inside InnoDB,').findall(row_operations)[0].strip(),
			'queries_in_queue' : re.compile('queries inside InnoDB,(.+)queries in queue').findall(row_operations)[0].strip(),

			#/* This is a dirty read, without holding trx_sys->mutex. */
			'read_views_open_inside_innodb' : re.compile('(.+)read views open inside InnoDB').findall(row_operations)[0].strip(),
			#TODO B-tree split operations

			'process_id' : re.compile('Process ID=(.+), Main thread ID=').findall(row_operations)[0].strip(),
			'main_thread_id' : re.compile(', Main thread ID=(.+), state:').findall(row_operations)[0].strip(),
			'state' : re.compile(', state:(.+)').findall(row_operations)[0].strip(),

			'number_of_rows_inserted' : re.compile('Number of rows inserted(.+), updated').findall(row_operations)[0].strip(),
			'number_of_rows_updated' : re.compile(', updated(.+), deleted').findall(row_operations)[0].strip(),
			'number_of_rows_deteled' : re.compile(', deleted(.+), read').findall(row_operations)[0].strip(),
			'number_of_rows_read' : re.compile(', read(.+)').findall(row_operations)[0].strip(),

			'insert_per_second' : re.compile('(.+)inserts/s,').findall(row_operations)[0].strip(),
			'update_per_second' : re.compile('inserts/s,(.+)updates/s,').findall(row_operations)[0].strip(),
			'delete_per_second' : re.compile('updates/s,(.+)deletes/s,').findall(row_operations)[0].strip(),
			'read_per_second' : re.compile('deletes/s,(.+)reads/s').findall(row_operations)[0].strip(),
			
		}

	def set_all(self):
		self.set_file_io()
		self.set_background_thread()
		self.set_semaphores()
		self.set_transactions()
		self.set_insert_buffer_and_adaptive_hash_index()
		self.set_log()
		self.set_buffer_pool_and_memory()
		self.set_row_operations()

class innodb_status_suggestion:
	def __init__(self,innodb_status_dict):
		self.innodb_status_dict = innodb_status_dict
		self.suggestion = []

	def suggestion_xxx(self):
		self.suggestion.append('TO BE CONTINUED')

	def suggestion_all(self):
		self.suggestion_xxx()

	def get_suggestion(self):
		return self.suggestion