Media Cast & MMTP Receiver
===========================


<br />
0. chrome mmt协议
-----------------

### 0) 通过本地媒体读取数据

- html/cixml位置
    - /tmp/index.html
    - /tmp/ci.xml
- chrome地址格式
    - mmt://localhost/tmp/index.html
- audio/video/image地址格式
    - cixml中格式: <mark>[sequence_num=1-230&]type=audio/video/image</mark>
        - mmt://localhost/tmp/Channel1?sequence_num=1-230&type=audio
        - mmt://localhost/tmp/Channel1?sequence_num=1-230&type=video
        - mmt://localhost/tmp/test.mp4?type=image
    - Chrome内部格式会额外添加: &htmlid=xx&tabid=xx
- subset xml地址格式
    - cixml中格式: mmt://localhost/tmp/subset1.xml
    - chrome内部将额外添加: type=ci&htmlid=xx&tabid=xx

### 1) 通过mmtp协议读取数据

- chrome地址格式: <mark>proto=mmtp</mark>
    - mmt://localhost/index?proto=mmtp
- audio/video/image格式: <mark>proto=mmtp&type=audio/video/image</mark>
    - mmt://localhost/index?proto=mmtp&type=audio
    - mmt://localhost/index?proto=mmtp&type=video
    - mmt://localhost/index?proto=mmtp&type=image
    - chrome内部格式会额外添加: &htmlid=xx&tabid=xx
- subset cixml by http
    - cixml种格式: <mark>proto=extra</proto>
        - mmt://localhost/subset.xml?proto=extra
    - chrome内部格式会额外添加: <mark>&type=ci&htmlid=xx&tabid=xx</mark>
- html/xml是通过mmtp接收端直接获取得到.


<br />
1. media casting
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
2. MMTP Service接口
-------------------

### 0) 模块划分及功能
- **MMTP数据接收**: 
    - 处理广播地址协议
    - 接收asset id并返回对应的url
    - 接收组播频道媒体数据并通知chrome接收端
- **MMTP多屏Server**: 
    - 与chrome主屏交互, 重新生成副屏所需要的html/xml
    - 接收chrome副屏的媒体共享请求, 并通知chrome主屏
    - 向chrome副屏提供html/cixml资源
- **通过消息在各模块之间进行交互**(以MMTP为中介): 
    - <mark>chrome主屏</mark> <=> MMTP
    - MMTP <=> <mark>chrome副屏</mark>

<br />
### 1) MMTP消息类型及数据包结构

<!--lang:c++-->
```
/**
 * mmtp packet types
 */ 
enum mmtp_type_t {
    E_Mmtp_Unknown      =   0,
    
    
    // For mmtp receiver
    E_Mmtp_Open         =   0x0001,
    E_Mmtp_CiHtml       =   0x0002,
    E_Mmtp_AssetId      =   0x0004,
    E_Mmtp_AssetUrl     =   0x0008,
    E_Mmtp_Media        =   0x0010,
    E_Mmtp_HeartBeat    =   0x0020,
    E_Mmtp_Close        =   0x0040,
    E_Mmtp_Quit         =   0x0080,
    
    // For mmtp multi-screen server
    E_Mmtp_MS_Start     =   0x2001, //> start multi-screen server
    E_Mmtp_MS_Share     =   0x2002, //> Share some asset id
    E_Mmtp_MS_Request   =   0x2004, //> second request sharing from main screen
    
    
    E_Mmtp_All          =   0xffff
};


/** 
 * mmtp packet structure: not include <body>.
 */
#praram pack(1)
typedef struct mmtp_packet_t {
    char        ver;
    int         type;       //> packet type
    char        bcast[64];  //> broadcast address
    int         size;       //> packet body size
    char        body[1];
}mmtp_packet_t;
#praram pack()

#define DEFAULT_VERSION             1
#define HEAD_SIZE                   (sizeof(mmtp_packet_t)-1)
#define MAX_BODY_SIZE               (1024*16-HEAD_SIZE)
#define assert_return(p, v)         if(!(p)) return (v);

/**
 * Init commom header of mmtp packet
 */
mmtp_packet_t* init_header(char* buffer, int type, const char* bcast) {
    mmtp_packet_t* pkt = (mmtp_packet_t*) buffer;
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


<br />
### 2）MMTP媒体数据接收
mmtp数据接收的交互消息, 例如asset id/assert url等, 具体参照代码。

<!--lang:c++-->
```
/** 
 * open broadcast address: 
 *      chrome => mmtp receiver
 * @param bcast: broadcast address
 * @param port:  chromium's listen udp port
 */
