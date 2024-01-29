# hip-vpls-controller
HIP-VPLS controller (HIP switch controller)

This repository contains the implementation of HIP switch controller and configurator.

Manage and configure your HIP-VPLS switches on the central controller.

# Architecture

```
                              +-------------+
                              | WEB config  |
                              +-------------+
                                     |
                              +-------------+
                              | Controller  |
                              +------+------+
+------------+      TLS       |      |      |   TLS             +------------+
| HIP switch |----------------+   HIP/IPSec +-------------------| HIP switch |
+-----+------+-----------------------|--------------------------+------+-----+
      |                              |                                 |
      |        HIP/IPSec      +------------+      HIP/IPSec            |
      +-----------------------| HIP switch |---------------------------+
                              +------------+
```

```
$ cd configurator
$ cd deployment
$ sudo bash deploy.sh
```

Open the browser at the private IP address (you might need to change the IP address in the front end though main.js file) 

