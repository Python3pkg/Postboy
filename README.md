# Postboy
Simple but Fast Http client based on pycurl

## Usage
this package is developed with python3, because the name 'postboy' is occupied by others, you have to import `postboy2`

```python
# coding=utf-8
from postboy2 import PostBoy

if __name__ == '__main__':
    result = PostBoy('www.douban.com','utf-8').get()
    print(result['data']['title'])
```

##Change Log

v0.0.3 : add simple post support

v0.0.2 : reformat the result output

v0.0.1 : add get support


