# 第三方模块指的是别人定义好的,用于解决特定问题的模块
'''
注意:
1.在使用第三方模块的时候,需要先安装   numpy  pandas  matplotlib  flask  django
2.导入后才能使用
'''

# 第一种安装方式:   pip指令
'''
pip -V    查看pip的版本
python -m pip install --upgrade  pip  更新pip的版本
pip list  查看当前环境中安装的所有的模块
pip install  模块名(扩展名)     安装第三方模块
pip install  模块名(扩展名)  -i  "https://pypi.douban.com/simple"    临时使用国内的镜像源

pip uninstall 模块名(扩展名)     卸载指定的第三方模块
pip show 模块名(扩展名)   查看某个模块的详细信息

练习: 使用pip 安装 numpy  pandas   matplotlib  flask   django
'''

# 第二种安装方式:
# 通过pycharm编辑器:   文件-->设置--->项目---->python解释器
'''
+ 表示安装模块
- 表示卸载模块
'''
