
import sys

sys.path.append(r'G:\py\pypi\rcdata\src')

from rcdata import BaseData, Field

class TestBaseData(BaseData):
    name = Field("default_name", str)
    age = Field(30, int)



obj = TestBaseData()
obj.name = "Alice"  # 写入 __data
print(obj.name)  # 输出: Alice
print(obj.age)  # 输出: KeyError，因为 age 不在 __data 中
obj.age = 25  # 写入 __data
print(obj.age)  # 输出: 25

obj.custom_attr = "custom_value"  # 写入 __dict__
print(obj.custom_attr)  # 输出: custom_value

print(dir(obj))
