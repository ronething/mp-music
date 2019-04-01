# mp-music

## 前言

微信公众号接入音乐 API

其实应该很多人都做过了。只是无聊又想给自己的订阅号接入一下。

## Run

```python
git clone [repo]
pipenv install
```

~~在 `config/setting.py` 下新增 TOKEN='xxxx' 与公众号配置的 TOKEN 一致。~~

在 `app/config` 目录下新建 `secure.py`  新增 TOKEN='xxxx' 与公众号配置的 TOKEN 一致

```sh
pipenv shell
python manage.py
```

## Demo

![music](./assets/music.gif)

## Change Log

- Tue Apr  2 02:13:13 first version

## 致谢

- [music-dl](https://github.com/0xHJK/music-dl)
