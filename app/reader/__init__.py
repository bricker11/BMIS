# -*— coding:utf-8 -*—
from flask import Blueprint

reader = Blueprint('reader',__name__)

from . import forms, views, errors