#!/usr/bin/env python3
#encoding = utf-8

from flask import Flask

app = Flask(__name__)

from app import views
