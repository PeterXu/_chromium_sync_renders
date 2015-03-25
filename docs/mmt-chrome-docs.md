Media Cast & MMTP Receiver
===========================


<br />
1. chrome mmt协议
-----------------

### 1) MMT数据地址格式

#### a) 通过本地媒体读取数据

- html和cixml文件本地路径
    - /tmp/index.html
    - /tmp/ci.xml
- chrome获取html数据地址格式
    - mmt://localhost/tmp/index.html
- chrome获取ci数据
    - 由mmt模块直接读取文件/tmp/ci.xml
- audio/video/image地址格式
    - cixml中格式(sequence_num可选)
        - mmt://localhost/tmp/Channel1?<mark>sequence_num=1-230&type=audio</mark>
        - mmt://localhost/tmp/Channel1?sequence_num=1-230&type=video
        - mmt://localhost/tmp/test.mp4?type=image
    - chrome内部数据格式: <mark>sequence_num=1-230&type=audio&htmlid=xx&tabid=xx</mark>
- subset xml地址格式
    - cixml中格式: mmt://localhost/tmp/subset1.xml
    - chrome内部数据格式: <mark>type=ci&htmlid=xx&tabid=xx</mark>

#### b) 通过mmtp协议读取数据

- chrome组播地址格式
    - mmt://224.1.1.101:6080?<mark>proto=mmtp</mark>
- html和主cixml数据获取
    - 由mmtp接收端直接获取得到(回调函数)
- audio/video/image获取格式
    - mmt://asset_id1?<mark>proto=mmtp&type=audio</mark>
    - mmt://asset_id2?proto=mmtp&type=video
    - mmt://asset_id3?proto=mmtp&type=image
    - chrome内部数据格式: <mark>proto=mmtp&type=audio&htmlid=xx&tabid=xx</mark>
- subset cixml通过http协议获取
    - 地址格式
        - mmt://<mark>apache-address</mark>/subset.xml?<mark>proto=extra</mark>
    - chrome内部数据格式: <mark>proto=extra&type=ci&htmlid=xx&tabid=xx</mark>
    - 格式更新
        - 原<mark>proto=extra</mark>依旧支持
        - 用<mark>proto=http</mark>替代方案


#### c) 支持mmtp协议列表
- chrome频道列表获取(每个列表包含一个组播地址)
    - mmt://apache-address/index.html?<mark>proto=http</mark>
- 组播地址格式(同上)
    - mmt://224.1.1.101:6080?<mark>proto=mmtp</mark>
- audio/video/image格式(同上)
    - mmt://asset_id1?<mark>proto=mmtp&type=audio</mark>
    - mmt://asset_id2?proto=mmtp&type=video
    - mmt://asset_id3?proto=mmtp&type=image


### 2) MMT协议处理数据流程

### 3) MMT协议处理模块

- mmt control
- mmt stream
- mmt parser
- mpu parser
- mmtp receiver


### 4) 模块代码

    src/net/mmt/
    src/net/url_request/
    src/chrome/browser/
    src/content/public/
    src/extension/
    src/third_party/ffmpeg/
    
    src/media/cast/
    src/media/blink/
    src/media/filters/
    src/third_party/WebKit/




<br />
2. media casting
----------------


### 1) HTML模块接口
```
src/thirdparty/WebKit/public/platform/WebMediaPlayer.h
src/thirdparty/WebKit/Source/core/html/HTMLMediaElement.cpp/h
src/thirdparty/WebKit/Source/core/html/HTMLMediaElement.idl
```

#### a) 在html5 \<video>\<audio>添加新method:
```
/**
 * Set Casting dest ip/port
 * @param enable:  true/false => start/stop media casting 
 * @param ip/port:  unicast udp ip/port
 */
void cast(boolean enable, optional string ip, optional short port);
```

#### b) WebKit与chromium之间的播放器接口定义在WebMediaPlayer.h中
    class blink::WebMediaPlayer;


### 2) 播放器模块
- 将解码后的audio/video数据转发到cast模块. 公共实现在class media::WebMediaPlayerImpl中。
- Source code

    ```
    media/blink/webmediaplayer_impl.cc
    media/base/pipeline.cc
    media/filters/audio_renderer_impl.cc
    media/filters/renderer_impl.cc
    ```


