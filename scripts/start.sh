#!/bin/bash
cp conf/supervisor/*.conf /etc/supervisor/conf.d
/etc/init.d/supervisor start