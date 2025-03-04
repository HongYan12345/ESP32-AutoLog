import gc
import time
import _thread

class MemoryManager:
    def __init__(self):
        self.stop_threads = False
        self._cleaner_thread = None
        
    def get_memory_info(self):
        """获取内存信息"""
        gc.collect()  # 执行垃圾回收
        free_memory_bytes = gc.mem_free()
        allocated_memory_bytes = gc.mem_alloc()
        
        # 转换为 KB 和 MB
        free_memory_kb = free_memory_bytes / 1024
        free_memory_mb = free_memory_kb / 1024
        allocated_memory_kb = allocated_memory_bytes / 1024
        
        return {
            'free_kb': free_memory_kb,
            'free_mb': free_memory_mb,
            'allocated_kb': allocated_memory_kb
        }
        
    def print_memory_info(self):
        """打印内存信息"""
        mem_info = self.get_memory_info()
        print("Allocated memory: {:.2f} KB".format(mem_info['allocated_kb']))
        print("Free memory: {:.2f} KB = {:.2f} MB".format(
            mem_info['free_kb'], 
            mem_info['free_mb']
        ))
        
    def _memory_cleaner_thread(self, interval=10):
        """内存清理线程"""
        while not self.stop_threads:
            self.print_memory_info()
            time.sleep(interval)
        print("cleaner thread finish...")
        
    def start_cleaner(self, interval=10):
        """启动内存清理线程"""
        self.stop_threads = False
        _thread.start_new_thread(self._memory_cleaner_thread, (interval,))
        
    def stop_cleaner(self):
        """停止内存清理线程"""
        self.stop_threads = True

# 使用示例
memory_manager = MemoryManager()

# 启动内存清理
def start_memory_monitoring(interval=10):
    memory_manager.start_cleaner(interval)

# 停止内存清理
def stop_memory_monitoring():
    memory_manager.stop_cleaner()