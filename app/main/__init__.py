"""
main包为业务逻辑包 - 主业务
通过蓝图(Blueprint)将自己与app关联到一起
"""
from flask import Blueprint

main = Blueprint('main',__name__)

from . import views