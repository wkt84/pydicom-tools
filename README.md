# pydicom tools

pydicomを用いてDICOM RTを解析するときのツール群です。

## 3次元CTデータの構築

以下の方法で変数`ct`に3次元Volumeを読み込みます。

```python
from pydicom_tools import CTImage
ct = CTImage()
ct.load(path_to_ct)
```