### 3) Cast核心模块代码
    media/cast/cast_streaming.h/cc
    media/cast/cast_source.h/cc
    media/cast/sender/**
    media/cast/net/**
    
#### a) 初始化audio encoder模块(cast_streaming.h/cc)
    codec: opus
    channels: 2
    sample rate: 48000
    bitrate: auto-VBR
        
#### b) 初始化video encode模块(cast_streaming.h/cc)
    codec: vp8
    size: 320x180
    fps: 20
    bitrate: 100kbps - 1.5mbps
    encode QP: 4-40
        
#### c) 初始化rtp/rtcp/udp传输模块
    code: media/cast/net/**
    supported codec: OPUS/PCM16/AAC/VP8/H264 
    current using codec: OPUS/VP8


### 4) chrome cast基本实现原理
    a. 在原有HTML5 video/audio的基础上, 获取解码后的音视频数据(包含呈现timestamp),
    b. 将解码后的音视频数据提交到audio/video编码器中(以上面的timestamp为参考),
    c. 将编码后的数据进行RTP打包,并通过网络发送出去,
    d. Cast接收端接收相应地RTP audio/video数据, 并解码呈现,
    e. cast实现代码在src/media/cast模块中。


### 5) chrome cast代码流程

#### a) \<video> 处理
    => html5 <video> => video decode ...
    => VideoRendererImpl::ThreadMain() 
    => VideoRendererImpl::PaintNextReadyFrame_Locked()
    => paint_cb_.Run(next_frame);
    => WebMediaPlayerImpl::FrameReady()
    => CastStreaming::InputRawVideo() 
    => CastSource::InputRawVideo()
    => CastSource::SendNextTranscodedVideo()
    => VideoFrameInput::InsertRawVideoFrame() 
 
#### b) \<audio>处理
    => html5 <audio> => audio decode ...
    => AudioRendererImpl::AttemptRead_Locked()
    => AudioRendererImpl::DecodedAudioReady()
    => AudioRendererImpl::HandleSplicerBuffer_Locked()
    => echo_cb_.Run(buffer);
    => WebMediaPlayerImpl::EchoReady()
    => CastStreaming::InputRawAudio() 
    => CastSource::InputRawAudio()
    => CastSource::SendNextTranscodedAudio()
    => AudioFrameInput::InsertAudio() 



<br />
3. MMTP Receiver接口
-------------------

### 1) 模块功能
    
- 处理组播地址协议
- 接收asset id并返回对应的url
- 接收组播频道媒体数据并通知chrome接收端


### 2) MMTP数据接收

MMTP提供给chrome调用的接口API:

<!--lang:c++-->
```
//== filename: mmtp.h ==

/**
 * Chrome init mmtp receiver: do some initilization for receiver
 */
void init_mmtp();

/**
 * Chrome set asset ids
 */
void set_mmtp_assets(const char* ids[], int num);

/**
 * Chrome start mmtp receiver with multicast address
 */
void start_mmtp(const char* mcast_ip, int mcast_port);

/**
 * Chrome stop current mmtp receiver
 */
void stop_mmtp();

/**
 * Chrome uninit mmtp receiver, release all allocated resources
 */
void uninit_mmtp();


/**
 * Chrome set mmtp callback, it will be called to notify chrome
 *  When receiving ci/html/audio/video/image
 * 
 * 下一部分的push_mmtp_cihtml/push_mmtp_media就是通过调用该回调函数实现
 * 通知chrome的.
 */
struct mmtp_rinfo_t;
typedef void (*mmtp_callback_t) (struct mmtp_rinfo_t* rinfo);
void set_mmtp_callback(mmtp_callback_t cb);
```


<br />
MMTP内部调用的封装接口

```
//== filename: mmtp.h ==

/**
 * mmtp resource type
 */
enum mmtp_res_t {
    Res_Unknown   = 0,
    Res_CI        = 0x0001,
    Res_Html      = 0x0002,
    Res_Signal    = Res_CI + Res_Html,

    Res_Video     = 0x0004,
    Res_Audio     = 0x0008,
    Res_Image     = 0x0010,
    Res_Media     = Res_Video + Res_Audio + Res_Image,
};


/**
 * The info of received data
 */
struct mmtp_rinfo_t {
    int  res;           //> @refer mmtp_res_t
    char id[512];       //> asset id
    char url[512];      //> asset url
    char fname[512];    //> received filename
    
    int  sequence;      //> reserverd
};

/**
 * When receiving ci/html, MMTP should call it to notify chrome
 * @param res: Res_CI or Res_Html.
 * @param fname: the file path of ci/html
 */
void push_mmtp_cihtml(int res, const char* fname);

/**
 * When receiving audio/video/image, MMTP should call it to notify chrome
 * @param res: Res_Video, Res_Audio or Res_Image
 * @param id: asset id
 * @param url: asset url
 * @param fname: the file path of video/audio/image
 */
void push_mmtp_media(int res, const char* id, const char* url, const char* fname);

