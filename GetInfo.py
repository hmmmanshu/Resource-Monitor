def get_processes_info():
    import psutil
    from datetime import datetime
    processes = []
    for process in psutil.process_iter():
        with process.oneshot():
            pid = process.pid
            if pid == 0: continue
        name = process.name()

        try:
            create_time = datetime.fromtimestamp(process.create_time())
        except OSError:
            create_time = datetime.fromtimestamp(psutil.boot_time())
        
        try:
            # get the number of CPU cores that can execute this process
            cores = len(process.cpu_affinity())
        except psutil.AccessDenied:
            cores = 0
        # get the CPU usage percentage
        cpu_usage = process.cpu_percent()
        # get the status of the process (running, idle, etc.)
        status = process.status()
        
        try:
            # get the process priority (a lower value means a more prioritized process)
            nice = int(process.nice())
        except psutil.AccessDenied:
            nice = 0

        try:
            # get the memory usage in bytes
            memory_usage = process.memory_full_info().uss
        except psutil.AccessDenied:
            memory_usage = 0

        # total process read and written bytes
        io_counters = process.io_counters()
        read_bytes = io_counters.read_bytes
        write_bytes = io_counters.write_bytes

        n_threads = process.num_threads()

        # get the username of user spawned the process
        try:
            username = process.username()
        except psutil.AccessDenied:
            username = "N/A"
            
        processes.append({
            'pid': pid, 'name': name, 'create_time': create_time,
            'cores': cores, 'cpu_usage': cpu_usage, 'status': status, 'nice': nice,
            'memory_usage': memory_usage, 'read_bytes': read_bytes, 'write_bytes': write_bytes,
            'n_threads': n_threads, 'username': username,
        })

    return processes