openstack-setup
===============

Helper utilities for OpenStack services on Fedora/RHEL distros

Largely based on openstack-utils, and dependant on openstack-db, 
openstack-config and openstack-status


Configs
-------

* openstack-setup.rc                - Setup resource/configuration file - 
                                      all tweaking happens there
* openstack-runtime.rc              - This file will be auto-updated by setup
                                      process. To be used for setting up environment
                                      to use with OpenStack CLI tools:
                                        $ . openstack-runtime.rc

All of the scripts below accept parameter - name of the RC file to use for 
variable initialization.


Scripts
-------

* openstack-setup                   - Main script

* openstack-keystone-setup          - Setup Keystone service

  * openstack-keystone-setup-data     - Sample Data for keystone (and others) service

* openstack-glance-setup            - Setup Glance service
* openstack-nova-setup              - Setup Nova service

  * openstack-nova-glance-demo        - Sample script to add instance to Glance & Nova

* openstack-cinder-setup            - Setup Cinder service
* openstack-horizon-setup           - Setup Horizon service
* openstack-swift-setup             - Setup Swift service

Library/misc
------------

* openstack-setup-utils             - Shell utils used from other scripts and that could be
                                      used from CLI for debugging etc.

