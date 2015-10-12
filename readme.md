# SpeechToTextProxy

Pepperのマイクから拾った音声をテキストに変換し、結果をPepperのメモリに格納するプロキシ。  
変換にはBluemix Speech To Textを用い、WebSocketで音声データを流し、変換し続ける。 

## サンプルの実行方法
1. `pip install -r requirements.txt` を実行し、依存ライブラリをインストールする。
2. `index.py` の parameters の値を適宜変更する。
3. `SpeechToTextProxy_sample/SpeechTextProxy_sample.pml` をChoregrapheで起動する。
4. `index.py` で `EVENT_ROOT_NAME` を変更した場合は、メモリイベントを指定しなおす。
5. Choregraphe で実機Pepperに接続する。
6. `python index.py` を実行する。
7. `Choregraphe でサンプルプロジェクトを実行する。

## Memories

### WordRecognition
変換結果のリストを格納する。

~~~
[[word, confidence]*]
~~~

### Status

プロキシの状態を示す。
"running"を指定すると変換を開始する。
"stop"を指定すると変換を停止する。

~~~
"running"|"stop"|"error"
~~~

### Error

エラー情報を格納する。

~~~
Error|None
~~~
