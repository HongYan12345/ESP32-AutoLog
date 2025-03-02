import gc

# 打印当前可用内存
gc.collect()
print("Free memory:", gc.mem_free()/1024, "KB")