```


<br />
### 3).<mark>**数据请求示例**</mark>

- chrome初始化MMTP模块

    ```
    init_mmtp();
    ```

- chrome设置需要请求的asset id

    ```
    char* asset_ids[] = {"asset_video1", "asset_audio1"};
    set_mmtp_assets(asset_ids, 2);
    ```

- chrome启动MMTP接收组播频道

    ```
    char mcast_ip[] = "224.1.1.101";
    int mcast_port = 6080;
    start_mmtp(mcast_ip, mcast_port);
    ```

- 当MMTP接收到html/xml时，调用方式如下

    ```
    char ci[] = "ci.xml";
    push_mmtp_cihtml(Res_CI, ci);
    
    char html[] = "index.html";
    push_mmtp_cihtml(Res_Html, html);
    ```

- 当MMTP接收到audio/video/image时,需要进行如下操作

    ```
    char audio_id[] = "asset_audio_id1";
    char audio_url[] = "mmt://test/audio/...";
    char audio_fname[] = "audio.mp4";
    push_mmtp_media(Res_Audio, audio_id, audio_url, audio_fname);
    
    /// video/image is like audio above.
    push_mmtp_media(Res_Video, video_id, video_url, video_fname);
    push_mmtp_media(Res_Image, image_id, image_url, image_fname);
    ```

- chrome关闭MMTP数据接收

    ```
    stop_mmtp();
    ```
    
- chrome释放MMTP资源

    ```
    uninit_mmtp();
    ```



<br />
3 多屏实现
---------

### 1).<mark>**实现功能**</mark>

- 主屏/副屏监听本地UDP端口服务
- 主屏额外添加一个html form供用户设置分享的副屏IP
- 主屏接收其它chrome多屏请求(UDP)
- 主屏发送xml/html给chrome副屏
- 副屏向主屏发送多屏请求(mmt://multi-screen) - 通过扩展打开页面提供设置主屏IP


### 2).<mark>**扩展multi-screen(简称ms)协议**</mark>

具体参照以下代码实现。

<!--lang:c++-->
```
/**
 * The type of multi-screen message.
 */
enum ms_type_t{
    E_MS_Unknown    = 0,
    
    E_MS_Request    = 0x0001,
    E_MS_CiHtml     = 0x0002,
    
    E_MS_All        = 0xffff
};

/** 
 * ms packet structure: not include <body>.
 */
#prarma pack(1)
typedef struct ms_packet_t {
    char        ver;
    int         type;       //> packet type
    char        bcast[64];  //> broadcast address
    int         size;       //> packet body size
    char        body[1];
}ms_packet_t;
#prarma pack(0)

#define DEFAULT_VERSION             1
#define HEAD_SIZE                   (sizeof(mmtp_packet_t)-1)
#define MAX_BODY_SIZE               (1024*16-HEAD_SIZE)
#define assert_return(p, v)         if(!(p)) return (v);


/**
 * Init commom header of ms packet
 */
mmtp_packet_t* init_header(char* buffer, int type, const char* bcast) {
    ms_packet_t* pkt = (ms_packet_t*) buffer;
    assert_return(pkt, NULL);
    memset((void*)pkt, 0, HEAD_SIZE);
    pkt->ver  = DEFAULT_VERSION;
    pkt->type = type;
    if (bcast && strlen(bcast) > 0) {
        strncpy(pkt->bcast, bcast, sizeof(pkt->bcast)-1);
    }
    return pkt;
}
```

<!--lang:c++-->
```
/**
 * Request sharing from main screen.
 */
int set_packet_ms_request(char* buffer) {
    ms_packet_t* pkt = init_header(buffer, E_MS_Request, NULL);
    assert_return(pkt, -1);
    return HEAD_SIZE + pkt->size;
}

/**
 * send multi-screen(ms) html/xml to second screen
 * @param bcast: broadcast address
 * @param ci: ci xml content
 * @param html: html content
 */
int set_packet_ms_cihtml(char* buffer, const char* bcast, const char* ci, const char* html) {
    ms_packet_t* pkt = init_header(buffer, E_MS_CiHtml, bcast);
    assert_return(pkt, -1);
    
    int pos = 0;
    char data[MAX_BODY_SIZE];
    memset(data, 0, sizeof(data));
    if (ci && strlen(ci) > 0)
        pos += snprintf(data+pos, sizeof(data)-pos, "[ci]:%s\n", ci);
    if (html && strlen(html) > 0)
        pos += snprintf(data+pos, sizeof(data)-pos, "[html]:%s\n", html);
    assert_return(pos > 0, -1);
    
    pkt->size = pos;
    memcpy(pkt->body, data, pkt->size);
    return HEAD_SIZE + pkt->size;
}

```

<br />
### 3).<mark>**多屏交互示例**</mark>

- 副屏发送该请求数据消息:

    ```
    char buffer[1024*16];
    ms_packet_t* pkt = (ms_packet_t*) buffer;
    
    int len = set_packet_ms_request(buffer);
    SendToMainScreen(buffer, len);
    ```

- 发送多屏cihtml数据
    
    ```
    char bcast[] = "224.0.0.10:2500";
    char ci[] = "<area>...</area>";
    char html[] = "<html>...</html>";
    
    int len = set_packet_ms_cihtml(buffer, bcast, ci, html);
    SendToSecondScreen(buffer, len);
    ```



<br />
-
&copy; 2015-03-22
