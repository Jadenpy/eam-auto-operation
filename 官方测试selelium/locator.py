# 用于存储网页定位符的别名模块
from enum import Enum
class Locator(Enum):
    TEXT_INPUT = "text_input"
    PASSWORD_INPUT = "password_input"
    TEXT_AREA = "textarea"
    DISABLED_INPUT = "disabled_input"
    READONLY_INPUT = "readonly_input"
    RETURN_TO_INDEX = 'return_to_index'
    SELECT_DROPDOWN = 'select_dropdown'
    DATALIST_DROPDOWN = 'datalist_dropdown'
    FILE_INPUT = 'file_input'
    CHECKED_CHECKBOX = 'checked_checkbox'
    DEFAULT_CHECKBOX = 'default_checkbox'
    CHECKED_RADIO = 'checked_radio'
    DEFAULT_RADIO = 'default_radio'
    SUBMIT_BUTTON = 'submit_button'
    COLOR_PICKER = 'color_picker'
    DATA_PICKER = 'date_picker'
    EXAMPLE_RANGE = 'example_range'
    # 可以根据需要添加更多的定位符别名

locators = {

    "text_input": '#my-text-id',  # 别名：  HTML标签：input     动作：
    'password_input': '/html/body/main/div/form/div/div[1]/label[2]/input',  # 别名：PASSWORD_INPUT  HTML标签：input     动作：输入密码
    'textarea': '/html/body/main/div/form/div/div[1]/label[3]/textarea',    # 别名：    HTML标签：    动作：
    'disabled_input': '/html/body/main/div/form/div/div[1]/label[4]/input',     # 别名：     HTML标签：input     动作：输入内容
    'readonly_input': '/html/body/main/div/form/div/div[1]/label[5]/input',  # 别名：  SUBMIT_BUTTON    HTML标签：button    动作：点击提交按钮
    'return_to_index': '/html/body/main/div/form/div/div[1]/div/a',  # 别名：RETURN_TO_INDEX    HTML标签：a    动作：返回首页
    'select_dropdown': '/html/body/main/div/form/div/div[2]/label[1]/select',  # 别名：SELECT_DROPDOWN    HTML标签：select    动作：选择下拉选项
    'datalist_dropdown': '/html/body/main/div/form/div/div[2]/label[2]/input',  # 别名：DATALIST_DROPDOWN    HTML标签：input    动作：选择数据列表选项
    'file_input': '/html/body/main/div/form/div/div[2]/label[3]/input',  # 别名：FILE_INPUT    HTML标签：input    动作：上传文件
    'checked_checkbox': '//*[@id="my-check-1"]',  # 别名：CHECKED_CHECKBOX    HTML标签：input    动作：勾选复选框
    'default_checkbox': '//*[@id="my-check-2"]',  # 别名：DEFAULT_CHECKBOX    HTML标签：input    动作：默认复选框
    'checked_radio': '//*[@id="my-radio-1"]',  # 别名：CHECKED_RADIO    HTML标签：input    动作：选择单选按钮
    'default_radio': '//*[@id="my-radio-2"]',  # 别名：DEFAULT_RADIO    HTML标签：input    动作：默认单选按钮
    'submit_button': '/html/body/main/div/form/div/div[2]/button',  # 别名：SUBMIT_BUTTON    HTML标签：button    动作：点击提交按钮
    'color_picker': '/html/body/main/div/form/div/div[3]/label[1]/input',  # 别名：COLOR_PICKER    HTML标签：input    动作：选择颜色
    'date_picker': '/html/body/main/div/form/div/div[3]/label[2]/input',  # 别名：DATE_PICKER    HTML标签：input    动作：选择日期
    'example_range': '/html/body/main/div/form/div/div[3]/label[3]/input',  # 别名：TIME_PICKER    HTML标签：input    动作：选择时间

}

# 使用示例
# mySite.element_write(locators[Locator.USERNAME_INPUT.value], "my_username")