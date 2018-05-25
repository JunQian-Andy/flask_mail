#!/usr/bin/env python
#-*- encoding: utf-8 -*-

from app import api
#app.run(debug=True)
api.app.run(host = '0.0.0.0', debug=True)
