# pydicom tools

pydicomを用いてDICOM RTを解析するときのツール群です。

## 3次元CTデータの構築

以下の方法で変数`ct`に3次元Volumeを読み込みます。

```python
from pydicom_tools import CTImage
ct = CTImage()
ct.load(path_to_ct)
```

## DRRの生成

以下の方法でDRRを生成します。
DRRの作成にはITKが必要です。事前にpipなどでインストールしてください。

```console
pip install itk
```

```python
from pydicom_tools import DRR
drr = DRR(ct, beam, size)
```

`ct`は`CTImage`クラスのインスタンス、`beam`はBeamSequenceのオブジェクト、
`size`はDRRのmm単位のサイズです。