int set_packet_open(char* buffer, const char* bcast, int port) {
    mmtp_packet_t* pkt = init_header(buffer, E_Mmtp_Open, bcast);
    assert_return(pkt, -1);
    
    ((unsigned short *)pkt->body)[0] = port;
    pkt->size = 2; // 2 bytes for port
    return HEAD_SIZE + pkt->size;
}

/**
 * set ci xml and html: 
 *      mmtp receiver => chrome
 * @param bcast: broadcast address
 * @param ci: ci xml filename
 * @param html: html filename
 */
int set_packet_cihtml(char* buffer, const char* bcast, const char* ci, const char* html) {
    mmtp_packet_t* pkt = init_header(buffer, E_Mmtp_CiHtml, bcast);
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

/**
 * set asset id: 
 *      chrome => mmtp receiver
 * @param bcast: broadcast address
 * @param ids: asset ids
 * @param num: the number of asset ids
 */
int set_packet_asset_id(char* buffer, const char* bcast, const char* ids[], int num) {
    mmtp_packet_t* pkt = init_header(buffer, E_Mmtp_AssetId, bcast);
    assert_return(pkt, -1);
    
    int pos = 0;
    char data[MAX_BODY_SIZE];
    memset(data, 0, sizeof(data));
    for (int k=0; k < num; k++) {
        pos += snprintf(data+pos, sizeof(data)-pos, "[id]:%s\n", ids[k]);
    }
    assert_return(pos > 0, -1);
    
    pkt->size = pos;
    memcpy(pkt->body, data, pkt->size);
    return HEAD_SIZE + pkt->size;
}

/**
 * set url for corresponding asset id: 
 *      mmtp receiver => chrome
 * @param bcast: broadcast address
 * @param ids: asset ids
 * @param urls: url for asset id
 * @param num: the number of ids or urls array.
 */
int set_packet_url(char* buffer, const char* bcast, const char* ids[], const char* urls[], int num) {
    mmtp_packet_t* pkt = init_header(buffer, E_Mmtp_AssetUrl, bcast);
    assert_return(pkt, -1);
    
    int pos = 0;
    char data[MAX_BODY_SIZE];
    memset(data, 0, sizeof(data));
    for (int k=0; k < num; k++) {
        pos += snprintf(data+pos, sizeof(data)-pos, "[%s]:%s\n", ids[k], urls[k]);
    }
    assert_return(pos > 0, -1);
    
    pkt->size = pos;
    memcpy(pkt->body, data, pkt->size);
    return HEAD_SIZE + pkt->size;
}

/**
 * set media(file name) for asset id: 
 *      mmtp receiver => chrome
 * @param bcast: broadcast address
 * @param ids: asset ids,
 * @param medias: media filenames for the asset ids
 * @param num: the number of ids or medias array.
 */
int set_packet_media(char* buffer, const char* bcast, const char* ids[], const char* medias[], int num) {
    mmtp_packet_t* pkt = init_header(buffer, E_Mmtp_Media, bcast);
    assert_return(pkt, -1);
    
    int pos = 0;
    char data[MAX_BODY_SIZE];
    memset(data, 0, sizeof(data));
    for (int k=0; k < num; k++) {
        pos += snprintf(data+pos, sizeof(data)-pos, "[%s]:%s\n", ids[k], medias[k]);
    }
    assert_return(pos > 0, -1);
    
    pkt->size = pos;
    memcpy(pkt->body, data, pkt->size);
    return HEAD_SIZE + pkt->size;
}

/**
 * HeartBeat between MMTP and chrome,
 *  When recving no heartbeat msg during 1min, MMTP should close this channel. 
 *      chrome => mmtp receiver
 * @param bcast: broadcast address
 */
int set_packet_heartbeat(char* buffer, const char* bcast) {
    mmtp_packet_t* pkt = init_header(buffer, E_Mmtp_HeartBeat, bcast);
    assert_return(pkt, -1);
    return HEAD_SIZE + pkt->size;
}

/**
 * close one broadcast url: 
 *      chrome => mmtp receiver
 * @param bcast: broadcast address
 */
int set_packet_close(char* buffer, const char* bcast) {
    mmtp_packet_t* pkt = init_header(buffer, E_Mmtp_Close, bcast);
    assert_return(pkt, -1);
    return HEAD_SIZE + pkt->size;
}

/**
 * quit mmtp receiver: 
 *      chrome => mmtp receiver
 */
int set_packet_quit(char* buffer) {
    mmtp_packet_t* pkt = init_header(buffer, E_Mmtp_Quit, NULL);
    assert_return(pkt, -1);
    return HEAD_SIZE + pkt->size;
}

```

<br />
<mark>**数据请求示例**</mark>:

- chrome发送打开频道(组播地址和端口号)消息给MMTP

    ```
    char buffer[1024*16];
    mmtp_packet_t* pkt = (mmtp_packet_t*) buffer;
    char bcast[] = "224.0.0.10:2500";
    int chrome_udp_port = 32180;

    int len = set_packet_open(buffer, bcast, chrome_udp_port);
    SendToMMTP(buffer, len);
    ```

- MMTP发送ci/html消息给chrome(<mark>有更新则发送</mark>)

    ```
    const char ci[] = "/tmp/ci_001.xml";
    const char html[] = "/tmp/index_002.html";
    int len = set_packet_cihtml(buffer, bcast, ci, html);
    SendToMMTP(buffer, len);
    ```

- chrome发送asset ids消息给MMTP

    ```
    const char *ids[] = {"asset_id_video1", "asset_id_audio1"};
    int len = set_packet_asset_id(buffer, bcast, ids, 2);
    SendToMMTP(buffer, len);
    ```

- MMTP发送asset ids对应的url消息给chrome

    ```
    const char *ids[] = {"asset_id_video1", "asset_id_audio1"};
    const char *urls[] = {"mmt://url1", "mmt://url2"};
    int len = set_packet_url(buffer, bcast, ids, urls, 2);
    SendToMMTP(buffer, len);
    ```

- MMTP发送asset ids对应的media filename消息给chrome(<mark>有更新则发送</mark>)

    ```
    const char *ids[] = {"asset_id_video1", "asset_id_audio1"};
    const char *medias[] = {"/tmp/file1", "/tmp/file2"};
    int len = set_packet_media(buffer, bcast, ids, medias, 2);
    SendToMMTP(buffer, len);
    ```

- chrome周期性发送HeartBeat消息给MMTP(<mark>1min内至少一次, 否则MMTP应自动关闭该频道</mark>)

    ```
    int len = set_packet_heartbeat(buffer, bcast);
    SendToMMTP(buffer, len);
    ```

- chrome发送关闭频道(组播地址)消息给MMTP

    ```
    int len = set_packet_close(buffer, bcast);
    SendToMMTP(buffer, len);
    ```

- chrome发送退出消息给MMTP

    ```
    int len = set_packet_quit(buffer);
    SendToMMTP(buffer, len);
    ```
    


<br />
### 3) MMTP多屏消息处理
扩展multi-screen协议, 具体参照以下代码实现。

<!--lang:c++-->
```
/**
 * start multi-screen server: 
 *      Main Screen(chrome) => mmtp process
 * @param bcast: broadcast address
 */
int set_packet_ms_start(char* buffer, const char* bcast) {
    mmtp_packet_t* pkt = init_header(buffer, E_Mmtp_MS_Start, bcast);
    assert_return(pkt, -1);
    return HEAD_SIZE + pkt->size;
}

/**
 * start multi-screen server for some asset ids: 
 *      main screen(chrome) => mmtp process
 * @param bcast: broadcast address
 * @param ids: asset ids
 * @param npts: npt(normal play time) for asset id
 * @param num: the number of asset ids
 */
int set_packet_ms_share(char* buffer, const char* bcast, const char* ids[], const char* npts[], int num) {
    mmtp_packet_t* pkt = init_header(buffer, E_Mmtp_MS_Share, bcast);
    assert_return(pkt, -1);
    
    int pos = 0;
    char data[MAX_BODY_SIZE];
    memset(data, 0, sizeof(data));
    for (int k=0; k < num; k++) {
        pos += snprintf(data+pos, sizeof(data)-pos, "[%s]:%s", ids[k], npts[k]);
    }
    assert_return(pos > 0, -1);
    
    pkt->size = pos;
    memcpy(pkt->body, data, pkt->size);
    return HEAD_SIZE + pkt->size;
}

/**
 * Request sharing from main screen: 
 *      Second screen => mmtp process => Main Screen(chrome)
 * @param bcast: broadcast address
 */
int set_packet_ms_request(char* buffer, const char* bcast) {
    mmtp_packet_t* pkt = init_header(buffer, E_Mmtp_MS_Request, bcast);
    assert_return(pkt, -1);
    return HEAD_SIZE + pkt->size;
}


```

<br />
<mark>**多屏交互示例**</mark>:

- 启动主屏server:
    
    - 主屏chrome端: 发送消息到mmtp启动server.
    
    ```
    char buffer[1024*16];
    mmtp_packet_t* pkt = (mmtp_packet_t*) buffer;
    char bcast[] = "224.0.0.10:2500";

    int len = set_packet_ms_start(buffer, bcast);
    SendToMMTP(buffer, len);
    ```

- 共享分发主屏数据:
    
    - 主屏chrome端: 发送消息告诉server将分享的数据: 组播地址, asset ids和播放时间npt.
    - Server端: 将收到的组合成新的html/xml, 以便副屏请求时发送该数据.

    ```
    char* ids[] = {"video1_asset1", "video2_asset2"};
    char* npts[] = {"npt1", "npt2"};
    int len = set_packet_ms_share(buffer, bcast, ids, npts, 2);
    SendToMMTP(buffer, len);
    ```

- 副屏发送该请求数据消息:
    
    - 副屏chrome端: 发送Server这个数据共享消息,
    - Server端: 处理这个消息(并将上面生成的新html/ci发送给副屏),并转发这个消息到主屏chrome,
    - 主屏chrome端: 处理该消息(例如plungeOut的三种状态sharable/dynamic/complementary).

    ```
    int len = set_packet_ms_request(buffer, bcast);
    SendToMMTP(buffer, len);
    ```


<br />
### 4) Receiver Process
    接收端为独立进程，如何实现由其自主决定，通常有两种模式，下面将分别介绍。
    
---
#### 模式1 >>> 多进程模式:   每个组播地址启动一个进程
    不直观，实现难度决定于对操作系统多进程编程技术的掌握。
    
#### a) 主进程
    保持系统中一个主进程实例，
    监听一个已知socket端口，
    接收来自chrome的请求，
    
    消息处理:
        收到E_Mmtp_Open, 则启动一个子进程对其进行处理（组播地址）。
        收到E_Mmtp_Close, 则关闭相应的子进程（对应组播地址）。
        收到E_Mmtp_Quit, 则关闭所有的子进程已经自身。
        收到其它消息，主进程需要与相应地子进程交互处理。
 
#### b) 子进程
    用于实际处理组播地址频道的服务。同时部分信息需要与主进程之间交互(可采取进程消息机制)

---
#### 模式2 >>> 单进程多线程模式:   每个组播地址启动一个线程
    直观，从编程技术上看更容易实现。
    
#### a) 主进程
    保持系统中一个主进程实例，
    主进程循环监听一个已知socket端口，
    接收来自chrome的请求，
    
    消息处理:
        收到E_Mmtp_Open, 则启动一个子线程对其进行处理（组播地址）。
        收到E_Mmtp_Close, 则关闭相应的子线程（对应组播地址）。
        收到E_Mmtp_Quit, 则关闭所有的子线程已经自身。
        收到其它消息，主进程需要与相应地子线程交互处理。
        
#### b)子线程
    用于实际处理组播地址频道的服务。
    


<br />
### 5) 伪代码示例(基于上述模式2) - 部分参考网上代码
```
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/file.h>
#include <unistd.h>

#define CLOSE_FILE(fd) if (fd != -1) {close(fd);fd=-1;}

static int g_lock_fd = -1;

static void lockfile_cleanup(void) {
    CLOSE_FILE(g_lock_fd);
}

/**
 * @return: 0 if exist, else -1.
 */
int is_this_exist(const char *process_name) {
    char lock_file[256];
    snprintf(lock_file, sizeof(lock_file), "/var/tmp/%s.lock", process_name);

    g_lock_fd = open(lock_file, O_CREAT|O_RDWR, 0644);
    if (-1 == g_lock_fd) {
        fprintf(stderr, "Fail to open lock file(%s). Error: %sn", 
            lock_file, strerror(errno));
        return 0;
    }

    if (0 == flock(g_lock_fd, LOCK_EX | LOCK_NB)) {
        atexit(lockfile_cleanup);
        return -1;
    }

    CLOSE_FILE(g_lock_fd);
    return 0;
}

int StartChannel(mmtp_packet_t* pkt) {
    char* broadcast_addr = pkt->bcast;
    int remote_port = ((unsigned short *)pkt->body)[0];
    // TODO
}
int CloseChannel(mmtp_packet_t* pkt) {
    char* broadcast_addr = pkt->bcast;
    // TODO
}
int QueryChannel(mmtp_packet_t* pkt) {
    char* broadcast_addr = pkt->bcast;
    char* asset_ids = pkt->body;
    // TODO
}

int RecvOnePacket(int sock, char* data, int len) {
    mmtp_packet_t* pkt = (mmtp_packet_t*)data;
    // for UDP blocking socket
    int iret = recv(sock, data);
    if (iret < HEAD_SIZE || iret < pkt->size + HEAD_SIZE) {
        // invalid packet head or body
        return -1;
    }
    return iret;
}

int main(int argc, char* argv[]) {
    if (is_this_exist("mmtp_receiver") == 0) {
        exit(0); // The reciever process has been started
    }
    
    int port = 32160; // default port
    int sock = socket(UDP, port);
    
    char data[1024*16];
    mmtp_packet_t* pkt = (mmtp_packet_t*)data;
    do {
        int ret = RecvOnePacket(sock, data, sizeof(data));
        if (ret <= 0) {
            // invalid packet head
            continue;
        }
        
        switch (pkt->type) {
        case E_Mmtp_Open:
            StartChannel(pkt);
            break;
        case E_Mmtp_AssetId:
            if (QueryChannel(pkt) == 0)
                SendToChrome(pkt); // reply with correspoding urls
            break;
        case E_Mmtp_Close:
            CloseChannel(pkt);
            break;
        case E_Mmtp_Quit:
            break;
        }
    }while(1);
    
    exit(0);
}
```

<br />
### 6) TODO简单替代方案

- 1.MMTP接收端添加新接口
    - 设置组播地址(ip:port)
    - 更新组播地址
- 2.chrome添加新模块处理多屏
    - 监听本地UDP端口
    - 接收其它chrome多屏请求(UDP)
    - 发送多屏html/xml给chrome副屏(UDP)
    - 向其它chrome主屏发送chrome多屏请求(mmt://another-chrome-address?proto=ms)




<br /><br />
-
&copy; 2015-03-22
