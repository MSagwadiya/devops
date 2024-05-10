 
#!/bin/bash

echo 1 >/proc/sys/vm/compact_memory

sync

echo 3 >/proc/sys/vm/drop_caches
