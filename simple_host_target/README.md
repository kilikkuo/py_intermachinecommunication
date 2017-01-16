# simple_host_target (python3 only for now)
A package which host and target server could be easily setup (I assume ...) in separate machine to dispatch task and execute then deliver results back.

 - Installation
    ```shellscript
        $> pip3 install git+https://github.com/kilikkuo/py_simple_host_target.git
    ```

 - On Host Machine
   * Terminal 1
    ```shellscript
        $> import simple_host_target as sht
        $> host = sht.create_host()
        $> host.setup_target_IPs(["TARGET.IP.SAMPLE.1", "TARGET.IP.SAMPLE.2"])
        $> host.run()
    ```

   * Terminal 2 (After target has set up, and be sure to run the python env in the same place as Terminal 1)
    ```shellscript
        $> import simple_host_target as sht
        $> sht.test_sample_project()
    ```

 - On Target Machine
   * Terminal 3
    ```shellscript
        $> import simple_host_target as sht
        $> target = sht.create_target()
        $> target.run("HOST.IP.SAMPLE.1")
    ```
