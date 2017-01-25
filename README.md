# simple_host_target (python3 only for now)
A package which host and target server could be easily setup (I assume ...) in separate machine to dispatch task and execute then deliver results back.

 - Introduction

 Intend to send a bunch of python sources (i.e. a folder) to multiple devices to
 continue the works !
 Host needs to be configured with several Target's IPs.
 Target needs to be configured with Host's IP.
 Sender needs to package and zip its whole project then invoking API |send_task_to_host| to deliver its loader scripts for Target to unzip the project and execute the task.
 The project program is responsible of saving the calculation results and the results
 can be easily zipped then send back to sender.

 Note : Please refer to sender.py for details.

 - Installation

  -- Method 1
    ```shellscript
        $> pip3 install git+"https://github.com/kilikkuo/py_simple_host_target.git#egg=simple_host_target&subdirectory=simple_host_target"
    ```
  -- Method 2
    ```shellscript
        $> git clone https://github.com/kilikkuo/py_simple_host_target.git
        $> cd py_simple_host_target/simple_host_target
        $> pip3 install .
    ```
 - Uninstallaiton

    ```shellscript
        $> pip3 uninstall simple_host_target
    ```

 - Give it a try

  Play with python source file
   * Host
    ```shellscript
        $> cd py_simple_host_target/simple_host_target/simple_host_target
        $> python3 host.py
    ```
   * Target
    ```shellscript
        $> cd py_simple_host_target/simple_host_target/simple_host_target
        $> python3 target.py
    ```
   * Sender
    ```shellscript
        $> python3 sender.py
    ```

  Play as python module
   * Host
    ```shellscript
        $> import simple_host_target as sht
        $> host = sht.create_host()
        <!-- This is optional
        $> host.setup_target_IPs(["TARGET.IP.SAMPLE.1", "TARGET.IP.SAMPLE.2"])
        -->
        $> host.run()
    ```

   * Target
    ```shellscript
        $> import simple_host_target as sht
        $> target = sht.create_target()
        $> target.run("HOST.IP.SAMPLE.1")
    ```

   * Sender (After Host & Target is up )
    ```shellscript
        $> python3 sender.py
    ```
