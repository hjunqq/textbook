# 附录B：编程基础知识速查

本附录提供了智慧水利平台开发中常用的编程语言基础知识速查，帮助读者快速回顾和掌握关键语法和概念。

## HTML5基础

### 文档结构

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>文档标题</title>
    <link rel="stylesheet" href="styles.css">
    <script src="script.js"></script>
</head>
<body>
    <!-- 页面内容 -->
    <h1>标题</h1>
    <p>段落</p>
</body>
</html>
```

### 常用标签

| 标签 | 描述 |
| ---- | ---- |
| `<h1>` - `<h6>` | 标题 |
| `<p>` | 段落 |
| `<div>` | 块级容器 |
| `<span>` | 行内容器 |
| `<a>` | 超链接 |
| `<img>` | 图片 |
| `<ul>`, `<ol>`, `<li>` | 列表 |
| `<table>`, `<tr>`, `<td>` | 表格 |
| `<form>`, `<input>`, `<button>` | 表单元素 |

## CSS3基础

### 选择器

```css
/* 元素选择器 */
div { color: blue; }

/* 类选择器 */
.class-name { color: red; }

/* ID选择器 */
#id-name { color: green; }

/* 属性选择器 */
input[type="text"] { border: 1px solid gray; }

/* 伪类选择器 */
a:hover { text-decoration: underline; }

/* 子元素选择器 */
ul > li { list-style-type: square; }
```

### 盒模型

```css
div {
    width: 300px;
    height: 200px;
    padding: 20px;
    border: 1px solid black;
    margin: 30px;
    box-sizing: border-box; /* 包含padding和border */
}
```

## JavaScript基础

### 变量与数据类型

```javascript
// 变量声明
let name = "张三";
const age = 30;
var isActive = true;

// 数据类型
// 字符串
let str = "Hello";
// 数字
let num = 42;
// 布尔值
let flag = false;
// 数组
let arr = [1, 2, 3, 4];
// 对象
let obj = { name: "李四", age: 25 };
// 空值
let n = null;
let u = undefined;
```

### 函数

```javascript
// 函数声明
function add(a, b) {
    return a + b;
}

// 箭头函数
const multiply = (a, b) => a * b;

// 函数调用
let sum = add(5, 3);
let product = multiply(4, 2);
```

### 条件与循环

```javascript
// if条件
if (age > 18) {
    console.log("成年");
} else {
    console.log("未成年");
}

// switch语句
switch (status) {
    case "online":
        console.log("在线");
        break;
    case "offline":
        console.log("离线");
        break;
    default:
        console.log("未知状态");
}

// for循环
for (let i = 0; i < 5; i++) {
    console.log(i);
}

// while循环
let j = 0;
while (j < 5) {
    console.log(j);
    j++;
}

// forEach遍历
arr.forEach(item => {
    console.log(item);
});
```

## Python基础

### 变量与数据类型

```python
# 变量赋值
name = "张三"
age = 30
is_active = True

# 数据类型
# 字符串
text = "Hello World"
# 数字
integer = 42
floating = 3.14
# 布尔值
flag = False
# 列表
my_list = [1, 2, 3, 4, 5]
# 元组
my_tuple = (1, 2, 3)
# 字典
my_dict = {"name": "李四", "age": 25}
# 集合
my_set = {1, 2, 3, 4}
```

### 函数

```python
# 函数定义
def greet(name):
    return f"Hello, {name}!"

# 带默认参数的函数
def add(a, b=0):
    return a + b

# 函数调用
message = greet("张三")
result = add(5, 3)
```

### 条件与循环

```python
# if条件
if age > 18:
    print("成年")
elif age == 18:
    print("刚好成年")
else:
    print("未成年")

# for循环
for i in range(5):
    print(i)

# while循环
j = 0
while j < 5:
    print(j)
    j += 1

# 列表推导式
squares = [x**2 for x in range(10)]
```

## Java基础

### 变量与数据类型

```java
// 基本数据类型
int number = 42;
double pi = 3.14;
boolean flag = true;
char letter = 'A';

// 引用类型
String name = "张三";
int[] numbers = {1, 2, 3, 4, 5};
List<String> names = new ArrayList<>();
Map<String, Integer> ages = new HashMap<>();
```

### 类与对象

```java
// 类定义
public class Person {
    // 属性
    private String name;
    private int age;
    
    // 构造函数
    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    // 方法
    public String getName() {
        return name;
    }
    
    public void setName(String name) {
        this.name = name;
    }
    
    public int getAge() {
        return age;
    }
    
    public void setAge(int age) {
        this.age = age;
    }
}

// 创建对象
Person person = new Person("张三", 30);
```

### 条件与循环

```java
// if条件
if (age > 18) {
    System.out.println("成年");
} else {
    System.out.println("未成年");
}

// switch语句
switch (status) {
    case "online":
        System.out.println("在线");
        break;
    case "offline":
        System.out.println("离线");
        break;
    default:
        System.out.println("未知状态");
}

// for循环
for (int i = 0; i < 5; i++) {
    System.out.println(i);
}

// while循环
int j = 0;
while (j < 5) {
    System.out.println(j);
    j++;
}

// 增强for循环
for (int num : numbers) {
    System.out.println(num);
}
```

## SQL基础

### 基本查询

```sql
-- 查询所有列
SELECT * FROM users;

-- 查询指定列
SELECT id, username, email FROM users;

-- 条件查询
SELECT * FROM users WHERE age > 18;

-- 排序
SELECT * FROM users ORDER BY created_at DESC;

-- 分组
SELECT department, COUNT(*) FROM employees GROUP BY department;

-- 连接查询
SELECT users.username, orders.order_number
FROM users
JOIN orders ON users.id = orders.user_id;
```

### 增删改

```sql
-- 插入数据
INSERT INTO users (username, email, age) VALUES ('张三', 'zhangsan@example.com', 25);

-- 更新数据
UPDATE users SET age = 26 WHERE username = '张三';

-- 删除数据
DELETE FROM users WHERE id = 1;
``` 